import os
import instructor
import pymupdf4llm
from diskcache import Cache
from resumer.schemas.sections_schemas import ResumeSchema
from resumer.schemas.job_details_schema import JobDetails
from resumer.prompts.resume_prompt import RESUME_DETAILS_EXTRACTOR, JOB_DETAILS_EXTRACTOR
from resumer.utils.scraper import scrape_job_details
from resumer.utils.latex_ops import json_to_latex_pdf
from resumer.variables import section_mapping
from typing import Callable, Optional

class ResumeTailorPipeline:
    """
        Args:
            aclient: used to make llm calls
            resume_path: path to the original resume (pdf file location)
            output_dir: folder where we can store the final taliored resume

        """
    def __init__(
        self, 
        aclient: instructor.AsyncInstructor, 
        model_name: str, 
        resume_path: str, 
        output_dir: str,
        log_callback: Optional[Callable[[str], None]] = None,
        max_concurrent_sections: int = 3
    ):
        self.aclient = aclient
        self.model_name = model_name
        self.resume_path = resume_path
        self.output_dir = output_dir
        self.log_callback = log_callback
        self.max_concurrent_sections = max_concurrent_sections
        self.resume_md = None
        self.resume_info = None
        self.resume_details = None
        self.tailored_resume_path = None
        self.tailored_resume_tex_path = None    

        # make the output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize Cache in a subfolder of your output_dir
        cache_dir = os.path.join(self.output_dir, ".resume_cache")
        self.cache = Cache(cache_dir)
    
    def _log(self, message: str):
        """Internal logging method that uses callback if available"""
        print(message)
        if self.log_callback:
            self.log_callback(message)

    def _read_resume_pdf(self):
        self._log("📄 Reading resume PDF...")
        if not self.resume_md:
            self._log("🔄 Converting PDF to markdown...")
            self.resume_md = pymupdf4llm.to_markdown(self.resume_path)
            self._log(f"✅ Successfully converted resume ({len(self.resume_md)} characters)")
        return self.resume_md

    async def _extract_resume_json(self):
        self._log("🔍 Starting resume extraction...")
        resume_md = self._read_resume_pdf()

        # Use the resume markdown string as the key
        cached_json = self.cache.get(resume_md)

        if cached_json:
            self._log("⚡ Loading resume info from disk cache...")
            self.resume_info = ResumeSchema.model_validate(cached_json)
            self._log("✅ Resume loaded from cache")
            return self.resume_info
        
        self._log("🤖 Cache miss: Extracting resume via LLM...(this may take a while)")
        self.resume_info = await self.aclient.chat.completions.create(
            model=self.model_name,
            response_model=ResumeSchema,
            messages=[
                {"role": "system", "content": RESUME_DETAILS_EXTRACTOR},
                {"role": "user", "content": resume_md},
            ],
        )
        self._log("✅ Resume structure extracted successfully")
        
        # Store as a Dictionary/JSON instead of a Class Object
        self.cache.set(resume_md, self.resume_info.model_dump())
        return self.resume_info

    async def _extract_job_json(self, url: str = None, job_site_content: str = None):
        """Scrapes and structures job details."""
        if not url and not job_site_content:
            raise ValueError("You must provide either a URL or raw job content.")
        
        if not job_site_content:
            self._log(f"🌐 Scraping job details from: {url}")
            job_site_content = scrape_job_details(url)
            self._log(f"✅ Job page scraped ({len(job_site_content)} characters)")

        self._log("🤖 Extracting job info via LLM...")
        self.job_info = await self.aclient.chat.completions.create(
            model=self.model_name,
            response_model=JobDetails,
            messages=[
                {"role": "system", "content": JOB_DETAILS_EXTRACTOR},
                {"role": "user", "content": job_site_content},
            ],
        )
        self._log("✅ Job structure extracted successfully")

        # Logic check for valid content
        if getattr(self.job_info, "is_noise_only", False):
            self._log("⚠️ Warning: Content identified as noise")
            raise ValueError("LLM identified the content as noise (ads/login walls) rather than a job post.")

        # Return the 'data' field if it exists, otherwise the whole object
        self.job_info = getattr(self.job_info, "data", self.job_info)
        return self.job_info

    def _get_all_sections(self):
        """Get all resume sections"""
        sections = list(self.resume_info.model_dump().keys())

        if "custom_sections" in sections:
            sections.remove("custom_sections")

        custom_sections = []

        if getattr(self.resume_info, "custom_sections"):
            for section in getattr(self.resume_info, "custom_sections"):
                sec_name = section.section_name.plain_text
                custom_sections.append(sec_name)

        return sections, custom_sections
                
            
    async def _process_section(self, section_title: str, section_data: str, mapping_key: str):
        """
        Helper method to tailor a single section using the LLM.
        
        Args:
            section_title: The name of the section (used for XML tags).
            section_data: The content of the section.
            mapping_key: The key to look up prompt and schema in section_mapping.
        """
        self._log(f"📝 Processing section: {section_title}")

        section_system_prompt = section_mapping.get(mapping_key).get("prompt")
        section_schema = section_mapping.get(mapping_key).get("schema")
        
        section_user_prompt = f"""
        <{section_title.upper()}>
        {section_data}
        </{section_title.upper()}>

        <JOB_DESCRIPTION>
        {self.job_info.model_dump_json()}
        </JOB_DESCRIPTION>
        """

        # make a llm call to get the section
        section_info = await self.aclient.chat.completions.create(
            model=self.model_name,
            response_model=section_schema,
            messages=[
                {"role": "system", "content": section_system_prompt},
                {"role": "user", "content": section_user_prompt},
            ],
        )

        section_info = section_info.model_dump()

        # first check if this section is relevant
        if section_info.get("is_relevant", False):
            self._log(f"✅ {section_title}: Tailored and included")
            return section_info.get("data", None)
        else:
            self._log(f"⏭️ {section_title}: Not relevant to job, skipping")
        return None

    # async def resume_builder(self):
    #     """Build the tailored resume from all sections"""
    #     self._log("🏗️ Starting resume builder...")
    #     section_names, custom_section_names = self._get_all_sections()
        
    #     # remove keywords from section_names
    #     if "keywords" in section_names:
    #         section_names.remove("keywords")
        
    #     resume_details = dict()

    #     # add personal info
    #     self._log("👤 Adding personal information...")
    #     resume_details["personal_info"] = getattr(self.resume_info, "personal_info").model_dump()
        
    #     if "personal_info" in section_names:
    #         section_names.remove("personal_info")

    #     # Process other sections
    #     self._log(f"📋 Processing {len(section_names)} standard sections...")
    #     for section_name in section_names:
    #         if getattr(self.resume_info, section_name) is None:
    #             continue

    #         if section_name == "summary":
    #             _section_data = self.resume_info.model_dump_json()
    #         else:
    #             _section_data = self.resume_info.model_dump_json(include={section_name})

    #         result = await self._process_section(section_name, _section_data, section_name)
    #         if result:
    #             resume_details[section_name] = result

    #     # Process custom sections
    #     resume_details["custom_sections"] = {}
    #     if getattr(self.resume_info, "custom_sections") is not None:
    #         self._log(f"📋 Processing {len(custom_section_names)} custom sections...")
    #         for csection in getattr(self.resume_info, "custom_sections"):
    #             section_name = csection.section_name.plain_text
    #             _section_data = str(csection.model_dump()["section_detail"])
    #             result = await self._process_section(section_name, _section_data, "custom_sections")
    #             if result:
    #                 resume_details["custom_sections"][section_name] = result

    #     self.resume_details = resume_details
    #     self._log("✅ Resume building complete")
    #     return self.resume_details

    async def resume_builder(self):
        """Build the tailored resume from all sections with parallel processing"""
        import asyncio
        
        self._log("🏗️ Starting resume builder...")
        section_names, custom_section_names = self._get_all_sections()
        
        # remove keywords from section_names
        if "keywords" in section_names:
            section_names.remove("keywords")
        
        resume_details = dict()

        # add personal info
        self._log("👤 Adding personal information...")
        resume_details["personal_info"] = getattr(self.resume_info, "personal_info").model_dump()
        
        if "personal_info" in section_names:
            section_names.remove("personal_info")

        # Create a semaphore to limit concurrent LLM calls
        semaphore = asyncio.Semaphore(self.max_concurrent_sections)
        
        async def process_section_with_semaphore(section_name, section_data, mapping_key):
            """Wrapper to limit concurrent calls"""
            async with semaphore:
                return await self._process_section(section_name, section_data, mapping_key)
        
        # Process standard sections in parallel
        self._log(f"📋 Processing {len(section_names)} standard sections (max {self.max_concurrent_sections} concurrent)...")
        
        # Create tasks for all sections
        tasks = []
        for section_name in section_names:
            if getattr(self.resume_info, section_name) is None:
                continue

            if section_name == "summary":
                _section_data = self.resume_info.model_dump_json()
            else:
                _section_data = self.resume_info.model_dump_json(include={section_name})

            # Create a task for this section
            task = process_section_with_semaphore(section_name, _section_data, section_name)
            tasks.append((section_name, task))
        
        # Run all standard section tasks concurrently
        if tasks:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            for (section_name, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    self._log(f"❌ Error processing {section_name}: {str(result)}")
                elif result:
                    resume_details[section_name] = result
        
        # Process custom sections in parallel
        resume_details["custom_sections"] = {}
        if getattr(self.resume_info, "custom_sections") is not None:
            self._log(f"📋 Processing {len(custom_section_names)} custom sections (max {self.max_concurrent_sections} concurrent)...")
            
            custom_tasks = []
            for csection in getattr(self.resume_info, "custom_sections"):
                section_name = csection.section_name.plain_text
                _section_data = str(csection.model_dump()["section_detail"])
                
                # Create a task for this custom section
                task = process_section_with_semaphore(section_name, _section_data, "custom_sections")
                custom_tasks.append((section_name, task))
            
            # Run all custom section tasks concurrently
            if custom_tasks:
                custom_results = await asyncio.gather(*[task for _, task in custom_tasks], return_exceptions=True)
                for (section_name, _), result in zip(custom_tasks, custom_results):
                    if isinstance(result, Exception):
                        self._log(f"❌ Error processing {section_name}: {str(result)}")
                    elif result:
                        resume_details["custom_sections"][section_name] = result

        self.resume_details = resume_details
        self._log("✅ Resume building complete")
        return self.resume_details


    async def generate_tailored_resume(self, job_url: str = None, job_site_content: str = None):
        """Generate the tailored resume"""
        self._log("=" * 50)
        self._log("🚀 Starting Resume Tailoring Pipeline")
        self._log("=" * 50)
        
        try:
            # Step 1: Extract job details
            self._log("\n📌 STEP 1: Extract Job Details")
            await self._extract_job_json(job_url, job_site_content)

            # Step 2: Extract resume details
            self._log("\n📌 STEP 2: Extract Resume Details")
            await self._extract_resume_json()

            self._log("\n✅ Successfully extracted both Resume and Job data")
            
            # Step 3: Build tailored resume
            self._log("\n📌 STEP 3: Build Tailored Resume")
            await self.resume_builder()

            # Step 4: Generate PDF
            self._log("\n📌 STEP 4: Generate PDF")
            self._log("🔄 Converting to LaTeX and generating PDF...")
            self.tailored_resume_path, self.tailored_resume_tex_path = json_to_latex_pdf(
                self.resume_details, 
                os.path.join(self.output_dir, "tailored_resume.pdf")
            )
            self._log(f"✅ PDF generated at: {self.tailored_resume_path}")

            self._log("\n" + "=" * 50)
            self._log("🎉 Resume Tailoring Complete!")
            self._log("=" * 50)

            return self.tailored_resume_path, self.tailored_resume_tex_path
            
        except Exception as e:
            self._log(f"\n❌ Error during pipeline execution: {str(e)}")
            raise

    def close_cache(self):
        """Cleanly close the cache connection."""
        self.cache.close()

    



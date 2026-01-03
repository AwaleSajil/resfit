RESUME_DETAILS_EXTRACTOR = """<objective>
Parse a resume into a structured JSON format following a specific RichText schema that preserves hyperlinks and their associated anchor text.
</objective>

<instructions>
Follow these steps to extract and structure the resume information:

1. Analyze Structure:
   - Examine the text-formatted resume to identify key sections (e.g., personal information, education, experience, skills, certifications).
   - Note any unique formatting or organization within the resume.

2. Extract Information:
   - Systematically parse each section, extracting relevant details.
   - Pay attention to dates, titles, organizations, and descriptions.

3. Handle Variations:
   - Account for different resume styles, formats, and section orders.
   - Adapt the extraction process to accurately capture data from various layouts.

5. Optimize Output:
   - Handle missing or incomplete information appropriately (use null values or empty arrays/objects as needed).
   - Standardize date formats, if applicable.

6. Validate:
   - Review the extracted data for consistency and completeness.
   - Ensure all required fields are populated if the information is available in the resume.
</instructions>
"""

JOB_DETAILS_EXTRACTOR = """
<task>
Analyze the provided text and determine if it contains a legitimate job description or if it is "noise" (e.g., bot protection screens, login walls, "Access Denied" messages, or cookie consent pages). 

You must output a structured JSON response following these rules:

1. **Noise Detection**: First, evaluate if the text is noise. Set `is_noise_only` to `true` if the text is a system error, a login prompt, or lacks any actual job-related information.
2. **Conditional Extraction**: 
   - If `is_noise_only` is `true`, set the `data` field to `null`.
   - If `is_noise_only` is `false`, extract the job details into the `data` object.
3. **Handling Missing Info**: Only populate specific fields within the `data` object if the information is explicitly stated or clearly implied. If a specific detail (like 'preferred_qualifications') is missing from the text, set that field to `null` or an empty list as appropriate. Do not hallucinate details.
4. **Focus**: Prioritize "keywords", "job_duties_and_responsibilities", and "required_qualifications" for resume tailoring. Ensure these are concise and accurate.
</task>
"""
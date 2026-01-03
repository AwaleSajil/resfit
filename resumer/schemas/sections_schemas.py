from typing import List, Optional, Union, Literal, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict

# --- Core Building Blocks ---

class TextSegment(BaseModel):
    # Removed Literal default to satisfy Gemini's strict schema rules
    type: str = Field(description="Must be 'text'")
    content: str

class LinkSegment(BaseModel):
    # Removed Literal default
    type: str = Field(description="Must be 'link'")
    content: str = Field(description="The display text that is clickable.")
    url: str = Field(description="The destination URL.")

class RichText(BaseModel):
    # Gemini handles Union better when the objects are distinct 
    # but the Literal constants are removed.
    segments: List[Union[TextSegment, LinkSegment]] = Field(
        description="An ordered list of segments. Use 'text' for plain strings and 'link' for URLs."
    )

    @property
    def plain_text(self) -> str:
        return "".join(s.content for s in self.segments)

# --- Reusable Components ---

class DatePeriod(BaseModel):
    """Consolidated date handling to remove redundancy across models"""
    date_description: RichText = Field(
        description="The timeframe. Use a single date 'Oct 2023' or a range 'Aug 2023 - Present'."
    )

# --- Resume Sections ---

class Certification(BaseModel):
    certificate_info: RichText = Field(description="Certificate name, issuer and/or other inforamtion.")
    date: Optional[RichText] = Field(description="The date of issuance or expiration.")

class Education(BaseModel):
    degree: RichText = Field(description="The degree and major. e.g., 'B.S. in Computer Science'.")
    university: RichText = Field(description="Institution name e.g. 'Arizona State University'.")
    location: Optional[RichText] = Field(description="Location wherer the institution is")
    date_description: RichText = Field(description="The period of study. e.g., 'Aug 2021 - May 2025'.")
    grade: Optional[RichText] = Field(description="GPA, honors, scholarships, or class standing. e.g., '3.9/4.0 GPA', 'Dean's List', 'Scholarship Recipient'")
    courses: Optional[List[RichText]] = Field(description="Relevant coursework. e.g. ['Operating Systems', 'Calculus'].")

class Project(BaseModel):
    name: RichText = Field(description="The name or title of the project.")
    type: Optional[RichText] = Field(description="Category, e.g., 'Open Source', 'Class Project', or 'Hackathon'.")
    link: Optional[LinkSegment] = Field(description="The primary project URL (GitHub, Demo, etc.).")
    resources: Optional[List[LinkSegment]] = Field(description="Supplementary links like slides, docs, or video demos.")
    date_description: RichText = Field(description="Timeframe of the project. Specific date point (e.g., 'Oct 2023' or '2021') or duration (e.g., 'Aug 2023 - Nov 2023' or 'Aug 2023 - Present')")
    description: List[RichText] = Field(
        description="bullet points using STAR/XYZ format: 'Did X by doing Y, achieved Z'."
    )

class SkillSection(BaseModel):
    name: RichText = Field(description="Category name of the skill group. e.g., 'Languages' or 'Cloud Infrastructure'.")
    skills: List[RichText] = Field(description="Specific skills or competencies within the skill group. e.g., ['Python', 'Docker', 'AWS'].")

class Experience(BaseModel):
    role: RichText = Field(description="Job title or position held. e.g., 'Senior Frontend Developer'.")
    company: RichText = Field(description="Name of the employer.")
    location: RichText = Field(description="The location of the company or organization. e.g. San Francisco, USA.")
    date_description: RichText = Field(description="Employment duration. e.g., 'Jan 2020 - Present'.")
    description: List[RichText] = Field(description="High-impact bullet points quantifying your professional achievements.")


class Media(BaseModel):
    portfolio: Optional[str] = Field(description="Personal profile website URL")
    linkedin: Optional[str] = Field(description="LinkedIn profile URL")
    github: Optional[str] = Field(description="GitHub profile URL")
    medium: Optional[str] = Field(description="Medium profile URL")
    devpost: Optional[str] = Field(description="Devpost profile URL")

    
class Achievement(BaseModel):
    name: RichText = Field(description="Title of the award or recognition.")
    issued_by: RichText = Field(description="The awarding body.")
    date: RichText = Field(description="Date of receipt.")
    description: List[RichText] = Field(description="Details of the award's significance or selectivity.")

class ResearchWork(BaseModel):
    title: RichText = Field(description="Research role or project title.")
    publication: Optional[RichText] = Field(description="Venue of publication (Journal/Conference).")
    date_description: RichText = Field(description="Duration of research or publication date.")
    link: Optional[LinkSegment] = Field(description="Link to paper (DOI) or lab project page.")
    description: List[RichText] = Field(description="Bullet points describing methodology and findings.")


class GenericElement(BaseModel):
    title: RichText = Field(description="The primary heading for the entry (e.g., 'Volunteer Lead') or the main text content")
    subtitle: Optional[RichText] = Field(description="The organization, location, or secondary context associated with the title.")
    date_description: Optional[RichText] = Field(description="The timeframe for the activity (single date or range).")
    description: Optional[List[RichText]] = Field(description="A list of bullet points detailing responsibilities, impact, and key accomplishments using the STAR methodology.")

class GenericSection(BaseModel):
    section_name: RichText = Field(description="Title for the section")
    section_detail: List[GenericElement] = Field(description="The specific entries belonging to this section.")

# --- Master Schema ---

T = TypeVar("T")

class SectionBase(BaseModel, Generic[T]):
    is_relevant: bool = Field(description="Is this section relevant to the job description?")
    data: Optional[T] = Field(description="The content of the section if relevant.", default=None)

class PersonalData(BaseModel):
    name: RichText = Field(description="Full legal name.")
    location: RichText = Field(description="Location of the candidate")
    phone: RichText = Field(description="Contact phone number.")
    email: RichText = Field(description="Professional email address.")
    media: Media = Field(description="Professional social and web presence.")

class Summary(SectionBase[RichText]):
    data: Optional[RichText] = Field(description="A brief summary or objective statement highlighting key skills, experience, and career goals.", alias="summary")

class Experiences(SectionBase[List[Experience]]):
    data: Optional[List[Experience]] = Field(default_factory=list, description="Professional work history.", alias="work_experience")

class Projects(SectionBase[List[Project]]):
    data: Optional[List[Project]] = Field(default_factory=list, description="Technical or academic projects.", alias="projects")

class SkillSections(SectionBase[List[SkillSection]]):
    data: Optional[List[SkillSection]] = Field(default_factory=list, description="Categorized technical and soft skills.", alias="skill_sections")

class Educations(SectionBase[List[Education]]):
    data: Optional[List[Education]] = Field(default_factory=list, description="Academic background.", alias="education")

class Certifications(SectionBase[List[Certification]]):
    data: Optional[List[Certification]] = Field(default_factory=list, description="Earned certifications and licenses.", alias="certifications")

class Achievements(SectionBase[List[Achievement]]):
    data: Optional[List[Achievement]] = Field(default_factory=list, description="Awards and recognitions.", alias="achievements")

class ResearchWorks(SectionBase[List[ResearchWork]]):
    data: Optional[List[ResearchWork]] = Field(default_factory=list, description="Scientific or academic research contributions.", alias="research_works")

class CustomSections(SectionBase[List[GenericElement]]):
    data: Optional[List[GenericElement]] = Field(default_factory=list, description="An additional section like Volunteer work or Interests.", alias="custom_sections")

class ResumeSchema(BaseModel):
    personal_info: PersonalData = Field(description="Primary candidate information.")
    summary: Optional[RichText] = Field(description="A brief summary or objective statement highlighting key skills, experience, and career goals.")
    work_experience: List[Experience] = Field(default_factory=list, description="Professional work history.")
    education: List[Education] = Field(default_factory=list, description="Academic background.")
    skill_sections: List[SkillSection] = Field(default_factory=list, description="Categorized technical and soft skills.")
    projects: List[Project] = Field(default_factory=list, description="Technical or academic projects.")
    certifications: Optional[List[Certification]] = Field(default_factory=list, description="Earned certifications and licenses.")
    achievements: Optional[List[Achievement]] = Field(default_factory=list, description="Awards and recognitions.")
    research_works: Optional[List[ResearchWork]] = Field(default_factory=list, description="Scientific or academic research contributions.")
    custom_sections: Optional[List[GenericSection]] = Field(default_factory=list, description="Additional sections like Volunteer work or Interests or Reference.")
    keywords: List[str] = Field(
        default_factory=list, description="Strategic industry terms and technical concepts for ATS optimization. Includes methodologies (Agile, SDLC), domains (NLP, Cloud), and core competencies not explicitly listed as skills."
    )
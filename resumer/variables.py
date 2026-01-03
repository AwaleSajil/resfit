from resumer.prompts.sections_prompt import SUMMARY, EXPERIENCE, SKILLS, PROJECTS, EDUCATIONS, CERTIFICATIONS, ACHIEVEMENTS, RESEARCH_WORK, CUSTOM_SECTIONS
from resumer.schemas.sections_schemas import Summary, Experiences, Projects, SkillSections, Educations, Certifications, Achievements, ResearchWorks, CustomSections


section_mapping = {
    "summary": {"prompt":SUMMARY, "schema": Summary},
    "work_experience": {"prompt":EXPERIENCE, "schema": Experiences},
    "projects": {"prompt":PROJECTS, "schema": Projects},
    "skill_sections": {"prompt":SKILLS, "schema": SkillSections},
    "education": {"prompt":EDUCATIONS, "schema": Educations},
    "certifications": {"prompt":CERTIFICATIONS, "schema": Certifications},
    "achievements": {"prompt":ACHIEVEMENTS, "schema": Achievements},
    "research_works": {"prompt":RESEARCH_WORK, "schema": ResearchWorks},
    "custom_sections": {"prompt":CUSTOM_SECTIONS, "schema": CustomSections},
}
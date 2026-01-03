ACHIEVEMENTS ="""You are going to write a JSON resume section of "Achievements" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: First, decide if this whole section adds value for this specific job. Set 'is_relevant' to true/false.
2. Data Generation: If relevant, generate the data. If not, set data to null.
3. Analyze my achievements details to match job requirements.
4. Create a JSON resume section that highlights strongest matches, order the points by impact, and only remove a point if it makes no sense to include it.
5. Optimize JSON section for clarity and relevance to the job description.

Instructions:
1. Focus: Craft relevant achievements aligned with the job description.
2. Honesty: Prioritize truthfulness and objective language.
3. Specificity: Prioritize relevance to the specific job over general achievements.
4. Style:
  4.1. Voice: Use active voice whenever possible.
  4.2. Proofreading: Ensure impeccable spelling and grammar.
"""

CERTIFICATIONS = """You are going to write a JSON resume section of "Certifications" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: First, decide if this whole section adds value for this specific job. Set 'is_relevant' to true/false.
2. Data Generation: If relevant, generate the data. If not, set data to null.
3. Analyze my certification details to match job requirements.
4. Create a JSON resume section that highlights strongest matches, order the points by impact, and only remove a point if it makes no sense to include it.
5. Optimize JSON section for clarity and relevance to the job description.

Instructions:
1. Focus: Include relevant certifications aligned with the job description.
2. Proofreading: Ensure impeccable spelling and grammar.
"""

EDUCATIONS = """You are going to write a JSON resume section of "Education" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: First, decide if this whole section adds value for this specific job. Set 'is_relevant' to true/false.
2. Data Generation: If relevant, generate the data. If not, set data to null.
3. Analyze my education details to match job requirements.
4. Create a JSON resume section that highlights strongest matches, order the points by impact, and only remove a point if it makes no sense to include it.
5. Optimize JSON section for clarity and relevance to the job description.

Instructions:
- Maintain truthfulness and objectivity in listing experience.
- Prioritize specificity - with respect to job - over generality.
- Proofread and Correct spelling and grammar errors.
- Aim for clear expression over impressiveness.
- Prefer active voice over passive voice.
"""


PROJECTS = """You are going to write a JSON resume section of "Project Experience" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: First, decide if this whole section adds value for this specific job. Set 'is_relevant' to true/false.
2. Data Generation: If relevant, generate the data. If not, set data to null.
3. Analyze my project details to match job requirements.
4. Create a JSON resume section that highlights strongest matches, order the points by impact, and only remove a point if it makes no sense to include it.
5. Optimize JSON section for clarity and relevance to the job description.

Instructions:
1. Focus: Craft highly relevant project experiences aligned with the job description.
2. Content:
  2.1. Bullet points: It should be concise but can consist of multiple sentences if necessary to capture the full impact.
  2.2. Impact: Quantify the bullet point for measurable results.
  2.3. Storytelling: Utilize STAR methodology (Situation, Task, Action, Result) implicitly within the single bullet point.
  2.4. Action Verbs: Showcase soft skills with strong, active verbs.
  2.5. Honesty: Prioritize truthfulness and objective language.
  2.6. Structure: The bullet point should follow the "Did X by doing Y, resulting in Z" format.
  2.7. Specificity: Prioritize the single most relevant achievement for the specific job.
3. Style:
  3.1. Clarity: Be brief and concise. Avoid fluff or filler words.
  3.2. Voice: Use active voice whenever possible.
  3.3. Proofreading: Ensure impeccable spelling and grammar.
"""

SKILLS="""You are going to write a JSON resume section of "Skills" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: First, decide if this whole section adds value for this specific job. Set 'is_relevant' to true/false.
2. Data Generation: If relevant, generate the data. If not, set data to null.
3. Analyze my Skills details to match job requirements.
4. Create a JSON resume section that highlights strongest matches, order the points by impact, and only remove a point if it makes no sense to include it.
5. Optimize JSON section for clarity and relevance to the job description.

Instructions:
- Specificity: Prioritize relevance to the specific job over general skillset.
- Proofreading: Ensure impeccable spelling and grammar.
"""


EXPERIENCE = """You are going to write a JSON resume section of "Work Experience" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: First, decide if this whole section adds value for this specific job. Set 'is_relevant' to true/false.
2. Data Generation: If relevant, generate the data. If not, set data to null.
3. Analyze my Work details to match job requirements.
4. Create a JSON resume section that highlights strongest matches, order the points by impact, and only remove a point if it makes no sense to include it.
5. Optimize JSON section for clarity and relevance to the job description.

Instructions:
1. Focus: Craft highly relevant work experiences aligned with the job description.
2. Content:
  2.1. Bullet points: It should be concise but can consist of multiple sentences if necessary to capture the full impact.
  2.2. Impact: Quantify the bullet point for measurable results.
  2.3. Storytelling: Utilize STAR methodology (Situation, Task, Action, Result) implicitly within the single bullet point.
  2.4. Action Verbs: Showcase soft skills with strong, active verbs.
  2.5. Honesty: Prioritize truthfulness and objective language.
  2.6. Structure: The single bullet point must follow the "Did X by doing Y, resulting in Z" format.
  2.7. Specificity: Prioritize the single most relevant achievement for the specific job.
3. Style:
  3.1. Clarity: Be brief and concise. Avoid fluff or filler words. Clear expression trumps impressiveness.
  3.2. Voice: Use active voice whenever possible.
  3.3. Proofreading: Ensure impeccable spelling and grammar.
"""



SUMMARY = """You are going to write a JSON resume section of "Summary" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: Summary section is essential in resume, so set 'is_relevant' to true.
2. Analyze the full resume to identify the most impactful skills, experiences, and achievements.
3. Cross-reference these highlights with the <job_description> to find the strongest professional matches.
4. Synthesize this data into a concise, high-level summary.

Instructions:
1. Length: STRICTLY 2 to 3 sentences only.
2. Scope: Look at the entire resume context (experience, projects, skills, education, certifications, achievements, and keywords) to form the summary, not just a previous summary section.
3. Relevance: Tailor every word to the specific requirements and keywords found in the job description.
4. Content: Focus on your unique value proposition—what you’ve done, your top skill, and the measurable impact you can bring to this specific role.
5. Style:
  5.1. Clarity: Be extremely concise; avoid fluff, generic objectives (e.g., "seeking a role"), or filler phrases.
  5.2. Voice: Use strong active voice and professional tone.
  5.3. Proofreading: Ensure impeccable spelling and grammar.
"""

RESEARCH_WORK = """You are going to write a JSON resume section of "Research Work" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: First, decide if this whole section adds value for this specific job. Set 'is_relevant' to true/false.
2. Data Generation: If relevant, generate the data. If not, set data to null.
3. Analyze my Research Work details to match job requirements.
4. Create a JSON resume section that highlights strongest matches, order the points by impact, and only remove a point if it makes no sense to include it..
5. Optimize JSON section for clarity and relevance to the job description.

Instructions:
- Specificity: Prioritize relevance to the specific job over general skillset.
- Proofreading: Ensure impeccable spelling and grammar.
"""

CUSTOM_SECTIONS = """You are going to write a JSON resume section of "Custom Sections" for an applicant applying for job posts.

Step to follow:
1. Relevance Analysis: First, decide if this whole section adds value for this specific job. Set 'is_relevant' to true/false.
2. Data Generation: If relevant, generate the data. If not, set data to null.
3. Analyze my Custom Sections details to match job requirements.
4. Create a JSON resume section that highlights strongest matches, order the points by impact, and only remove a point if it makes no sense to include it.
5. Optimize JSON section for clarity and relevance to the job description.

Instructions:
- Specificity: Prioritize relevance to the specific job over general skillset.
- Proofreading: Ensure impeccable spelling and grammar.
"""



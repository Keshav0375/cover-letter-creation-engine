import boto3
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any
from datetime import datetime

# Load environment variables
load_dotenv()


# Initialize AWS Bedrock client
def get_bedrock_client():
    """
    Initialize and return AWS Bedrock client.

    Returns:
        boto3 client for Bedrock Runtime

    Raises:
        Exception: If AWS credentials are not configured
    """
    try:
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

        if not aws_access_key or not aws_secret_key:
            raise Exception(
                "AWS credentials not found in .env file. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")

        bedrock = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name="us-east-1"
        )

        return bedrock
    except Exception as e:
        raise Exception(f"Failed to initialize AWS Bedrock client: {str(e)}")


def create_cover_letter_prompt(resume: Dict[str, Any], job_description: str) -> str:
    """
    Create an optimized prompt for cover letter generation.

    Args:
        resume: Resume data dictionary
        job_description: Job description text

    Returns:
        Formatted prompt string
    """
    # Format resume data
    resume_text = format_resume_data(resume)

    # Today's date
    today_date = datetime.today().strftime("%B %d, %Y")

    # Extract candidate info
    candidate_name = resume.get('name', 'Candidate Name')
    contacts = resume.get('contacts', {})

    prompt = f"""You are an expert cover letter writer specializing in creating compelling, personalized cover letters for Gen Z professionals. Your task is to create a professional yet modern cover letter that authentically showcases the candidate's fit for the position.

**TODAY'S DATE: {today_date}**

**CANDIDATE'S RESUME:**
{resume_text}

**JOB DESCRIPTION:**
{job_description}

**STRICT FORMAT REQUIREMENTS:**

The cover letter MUST follow this exact structure:

1. **Header (My Information):**
   {candidate_name}
   {contacts.get('email', '[Email]')}
   {contacts.get('phone', '[Phone]')}
   {contacts.get('location', '[Location]')}
   {contacts.get('linkedin', '[LinkedIn]')}

2. **Date:**
   {today_date}

3. **Employer Information:**
   Hiring Manager's Name (or "Hiring Manager" if not specified in JD)
   Company Name (extract from job description)
   Company Address (if available in JD, otherwise use "City, Province")

4. **Subject/Title:**
   Subject: Application for [Exact Job Title from JD]

5. **Greeting:**
   Dear Hiring Manager, (or use specific name if mentioned in JD)

6. **Opening Paragraph – Hook & Purpose (60-80 words):**
   - Strong, engaging hook that shows enthusiasm
   - Mention the specific position you're applying for
   - Brief statement of why you're an excellent fit
   - Use conversational yet professional tone

7. **Middle Paragraph(s) – Experience & Skills (2-3 paragraphs, 100-120 words each):**
   - **Paragraph 1:** Highlight 2-3 most relevant experiences that directly align with job requirements
   - **Paragraph 2:** Showcase technical skills and projects with specific examples and metrics
   - **Paragraph 3 (if needed):** Demonstrate cultural fit, soft skills, and enthusiasm for the company/role
   - Use specific metrics, achievements, and concrete examples
   - Draw clear connections between resume and job requirements
   - Avoid generic statements; be specific and authentic

8. **Closing Paragraph – Alignment & Call to Action (50-70 words):**
   - Express strong interest in the opportunity
   - State why you're a great fit (brief summary)
   - Include call to action (request for interview/discussion)
   - Thank them for their consideration

9. **Sign-off:**
   Sincerely,
   {candidate_name}

**STYLE GUIDELINES:**
- Professional but conversational Gen Z tone (avoid overly formal or stiff language)
- Use active voice and strong action verbs
- Be confident without being arrogant
- Show genuine enthusiasm and personality
- No buzzwords or corporate jargon
- Use "I" statements to show ownership of achievements
- Keep it authentic and human
- Extract company name and job title accurately from the job description

**CONTENT GUIDELINES:**
- Match skills and experiences from resume to job requirements
- Use specific numbers, metrics, and achievements
- Show you've researched the company (if info available in JD)
- Demonstrate how you can add value
- Be memorable and compelling

**TOTAL LENGTH:** 350-450 words maximum (excluding header and employer info)

**CRITICAL:** Follow the format structure EXACTLY as specified above. Each section should be clearly separated with proper spacing.

Generate a cover letter that would make a hiring manager excited to interview this candidate. Make it memorable, specific, and compelling while maintaining professionalism."""

    return prompt


def format_resume_data(resume: Dict[str, Any]) -> str:
    """
    Format resume data for the prompt.

    Args:
        resume: Resume dictionary

    Returns:
        Formatted string
    """
    sections = []

    # Name and Contact
    if 'name' in resume:
        sections.append(f"**Name:** {resume['name']}")

    contacts = resume.get('contacts', {})
    contact_info = []
    for key, value in contacts.items():
        contact_info.append(f"{key.title()}: {value}")
    if contact_info:
        sections.append(f"**Contact:** {' | '.join(contact_info)}")

    # Summary if available
    if 'summary' in resume:
        sections.append(f"**Summary:** {resume['summary']}")

    # Experience
    sections.append("\n**EXPERIENCE:**")
    for i, exp in enumerate(resume.get('experience', []), 1):
        if isinstance(exp, dict):
            title = exp.get('title', 'N/A')
            company = exp.get('company', 'N/A')
            duration = exp.get('duration', 'N/A')
            sections.append(f"{i}. {title} at {company} ({duration})")

            if 'responsibilities' in exp:
                resp_list = exp['responsibilities'] if isinstance(exp['responsibilities'], list) else [
                    exp['responsibilities']]
                for resp in resp_list[:4]:  # Limit to top 4
                    sections.append(f"   - {resp}")
        else:
            sections.append(f"{i}. {exp}")

    # Skills
    skills = resume.get('skills', [])
    if isinstance(skills, list):
        sections.append(f"\n**SKILLS:** {', '.join(str(s) for s in skills)}")
    else:
        sections.append(f"\n**SKILLS:** {skills}")

    # Projects
    sections.append("\n**PROJECTS:**")
    for i, proj in enumerate(resume.get('project', []), 1):
        if isinstance(proj, dict):
            name = proj.get('name', 'Untitled Project')
            desc = proj.get('description', '')
            tech = proj.get('technologies', [])
            sections.append(f"{i}. {name}")
            if desc:
                sections.append(f"   Description: {desc}")
            if tech:
                tech_str = ', '.join(tech) if isinstance(tech, list) else tech
                sections.append(f"   Technologies: {tech_str}")
        else:
            sections.append(f"{i}. {proj}")

    # Education
    if 'education' in resume:
        sections.append("\n**EDUCATION:**")
        edu_list = resume['education'] if isinstance(resume['education'], list) else [resume['education']]
        for edu in edu_list:
            if isinstance(edu, dict):
                degree = edu.get('degree', 'N/A')
                institution = edu.get('institution', 'N/A')
                duration = edu.get('duration', '')
                sections.append(f"- {degree} from {institution}" + (f" ({duration})" if duration else ""))
            else:
                sections.append(f"- {edu}")

    # Achievements
    if 'achievements' in resume:
        sections.append("\n**ACHIEVEMENTS:**")
        ach_list = resume['achievements'] if isinstance(resume['achievements'], list) else [resume['achievements']]
        for ach in ach_list:
            sections.append(f"- {ach}")

    # Certifications
    if 'certifications' in resume and resume['certifications']:
        sections.append("\n**CERTIFICATIONS:**")
        cert_list = resume['certifications'] if isinstance(resume['certifications'], list) else [
            resume['certifications']]
        for cert in cert_list:
            sections.append(f"- {cert}")

    return "\n".join(sections)


def create_example_response(candidate_name: str) -> dict:
    """
    Create an example response structure for the AI to follow.

    Returns:
        Example response dictionary
    """
    return {
        "cover_letter": f"""Keshav Arri
arri@uwindsor.ca
647-227-1538
Windsor, Ontario
https://www.linkedin.com/in/keshav-kumar-arri/

October 15, 2025

Hiring Manager
[Company Name]
[City, Province]

Subject: Application for [Job Title]

Dear Hiring Manager,

[Opening paragraph with enthusiasm and specific position mention - 60-80 words]

[Body paragraph 1 highlighting relevant experience with specific examples and metrics - 100-120 words]

[Body paragraph 2 showcasing technical skills and projects with achievements - 100-120 words]

[Body paragraph 3 demonstrating cultural fit and alignment with company values - 100-120 words]

[Closing paragraph expressing interest and call to action - 50-70 words]

Sincerely,
{candidate_name}"""
    }


def generate_cover_letter_with_ai(resume, job_description: str) -> str:
    """
    Generate cover letter using AWS Bedrock Claude Sonnet 3.5.

    Args:
        resume: Resume data dictionary
        job_description: Job description text

    Returns:
        Generated cover letter text

    Raises:
        Exception: If API call fails
    """
    try:
        # Get Bedrock client
        bedrock = get_bedrock_client()

        # Create prompt
        prompt_content = create_cover_letter_prompt(resume, job_description)

        # Get candidate name for example
        candidate_name = resume.get('name', 'Candidate Name')

        # Assistant prompt to guide response format
        user_content = "You are an expert in creating professional and creative cover letters using Job description and Resume. Follow the exact format structure provided."

        # Example response structure
        example_response = create_example_response(candidate_name)

        # Model configuration
        model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
        accept = "application/json"
        contentType = "application/json"

        # Invoke model with your specified format
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": user_content
                    },
                    {
                        "role": "assistant",
                        "content": prompt_content
                    },
                    {
                        "role": "user",
                        "content": f"Example response format (follow this structure EXACTLY):\n{json.dumps(example_response, indent=4)}\n\nNow generate the actual cover letter based on the resume and job description provided. IMPORTANT: Follow the exact format structure with all sections in order."
                    }
                ],
            }),
            accept=accept,
            contentType=contentType
        )

        # Parse response
        result = json.loads(response.get('body').read())
        content = result['content'][0]['text']

        # Try to parse as JSON first, if that fails, use as plain text
        # Try to parse as JSON first, if that fails, use as plain text
        try:
            j_ = json.loads(content)
            cover_letter = j_.get('cover_letter', content)
        except json.JSONDecodeError:
            # If not JSON, use the content directly
            cover_letter = content

        # Clean up any remaining JSON artifacts
        if cover_letter.strip().startswith('{'):
            # Try to extract cover letter from malformed JSON
            try:
                # Look for "cover_letter": pattern
                if '"cover_letter":' in cover_letter:
                    start = cover_letter.find('"cover_letter":') + len('"cover_letter":')
                    # Find the actual content after the key
                    temp = cover_letter[start:].strip()
                    if temp.startswith('"'):
                        temp = temp[1:]  # Remove opening quote
                        # Find closing quote (accounting for escaped quotes)
                        end = temp.rfind('"')
                        if end > 0:
                            cover_letter = temp[:end]
            except:
                pass

        # Remove any leading/trailing JSON characters
        cover_letter = cover_letter.strip().strip('{').strip('}').strip('"').strip()

        # Clean up the cover letter
        cover_letter = cover_letter.strip()

        # Validate minimum length
        if len(cover_letter) < 100:
            raise Exception("Generated cover letter is too short")

        return cover_letter

    except Exception as e:
        # Check for specific AWS errors
        error_msg = str(e)
        if "ValidationException" in error_msg:
            raise Exception(f"Validation error: {error_msg}")
        elif "ThrottlingException" in error_msg:
            raise Exception(f"Rate limit exceeded. Please try again in a moment: {error_msg}")
        elif "ModelTimeoutException" in error_msg:
            raise Exception(f"Model timeout. Please try again: {error_msg}")
        elif "ServiceQuotaExceededException" in error_msg:
            raise Exception(f"Service quota exceeded: {error_msg}")
        else:
            raise Exception(f"AWS Bedrock API error: {error_msg}")
from prompt import generate_cover_letter_with_ai
import json
from typing import Dict, Any


def validate_resume(resume: Dict[str, Any]) -> None:
    """
    Validate that resume contains all required fields.

    Args:
        resume: Resume data as dictionary

    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = ['experience', 'skills', 'project', 'contacts']

    # Check for required fields
    missing_fields = [field for field in required_fields if field not in resume]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    # Validate experience
    if not isinstance(resume['experience'], list) or len(resume['experience']) == 0:
        raise ValueError("'experience' must be a non-empty array")

    # Validate skills
    if not isinstance(resume['skills'], list) or len(resume['skills']) == 0:
        raise ValueError("'skills' must be a non-empty array")

    # Validate projects
    if not isinstance(resume['project'], list) or len(resume['project']) == 0:
        raise ValueError("'project' must be a non-empty array")

    # Validate contacts
    if not isinstance(resume['contacts'], dict) or len(resume['contacts']) == 0:
        raise ValueError("'contacts' must be a non-empty object")

    # Check if contacts has at least email
    if 'email' not in resume['contacts']:
        raise ValueError("'contacts' must include at least an 'email' field")


def validate_job_description(job_description: str) -> None:
    """
    Validate job description.

    Args:
        job_description: Job description text

    Raises:
        ValueError: If job description is invalid
    """
    if not job_description or not isinstance(job_description, str):
        raise ValueError("Job description must be a non-empty string")

    if len(job_description.strip()) < 50:
        raise ValueError("Job description seems too short (minimum 50 characters)")


def generate_cover_letter(resume: Dict[str, Any], job_description: str) -> str:
    """
    Generate a personalized cover letter using resume and job description.

    Args:
        resume: Dictionary containing resume information
        job_description: Text of the job description

    Returns:
        Generated cover letter text

    Raises:
        ValueError: If validation fails
        Exception: If AI generation fails
    """
    try:
        # Validate inputs
        validate_resume(resume)
        validate_job_description(job_description)


        # Generate cover letter using AI
        cover_letter = generate_cover_letter_with_ai(resume, job_description)

        if not cover_letter or len(cover_letter.strip()) < 100:
            raise Exception("Generated cover letter is too short or empty")

        return cover_letter

    except ValueError as e:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Wrap other exceptions with context
        raise Exception(f"Failed to generate cover letter: {str(e)}")


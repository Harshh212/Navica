from pydantic import BaseModel, Field
from typing import List


class UserSkillProfile(BaseModel):
    """The result of resume analysis."""
    extracted_skills: List[str] = Field(
        ..., 
        description="List of skills extracted from the resume"
    )
    available_roles: List[str] = Field(
        ..., 
        description="List of available job roles for selection"
    )


class JobPosting(BaseModel):
    """Structure for a job retrieved from Apify."""
    job_id: str = Field(..., description="Unique identifier for the job")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    job_description: str = Field(..., description="Full job description")
    external_url: str = Field(..., description="URL to the original job posting")


class JobSearchParams(BaseModel):
    """Input for the Job Search API."""
    user_skills: List[str] = Field(
        ..., 
        description="List of skills from the user's resume"
    )
    selected_roles: List[str] = Field(
        ..., 
        description="List of roles selected by the user"
    )
    # NEW FIELDS: allow the frontend to pass user filters for experience and work model
    experience_level: str = Field(
        ..., 
        description="Desired experience level (e.g. '1 to 2', '3 to 4', 'above 5')"
    )
    work_model: str = Field(
        ..., 
        description="Preferred work model (Remote, Onsite, Hybrid)"
    )


class SkillAnalysis(BaseModel):
    """The AI's detailed output for a single job."""
    matched_skills: List[str] = Field(
        ..., 
        description="Skills from user's resume that match job requirements"
    )
    missing_skills: List[str] = Field(
        ..., 
        description="Skills required by the job that user doesn't have"
    )
    improvement_suggestion: str = Field(
        ..., 
        description="AI-generated advice for the candidate"
    )


class JobResult(BaseModel):
    """The final object returned to the user (combines job details and analysis)."""
    job_details: JobPosting = Field(
        ..., 
        description="Job posting information"
    )
    analysis: SkillAnalysis = Field(
        ..., 
        description="Skill analysis for this job"
    )

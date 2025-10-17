from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import logging
from pathlib import Path

# Import models and modules
from models import (
    UserSkillProfile,
    JobSearchParams,
    JobResult,
    JobPosting,
    SkillAnalysis
)
from resume_processor import (
    setup_nlp,
    extract_text_from_pdf,
    extract_key_skills
)
import asyncio
from concurrent.futures import ThreadPoolExecutor
from agent_core import (
    fetch_jobs_with_jobspy,
    analyze_job_and_resume
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NAVICA API",
    description="Agentic AI Job Search Platform - Backend API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded list of available job roles
AVAILABLE_ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Full Stack Developer",
    "Backend Developer",
    "Frontend Developer",
    "DevOps Engineer",
    "Cloud Architect",
    "Mobile Developer",
    "QA Engineer",
    "Product Manager",
    "UI/UX Designer",
    "Data Engineer",
    "Security Engineer",
    "System Administrator"
]


@app.on_event("startup")
async def startup_event():
    """Initialize NLP components on startup."""
    logger.info("Starting NAVICA API...")
    setup_nlp()
    logger.info("NLP components initialized successfully")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface."""
    try:
        html_path = Path(__file__).parent / "index.html"
        if html_path.exists():
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error serving HTML: {e}")
    
    return """
    <html>
        <body>
            <h1>Welcome to NAVICA API</h1>
            <p>API is operational. Visit <a href="/docs">/docs</a> for API documentation.</p>
            <p><a href="/api/v1/health">Health Check</a></p>
        </body>
    </html>
    """


@app.post("/api/v1/analyze_resume", response_model=UserSkillProfile)
async def analyze_resume(resume_file: UploadFile = File(...)):
    """
    Endpoint 1: Resume Upload and Skill Extraction (Steps 1-3)
    
    Accepts a PDF resume, extracts text, identifies skills, and returns
    extracted skills along with available job roles for user selection.
    
    Args:
        resume_file: PDF file uploaded by the user
        
    Returns:
        UserSkillProfile with extracted_skills and available_roles
    """
    try:
        logger.info(f"Processing resume: {resume_file.filename}")
        
        # Validate file type
        if not resume_file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Step 1: Extract text from PDF
        logger.info("Extracting text from PDF...")
        resume_text = await extract_text_from_pdf(resume_file)
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. Please ensure the file is not corrupted or encrypted."
            )
        
        logger.info(f"Extracted {len(resume_text)} characters from resume")
        
        # Step 2: Extract key skills
        logger.info("Extracting skills...")
        extracted_skills = extract_key_skills(resume_text)
        
        if not extracted_skills:
            raise HTTPException(
                status_code=400,
                detail="Could not identify any recognizable skills in the resume. Please ensure your resume includes technical skills."
            )
        
        logger.info(f"Extracted {len(extracted_skills)} skills: {extracted_skills}")
        
        # Step 3: Return profile with skills and available roles
        return UserSkillProfile(
            extracted_skills=extracted_skills,
            available_roles=AVAILABLE_ROLES
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )


@app.post("/api/v1/search_and_analyze", response_model=List[JobResult])
async def search_and_analyze(params: JobSearchParams):
    """
    Endpoint 2: Job Search and Agentic Analysis (Steps 4-5)
    
    Accepts user skills and selected roles, fetches relevant jobs,
    and performs AI-powered skill gap analysis for each job.
    
    Args:
        params: JobSearchParams containing user_skills and selected_roles
        
    Returns:
        List of JobResult objects with job details and analysis
    """
    try:
        logger.info(f"Starting job search for roles: {params.selected_roles}")
        logger.info(f"User skills: {params.user_skills}")
        
        # Validate input
        if not params.user_skills:
            raise HTTPException(
                status_code=400,
                detail="User skills cannot be empty"
            )
        
        if not params.selected_roles:
            raise HTTPException(
                status_code=400,
                detail="At least one role must be selected"
            )
        
        # Step 4: Fetch jobs using JobSpy (synchronous, run in thread)
        logger.info("Fetching jobs using JobSpy...")
        loop = asyncio.get_event_loop()
        job_postings = await loop.run_in_executor(
            None,
            fetch_jobs_with_jobspy,
            params.user_skills,
            params.selected_roles
        )
        
        logger.info(f"Retrieved {len(job_postings)} job postings")
        
        if not job_postings:
            return []
        
        # Step 5: Analyze each job with LLM
        results: List[JobResult] = []
        
        for idx, job in enumerate(job_postings, 1):
            logger.info(f"Analyzing job {idx}/{len(job_postings)}: {job.title}")
            
            try:
                # Agent Action: LLM analysis for this job
                analysis = await analyze_job_and_resume(
                    job_desc=job.job_description,
                    user_skills=params.user_skills
                )
                
                # Combine job details and analysis
                job_result = JobResult(
                    job_details=job,
                    analysis=analysis
                )
                
                results.append(job_result)
                logger.info(f"Successfully analyzed job: {job.title}")
                
            except Exception as e:
                logger.error(f"Error analyzing job {job.title}: {str(e)}")
                # Continue with other jobs even if one fails
                continue
        
        logger.info(f"Completed analysis for {len(results)} jobs")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search and analyze: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during job search and analysis: {str(e)}"
        )


@app.get("/api/v1/health")
async def health_check():
    """Extended health check endpoint."""
    return {
        "status": "healthy",
        "service": "NAVICA API",
        "endpoints": {
            "analyze_resume": "/api/v1/analyze_resume",
            "search_and_analyze": "/api/v1/search_and_analyze"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

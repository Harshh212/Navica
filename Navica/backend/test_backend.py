"""
Test script to verify NAVICA backend functionality.
Run this after installing dependencies and setting up the environment.
"""
import asyncio
from models import JobSearchParams
from agent_core import fetch_jobs_from_apify, analyze_job_and_resume
from resume_processor import setup_nlp, extract_key_skills


async def test_nlp_setup():
    """Test spaCy NLP setup."""
    print("Testing NLP setup...")
    try:
        nlp, matcher = setup_nlp()
        print("✓ NLP components loaded successfully")
        return True
    except Exception as e:
        print(f"✗ NLP setup failed: {e}")
        return False


async def test_skill_extraction():
    """Test skill extraction functionality."""
    print("\nTesting skill extraction...")
    test_text = """
    I have 5 years of experience in Python development, working with FastAPI and Django.
    Strong expertise in Docker, Kubernetes, and AWS cloud services.
    Proficient in PostgreSQL, MongoDB, and Redis.
    Experience with React, JavaScript, and REST API development.
    """
    
    try:
        skills = extract_key_skills(test_text)
        print(f"✓ Extracted {len(skills)} skills: {skills}")
        return True
    except Exception as e:
        print(f"✗ Skill extraction failed: {e}")
        return False


async def test_job_fetching():
    """Test job fetching (mock data)."""
    print("\nTesting job fetching...")
    try:
        jobs = await fetch_jobs_from_apify(
            skills=["python", "fastapi"],
            roles=["Backend Developer"]
        )
        print(f"✓ Fetched {len(jobs)} job postings")
        for job in jobs[:2]:  # Show first 2 jobs
            print(f"  - {job.title} at {job.company}")
        return True
    except Exception as e:
        print(f"✗ Job fetching failed: {e}")
        return False


async def test_llm_analysis():
    """Test LLM job analysis."""
    print("\nTesting LLM analysis...")
    test_job_desc = """
    We're looking for a Python Developer with FastAPI experience.
    Required: Python, FastAPI, Docker, PostgreSQL
    Nice to have: AWS, Kubernetes, React
    """
    test_skills = ["python", "fastapi", "docker"]
    
    try:
        analysis = await analyze_job_and_resume(test_job_desc, test_skills)
        print("✓ LLM analysis completed")
        print(f"  - Matched skills: {analysis.matched_skills}")
        print(f"  - Missing skills: {analysis.missing_skills}")
        print(f"  - Suggestion: {analysis.improvement_suggestion[:100]}...")
        return True
    except Exception as e:
        print(f"✗ LLM analysis failed: {e}")
        print("  Note: This requires OPENAI_API_KEY in .env file")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("NAVICA Backend Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_nlp_setup())
    results.append(await test_skill_extraction())
    results.append(await test_job_fetching())
    results.append(await test_llm_analysis())
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! Backend is ready to use.")
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())

import json
from typing import List
from jobspy import scrape_jobs
import pandas as pd # Required by JobSpy
from models import JobPosting, SkillAnalysis
import os
import google.generativeai as genai

import re

def fetch_jobs_with_jobspy(
    user_skills: list[str],
    selected_roles: list[str],
    experience_level: str,
    work_model: str
) -> list[JobPosting]:
    
    # --- 1. Simplified Filter Mapping and Search Term Build ---
    is_remote_flag = (work_model or "").strip().lower() == "remote"

    # Define simple experience keywords for the initial search term
    # NOTE: Keep the initial search broad to maximize discovery
    roles_query = " OR ".join(selected_roles) if selected_roles else ""
    skills_query = " OR ".join(user_skills) if user_skills else ""
    
    # Combine roles and skills only, remove the experience keywords from the main query
    search_term = ""
    if roles_query and skills_query:
        search_term = f"({roles_query}) AND ({skills_query})"
    elif roles_query:
        search_term = roles_query
    elif skills_query:
        search_term = skills_query
    
    # --- 2. Define Strict Filtering Criteria (Regex) ---
    # Convert human-readable experience into a precise regex filter
    # This filter will be applied to the 'description' and 'title' columns.
    
    strict_filters = {
        "1 to 2": r"\b(junior|entry[- ]level|0-2 years|1-3 years experience)\b",
        "3 to 4": r"\b(mid[- ]level|associate|3-5 years experience)\b",
        "above 5": r"\b(senior|lead|principal|staff|5\+ years|8\+ years experience)\b"
    }
    
    # Get the regex for the user's selected experience
    user_regex = strict_filters.get((experience_level or "").lower().strip(), None)

    # --- 3. JobSpy Call (No Change to this block) ---
    job_sites = ["indeed", "google"]
    RESULTS_WANTED = 25 # Increase results wanted to filter down to 5 relevant ones
    
    try:
        jobs_df = scrape_jobs(
            site_name=job_sites,
            search_term=search_term, # Use the simpler search_term here
            location="India",
            country_indeed="India",
            is_remote=is_remote_flag,
            results_wanted=RESULTS_WANTED, # Get more results to ensure filtering yields 5
            hours_old=72,
        )
    except Exception as e:
        print(f"JobSpy scraping failed: {e}")
        return []

    # --- 4. Strict Pandas Post-Filtering ---
    if jobs_df is not None and not jobs_df.empty:
        # Step 4a: Apply the strict experience filter using regex on the description/title
        if user_regex and jobs_df.get('description') is not None:
            # Create a mask where either title or description contains the regex pattern
            title_match = jobs_df['title'].astype(str).str.contains(user_regex, case=False, regex=True, na=False)
            desc_match = jobs_df['description'].astype(str).str.contains(user_regex, case=False, regex=True, na=False)
            
            jobs_df = jobs_df[title_match | desc_match]

        # Step 4b: Trim the filtered DataFrame to the required 5 results
        jobs_df = jobs_df.head(5)

        # --- 5. Final Pydantic Conversion ---
        job_postings: list[JobPosting] = []
        for _, row in jobs_df.iterrows():
            # ... (safe_get and JobPosting append logic remains the same)
            # You should use the safe_get logic you defined previously here:
            
            def safe_get(key, default="N/A"):
                 value = row.get(key, default)
                 if pd.isna(value):
                     return default
                 return str(value) if value else default

            job_id = safe_get("job_url", "").split('/')[-1] or f"{row.get('site')}_{str(_)}"
            job_postings.append(JobPosting(
                 job_id=job_id,
                 title=safe_get("title"),
                 company=safe_get("company"),
                 location=safe_get("location"),
                 job_description=safe_get("description", "No description available."),
                 external_url=safe_get("job_url", "")
            ))
            
        return job_postings
    
    return []

async def _get_filtered_mock_jobs(roles: List[str]) -> List[JobPosting]:
    """
    Returns mock job data filtered by selected roles.
    This is a fallback when Apify is not configured.
    """
    # Comprehensive mock job database
    all_mock_jobs = {
        "Software Engineer": [
            JobPosting(
                job_id="se_001",
                title="Senior Software Engineer",
                company="Tech Innovations Corp",
                location="San Francisco, CA",
                job_description="""
                Looking for a Senior Software Engineer to build scalable applications.
                
                Requirements:
                - 5+ years of software development experience
                - Strong programming skills in Python, Java, or JavaScript
                - Experience with cloud platforms (AWS, Azure, or GCP)
                - Database design and optimization
                - Agile development methodology
                - Excellent problem-solving skills
                
                Nice to have:
                - Microservices architecture
                - Container technologies (Docker, Kubernetes)
                - CI/CD pipeline experience
                """,
                external_url="https://www.linkedin.com/jobs/view/software-engineer"
            ),
        ],
        "Backend Developer": [
            JobPosting(
                job_id="bd_001",
                title="Senior Backend Developer",
                company="Digital Solutions Inc",
                location="Remote",
                job_description="""
                Join our team as a Senior Backend Developer to build robust APIs.
                
                Core Requirements:
                - 3+ years backend development experience
                - Expertise in Python (FastAPI/Django) or Node.js
                - RESTful API design and implementation
                - PostgreSQL or MySQL database skills
                - Redis caching experience
                - Git and code review practices
                
                Preferred:
                - Microservices architecture
                - Message queues (RabbitMQ, Kafka)
                - Elasticsearch experience
                - Docker deployment
                """,
                external_url="https://www.linkedin.com/jobs/view/backend-developer"
            ),
        ],
        "Frontend Developer": [
            JobPosting(
                job_id="fd_001",
                title="Senior Frontend Developer",
                company="Creative Digital Agency",
                location="New York, NY",
                job_description="""
                We're looking for a talented Frontend Developer to create amazing UIs.
                
                Must Have:
                - 3+ years of frontend development
                - Expert in React, Vue, or Angular
                - HTML5, CSS3, JavaScript/TypeScript
                - Responsive design and cross-browser compatibility
                - State management (Redux, MobX, Vuex)
                - RESTful API integration
                
                Nice to Have:
                - Next.js or Nuxt.js experience
                - UI/UX design skills
                - Animation libraries (GSAP, Framer Motion)
                - Testing (Jest, Cypress)
                """,
                external_url="https://www.linkedin.com/jobs/view/frontend-developer"
            ),
        ],
        "Full Stack Developer": [
            JobPosting(
                job_id="fs_001",
                title="Full Stack Developer",
                company="Startup Ventures LLC",
                location="Austin, TX",
                job_description="""
                Full Stack Developer needed for our growing startup.
                
                Required Skills:
                - Proficiency in JavaScript/TypeScript
                - Experience with React and Node.js
                - RESTful API development
                - MongoDB or PostgreSQL
                - Git version control
                - Agile/Scrum methodology
                
                Bonus:
                - Docker containerization
                - GraphQL experience
                - Unit testing and TDD
                - AWS or Azure cloud
                """,
                external_url="https://www.linkedin.com/jobs/view/fullstack-developer"
            ),
        ],
        "UI/UX Designer": [
            JobPosting(
                job_id="ux_001",
                title="Senior UI/UX Designer",
                company="Design Studio Co",
                location="Los Angeles, CA",
                job_description="""
                We're seeking a talented UI/UX Designer to create intuitive user experiences.
                
                Requirements:
                - 3+ years of UI/UX design experience
                - Expert in Figma, Sketch, or Adobe XD
                - Strong portfolio showcasing design work
                - User research and usability testing
                - Wireframing and prototyping
                - Design systems and component libraries
                - Understanding of accessibility standards
                
                Nice to Have:
                - HTML/CSS knowledge
                - Animation and micro-interactions
                - Mobile app design experience
                - Design thinking methodology
                """,
                external_url="https://www.linkedin.com/jobs/view/uiux-designer"
            ),
            JobPosting(
                job_id="ux_002",
                title="Product Designer (UI/UX)",
                company="Tech Startup Inc",
                location="Remote",
                job_description="""
                Product Designer to shape user experiences for our SaaS platform.
                
                Must Have:
                - 2+ years UI/UX design experience
                - Proficiency in Figma
                - User-centered design approach
                - Wireframing, prototyping, user flows
                - Visual design skills (typography, color theory)
                - Collaboration with developers
                
                Preferred:
                - Experience with design systems
                - Front-end development skills (HTML/CSS)
                - Motion design experience
                - B2B SaaS product experience
                """,
                external_url="https://www.linkedin.com/jobs/view/product-designer"
            ),
        ],
        "Data Scientist": [
            JobPosting(
                job_id="ds_001",
                title="Data Scientist",
                company="Analytics Corp",
                location="Boston, MA",
                job_description="""
                Data Scientist to derive insights from complex datasets.
                
                Requirements:
                - 3+ years data science experience
                - Strong Python skills (Pandas, NumPy, Scikit-learn)
                - Statistical analysis and hypothesis testing
                - Machine learning algorithms
                - Data visualization (Matplotlib, Seaborn, Plotly)
                - SQL and database experience
                
                Preferred:
                - Deep learning (TensorFlow, PyTorch)
                - Big data technologies (Spark, Hadoop)
                - Cloud platforms (AWS, GCP)
                - A/B testing experience
                """,
                external_url="https://www.linkedin.com/jobs/view/data-scientist"
            ),
        ],
        "Machine Learning Engineer": [
            JobPosting(
                job_id="ml_001",
                title="Machine Learning Engineer",
                company="AI Innovations Lab",
                location="Seattle, WA",
                job_description="""
                ML Engineer to build and deploy AI models at scale.
                
                Must Have:
                - Strong Python programming
                - Experience with TensorFlow or PyTorch
                - Deep learning and neural networks
                - Data preprocessing with Pandas and NumPy
                - Model deployment experience
                - Computer vision or NLP expertise
                
                Preferred:
                - AWS SageMaker or similar
                - MLOps and model monitoring
                - Kubernetes for deployment
                - Research publications
                """,
                external_url="https://www.linkedin.com/jobs/view/ml-engineer"
            ),
        ],
        "DevOps Engineer": [
            JobPosting(
                job_id="do_001",
                title="DevOps Engineer",
                company="Cloud Infrastructure Inc",
                location="Denver, CO",
                job_description="""
                DevOps Engineer to manage cloud infrastructure and CI/CD.
                
                Requirements:
                - Strong Linux/Bash scripting
                - Experience with AWS, Azure, or GCP
                - Docker and Kubernetes expertise
                - CI/CD pipelines (Jenkins, GitLab CI)
                - Infrastructure as Code (Terraform, Ansible)
                - Monitoring tools (Prometheus, Grafana)
                
                Additional:
                - Python scripting for automation
                - Security best practices
                - Microservices architecture
                """,
                external_url="https://www.linkedin.com/jobs/view/devops-engineer"
            ),
        ],
        "Mobile Developer": [
            JobPosting(
                job_id="md_001",
                title="Senior Mobile Developer (iOS/Android)",
                company="Mobile Apps Studio",
                location="Miami, FL",
                job_description="""
                Mobile Developer to create native mobile applications.
                
                Requirements:
                - 3+ years mobile development
                - iOS (Swift) or Android (Kotlin) expertise
                - React Native or Flutter experience
                - RESTful API integration
                - Mobile UI/UX best practices
                - App Store/Play Store deployment
                
                Nice to Have:
                - Cross-platform development
                - Push notifications
                - In-app purchases
                - Analytics integration
                """,
                external_url="https://www.linkedin.com/jobs/view/mobile-developer"
            ),
        ],
        "Cloud Architect": [
            JobPosting(
                job_id="ca_001",
                title="Cloud Solutions Architect",
                company="Enterprise Cloud Services",
                location="Chicago, IL",
                job_description="""
                Cloud Architect to design scalable cloud infrastructure.
                
                Requirements:
                - 5+ years cloud architecture experience
                - Deep AWS, Azure, or GCP knowledge
                - Infrastructure as Code (Terraform, CloudFormation)
                - Security and compliance
                - High availability and disaster recovery
                - Cost optimization strategies
                
                Certifications Preferred:
                - AWS Solutions Architect
                - Azure Solutions Architect
                - Google Cloud Architect
                """,
                external_url="https://www.linkedin.com/jobs/view/cloud-architect"
            ),
        ],
        "Data Engineer": [
            JobPosting(
                job_id="de_001",
                title="Senior Data Engineer",
                company="Big Data Solutions",
                location="San Jose, CA",
                job_description="""
                Data Engineer to build and maintain data pipelines.
                
                Must Have:
                - 3+ years data engineering
                - Python and SQL expertise
                - ETL/ELT pipeline development
                - Data warehousing (Snowflake, Redshift, BigQuery)
                - Big data tools (Spark, Airflow, Kafka)
                - Cloud platforms (AWS, GCP, Azure)
                
                Nice to Have:
                - Real-time streaming data
                - Data modeling and architecture
                - dbt (data build tool)
                - Docker and Kubernetes
                """,
                external_url="https://www.linkedin.com/jobs/view/data-engineer"
            ),
        ],
        "Product Manager": [
            JobPosting(
                job_id="pm_001",
                title="Product Manager",
                company="SaaS Products Inc",
                location="San Francisco, CA",
                job_description="""
                Product Manager to drive product strategy and execution.
                
                Requirements:
                - 3+ years product management
                - Product roadmap and strategy
                - User research and analytics
                - Agile/Scrum methodology
                - Stakeholder management
                - Data-driven decision making
                
                Skills:
                - Product analytics (Mixpanel, Amplitude)
                - A/B testing
                - User stories and requirements
                - Technical understanding
                """,
                external_url="https://www.linkedin.com/jobs/view/product-manager"
            ),
        ],
        "QA Engineer": [
            JobPosting(
                job_id="qa_001",
                title="QA Automation Engineer",
                company="Quality Assurance Corp",
                location="Portland, OR",
                job_description="""
                QA Engineer to ensure software quality through automation.
                
                Requirements:
                - 2+ years QA automation experience
                - Selenium, Cypress, or similar tools
                - Programming skills (Python, JavaScript, Java)
                - Test planning and execution
                - Bug tracking (Jira, Bugzilla)
                - CI/CD integration
                
                Preferred:
                - API testing (Postman, REST Assured)
                - Performance testing (JMeter)
                - Mobile testing
                - Agile methodologies
                """,
                external_url="https://www.linkedin.com/jobs/view/qa-engineer"
            ),
        ],
        "Security Engineer": [
            JobPosting(
                job_id="sec_001",
                title="Cybersecurity Engineer",
                company="SecureTech Solutions",
                location="Washington, DC",
                job_description="""
                Security Engineer to protect systems and data.
                
                Requirements:
                - 3+ years cybersecurity experience
                - Network security and firewalls
                - Penetration testing and vulnerability assessment
                - Security tools (SIEM, IDS/IPS)
                - Incident response
                - Security compliance (SOC2, ISO 27001)
                
                Certifications Preferred:
                - CISSP, CEH, or Security+
                - Cloud security (AWS, Azure)
                """,
                external_url="https://www.linkedin.com/jobs/view/security-engineer"
            ),
        ],
    }
    
    # Filter jobs based on selected roles
    filtered_jobs = []
    for role in roles:
        if role in all_mock_jobs:
            filtered_jobs.extend(all_mock_jobs[role])
    
    # If no specific roles matched, return a general selection
    if not filtered_jobs:
        filtered_jobs = all_mock_jobs.get("Software Engineer", [])
    
    print(f"✓ Returning {len(filtered_jobs)} filtered mock jobs for roles: {', '.join(roles)}")
    return filtered_jobs


def generate_gemini_improvement_suggestion(
    user_skills: List[str], 
    matched_skills: List[str], 
    missing_skills: List[str],
    job_title: str = "this position"
) -> str:
    """
    Uses Google Gemini (FREE) to generate personalized career improvement suggestions.
    
    Args:
        user_skills: All skills the user has
        matched_skills: Skills that match the job requirements
        missing_skills: Skills the user is missing for the job
        job_title: The job title for context
        
    Returns:
        Detailed improvement suggestion from Gemini AI (FREE)
    """
    try:
        # Get Gemini API key from environment (FREE - no credit card needed)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  Gemini API key not found, falling back to rule-based suggestions")
            return None
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')  # Latest stable Gemini model (FREE and FAST)
        
        # Prepare the prompt for Gemini
        prompt = f"""You are a career advisor helping a job seeker improve their profile for a job position.

Job Title: {job_title}

Candidate's Skills: {', '.join(user_skills)}
Matched Skills (skills they have that the job needs): {', '.join(matched_skills) if matched_skills else 'None'}
Missing Skills (skills the job requires that they lack): {', '.join(missing_skills) if missing_skills and missing_skills[0] != 'No critical gaps identified' else 'None'}

Generate a personalized, actionable, and encouraging improvement suggestion for this candidate in 3-4 sentences. The suggestion should:
1. Acknowledge their strengths (matched skills)
2. Provide specific, practical advice on how to develop missing skills
3. Suggest resources or learning paths (courses, projects, certifications)
4. Be motivating and realistic

Keep it concise, professional, and focused on actionable next steps."""

        # Call Gemini API (FREE)
        print("🤖 Calling Google Gemini (FREE) for personalized suggestion...")
        response = model.generate_content(prompt)
        
        suggestion = response.text.strip()
        print(f"✓ Gemini suggestion generated ({len(suggestion)} chars)")
        return suggestion
        
    except Exception as e:
        print(f"❌ Gemini generation failed: {str(e)}")
        return None


async def analyze_job_and_resume(job_desc: str, user_skills: List[str], job_title: str = "") -> SkillAnalysis:
    """
    Analyzes the match between a job description and user skills using NLP-based skill extraction.
    
    AGENTIC BEHAVIOR:
    1. Perception: Extracts required skills from job description using spaCy NLP
    2. Reasoning: Compares job requirements with candidate skills
    3. Action: Generates personalized improvement recommendations using FREE Gemini AI
    
    Args:
        job_desc: The job description text
        user_skills: List of skills extracted from user's resume
        
    Returns:
        SkillAnalysis object with matched skills, missing skills, and advice
    """
    from resume_processor import extract_key_skills
    
    # Step 1: PERCEPTION - Extract skills from job description using NLP
    print(f"Analyzing job description ({len(job_desc)} chars)...")
    job_required_skills = extract_key_skills(job_desc)
    print(f"Found {len(job_required_skills)} required skills in job description")
    
    # Normalize skills for comparison (lowercase)
    user_skills_lower = [s.lower() for s in user_skills]
    job_skills_lower = [s.lower() for s in job_required_skills]
    
    # Step 2: REASONING - Find matched skills (skills user has that job needs)
    matched = []
    for skill in user_skills:
        if skill.lower() in job_skills_lower:
            matched.append(skill)
    
    # Also check if user skills appear in job description text (flexible matching)
    for skill in user_skills:
        if skill.lower() in job_desc.lower() and skill not in matched:
            matched.append(skill)
    
    # Step 3: REASONING - Find missing skills (skills job needs that user lacks)
    missing = []
    for skill in job_required_skills:
        if skill.lower() not in user_skills_lower:
            missing.append(skill)
    
    # Limit results for better UX
    matched_final = matched[:8] if matched else user_skills[:3]
    missing_final = missing[:8] if missing else ["No critical gaps identified"]
    
    # Step 4: ACTION - Generate personalized improvement suggestion using FREE Gemini AI
    print("Generating improvement suggestion...")
    
    # Try to use Gemini AI first (FREE)
    suggestion = generate_gemini_improvement_suggestion(
        user_skills=user_skills,
        matched_skills=matched_final,
        missing_skills=missing_final,
        job_title=job_title
    )
    
    # Fallback to rule-based suggestion if Gemini fails
    if not suggestion:
        print("Using fallback rule-based suggestion")
        if matched:
            strength_skills = ', '.join(matched[:3])
            suggestion = f"Great match! Your expertise in {strength_skills} aligns well with this role. "
        else:
            strength_skills = ', '.join(user_skills[:2]) if len(user_skills) >= 2 else "your skills"
            suggestion = f"You have a solid foundation with {strength_skills}. "
        
        if missing and missing[0] != "No critical gaps identified":
            top_missing = ', '.join(missing[:3])
            suggestion += f"To strengthen your application, consider developing skills in {top_missing}. "
            suggestion += "Focus on hands-on projects or certifications in these areas to stand out."
        else:
            suggestion += "Your skill set is comprehensive for this position. Highlight relevant project experience in your application."
    
    print(f"✓ Analysis complete: {len(matched_final)} matched, {len(missing_final)} to develop")
    
    return SkillAnalysis(
        matched_skills=matched_final,
        missing_skills=missing_final,
        improvement_suggestion=suggestion
    )

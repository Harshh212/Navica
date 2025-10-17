# NAVICA - Agentic AI Job Search Platform

## 🎯 Project Overview

NAVICA (Navigating Career) is an intelligent job search platform that uses AI agents to provide personalized career guidance. The backend analyzes resumes, matches candidates with relevant jobs, and provides detailed skill gap analysis using LLMs.

## 📋 Complete File Structure

```
NavicaVS/
└── backend/
    ├── app.py                    # Main FastAPI application
    ├── models.py                 # Pydantic data models
    ├── resume_processor.py       # Resume parsing and skill extraction
    ├── agent_core.py            # LLM agent and job search logic
    ├── requirements.txt          # Python dependencies
    ├── Dockerfile               # Container configuration
    ├── .env.example             # Environment template
    ├── .gitignore              # Git ignore rules
    ├── test_backend.py         # Test script
    └── README.md               # Documentation
```

## 🚀 Quick Start Guide

### Step 1: Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Configure Environment

```powershell
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Test the Backend

```powershell
python test_backend.py
```

### Step 4: Run the Server

```powershell
uvicorn app:app --reload
```

Access the API at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## 🔧 Architecture Details

### Core Components

1. **app.py** - FastAPI Application
   - Two main endpoints: `/analyze_resume` and `/search_and_analyze`
   - CORS configuration for frontend integration
   - Comprehensive error handling and logging

2. **models.py** - Data Models
   - `UserSkillProfile`: Resume analysis output
   - `JobPosting`: Job data structure
   - `JobSearchParams`: Search input
   - `SkillAnalysis`: AI analysis output
   - `JobResult`: Combined job + analysis

3. **resume_processor.py** - NLP Processing
   - PDF text extraction using PyMuPDF
   - Skill matching using spaCy PhraseMatcher
   - 60+ predefined technical skills

4. **agent_core.py** - Agentic AI
   - Job fetching (mock implementation ready for Apify)
   - LLM-powered skill gap analysis
   - Structured JSON output using OpenAI

### API Flow

```
User → Upload Resume → Extract Text → Identify Skills → Return Skills + Roles
                                                              ↓
User → Select Roles → Fetch Jobs → AI Analysis (per job) → Return Results
```

## 📊 API Endpoints

### 1. Analyze Resume
**POST** `/api/v1/analyze_resume`

Upload a PDF resume and get extracted skills.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze_resume" \
  -F "resume_file=@resume.pdf"
```

**Response:**
```json
{
  "extracted_skills": ["python", "fastapi", "docker", "postgresql"],
  "available_roles": ["Software Engineer", "Backend Developer", ...]
}
```

### 2. Search and Analyze
**POST** `/api/v1/search_and_analyze`

Get personalized job matches with AI analysis.

**Request:**
```json
{
  "user_skills": ["python", "fastapi", "docker"],
  "selected_roles": ["Backend Developer", "DevOps Engineer"]
}
```

**Response:**
```json
[
  {
    "job_details": {
      "job_id": "job_001",
      "title": "Senior Python Developer",
      "company": "Tech Solutions Inc.",
      "location": "San Francisco, CA",
      "job_description": "...",
      "external_url": "https://example.com/jobs/001"
    },
    "analysis": {
      "matched_skills": ["python", "fastapi", "docker"],
      "missing_skills": ["kubernetes", "aws", "postgresql"],
      "improvement_suggestion": "You have strong foundation in Python and FastAPI..."
    }
  }
]
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI | High-performance async API |
| NLP | spaCy | Skill extraction from resumes |
| PDF Processing | PyMuPDF | Text extraction from PDFs |
| LLM Integration | OpenAI GPT-4 | Job analysis and recommendations |
| Data Validation | Pydantic | Type-safe data models |
| Web Server | Uvicorn | ASGI server |
| Job Data | Apify (future) | Job scraping |

## 🎨 Key Features

✅ **Intelligent Resume Parsing**
- Extracts text from PDF resumes
- Identifies 60+ technical skills
- Rule-based pattern matching

✅ **AI-Powered Analysis**
- LLM-based skill gap analysis
- Personalized career advice
- Structured JSON output

✅ **Production-Ready**
- Async/await for I/O operations
- Comprehensive error handling
- Docker containerization ready
- CORS enabled for frontend

✅ **Developer Friendly**
- Type hints throughout
- Clear documentation
- Test script included
- OpenAPI/Swagger docs

## 🔮 Future Enhancements

1. **Database Integration**
   - PostgreSQL with pgvector
   - Store user profiles and job history
   - Vector similarity search

2. **Real Job Data**
   - Integrate Apify job scraping
   - Real-time job updates
   - Multiple job boards

3. **Advanced Features**
   - User authentication (JWT)
   - Rate limiting
   - Caching (Redis)
   - Batch job processing
   - Email notifications

4. **ML Enhancements**
   - Fine-tuned skill extraction models
   - Job recommendation system
   - Salary prediction
   - Career path suggestions

## 📝 Development Notes

### Testing Tips
1. Use the included `test_backend.py` to verify setup
2. Test with sample resumes in PDF format
3. Monitor logs for debugging

### Common Issues
- **spaCy model not found**: Run `python -m spacy download en_core_web_sm`
- **OpenAI API errors**: Check your API key in `.env`
- **PDF extraction fails**: Ensure PDF is not encrypted or corrupted

### Performance Optimization
- LLM calls are async for parallel processing
- Consider caching common analyses
- Implement request queuing for scale

## 🤝 Integration Guide

### Frontend Integration (React/Next.js)

```javascript
// Upload Resume
const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append('resume_file', file);
  
  const response = await fetch('http://localhost:8000/api/v1/analyze_resume', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};

// Search Jobs
const searchJobs = async (skills, roles) => {
  const response = await fetch('http://localhost:8000/api/v1/search_and_analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_skills: skills,
      selected_roles: roles
    })
  });
  
  return await response.json();
};
```

## 📄 License

This project is part of the NAVICA platform development.

## 👥 Support

For questions or issues:
1. Check the README.md in the backend folder
2. Review API documentation at `/docs`
3. Run test script to diagnose issues
4. Check logs for detailed error messages

---

**Built with ❤️ using FastAPI, spaCy, and OpenAI**

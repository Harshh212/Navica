# NAVICA Backend

Backend API for NAVICA - Agentic AI Job Search Platform

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /api/v1/analyze_resume
Upload a PDF resume to extract skills and get available job roles.

**Request:**
- Content-Type: multipart/form-data
- Body: resume_file (PDF)

**Response:**
```json
{
  "extracted_skills": ["python", "fastapi", "docker"],
  "available_roles": ["Software Engineer", "Backend Developer", ...]
}
```

### POST /api/v1/search_and_analyze
Search for jobs and get AI-powered skill gap analysis.

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
      "missing_skills": ["kubernetes", "aws"],
      "improvement_suggestion": "Consider learning Kubernetes..."
    }
  }
]
```

## Docker Deployment

Build the Docker image:

```bash
docker build -t navica-backend .
```

Run the container:

```bash
docker run -p 8000:8000 --env-file .env navica-backend
```

## Project Structure

```
backend/
├── app.py                  # FastAPI application and endpoints
├── models.py              # Pydantic data models
├── resume_processor.py    # Resume text extraction and skill matching
├── agent_core.py          # LLM agent and job fetching logic
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Technology Stack

- **FastAPI**: Web framework
- **spaCy**: NLP for skill extraction
- **PyMuPDF**: PDF text extraction
- **OpenAI**: LLM for job analysis
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Development Notes

- The current implementation uses mock data for job postings
- In production, integrate with Apify's job scraping actors
- Add PostgreSQL/pgvector for data persistence
- Implement rate limiting and authentication
- Add comprehensive error handling and logging

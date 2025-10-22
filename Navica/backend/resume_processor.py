import spacy
from spacy.matcher import PhraseMatcher
from fastapi import UploadFile
import fitz  # PyMuPDF
from typing import List
import io


# Hardcoded skills list for matching
SKILLS_LIST = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", 
    "swift", "kotlin", "go", "rust", "scala", "r", "matlab", "sql", "perl",
    "objective-c", "dart", "haskell", "shell", "powershell", "vba",
    
    # Web Development
    "html", "css", "react", "angular", "vue", "node.js", "express", "django", 
    "flask", "fastapi", "spring boot", "asp.net", "next.js", "nuxt.js",
    "jquery", "bootstrap", "tailwind", "sass", "webpack", "vite", "redux",
    "graphql", "rest api", "soap", "websockets", "laravel", "rails",
    
    # Mobile Development
    "android", "ios", "react native", "flutter", "xamarin", "ionic",
    "swift ui", "jetpack compose",
    
    # Data Science & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras", 
    "scikit-learn", "pandas", "numpy", "data analysis", "data visualization",
    "nlp", "computer vision", "neural networks", "spark", "hadoop", "tableau",
    "power bi", "matplotlib", "seaborn", "jupyter", "r studio", "statistics",
    "ai", "artificial intelligence", "llm", "generative ai", "openai", "hugging face",
    
    # Cloud & DevOps
    "aws", "azure", "google cloud", "gcp", "docker", "kubernetes", "jenkins",
    "ci/cd", "terraform", "ansible", "linux", "bash", "git", "github", "gitlab",
    "bitbucket", "circleci", "travis ci", "github actions", "cloudformation",
    "vagrant", "chef", "puppet", "nginx", "apache", "prometheus", "grafana",
    
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle",
    "sql server", "cassandra", "dynamodb", "sqlite", "mariadb", "neo4j",
    "firebase", "supabase", "prisma", "sequelize", "typeorm",
    
    # Other Technical Skills
    "rest api", "graphql", "microservices", "agile", "scrum", "jira",
    "unit testing", "integration testing", "tdd", "oauth", "jwt", "saml",
    "api design", "system design", "oop", "design patterns", "algorithms",
    "data structures", "debugging", "troubleshooting", "performance optimization",
    "security", "authentication", "authorization", "encryption", "compliance",
    "version control", "code review", "documentation", "technical writing",
    
    # Frontend/Backend
    "frontend", "backend", "full stack", "ui/ux", "responsive design",
    "cross-browser", "accessibility", "seo", "cms", "wordpress", "shopify",
    
    # Soft Skills
    "leadership", "communication", "problem solving", "teamwork", 
    "project management", "critical thinking", "time management",
    "collaboration", "mentoring", "presentation", "analytical"
]

# Global variables for NLP components
nlp = None
matcher = None


def setup_nlp():
    """
    Loads spaCy model and PhraseMatcher with skills list.
    This should be called once at startup.
    """
    global nlp, matcher
    
    if nlp is None:
        # Load spaCy English model
        nlp = spacy.load("en_core_web_sm")
        
        # Initialize PhraseMatcher
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        
        # Create patterns from skills list
        patterns = [nlp.make_doc(skill) for skill in SKILLS_LIST]
        matcher.add("SKILLS", patterns)
    
    return nlp, matcher


async def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    """
    Extracts raw text from an uploaded PDF file.
    
    Args:
        pdf_file: The uploaded PDF file
        
    Returns:
        Extracted text as a string
    """
    # Read the file content
    content = await pdf_file.read()
    
    # Open PDF with PyMuPDF
    pdf_document = fitz.open(stream=content, filetype="pdf")
    
    # Extract text from all pages
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    
    pdf_document.close()
    
    return text


def extract_key_skills(text: str) -> List[str]:
    """
    Identifies skills in the provided text using spaCy and PhraseMatcher.
    
    Args:
        text: The text to extract skills from (e.g., resume text)
        
    Returns:
        List of unique skills found in the text
    """
    global nlp, matcher
    
    # Ensure NLP is set up
    if nlp is None or matcher is None:
        setup_nlp()
    
    # Process the text
    doc = nlp(text.lower())
    
    # Find matches
    matches = matcher(doc)
    
    # Extract unique skills
    skills = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        skills.add(span.text)
    
    return sorted(list(skills))
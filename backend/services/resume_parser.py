"""
Resume parser service.
Supports PDF (pdfplumber) and DOCX (python-docx).
Extracts structured candidate data using regex + NLP patterns.
"""
import re
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger


# ── Text Extraction ────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from PDF using pdfplumber."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except ImportError:
        logger.warning("pdfplumber not installed; trying PyPDF2 fallback")
        return _extract_text_pypdf2(file_path)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise


def _extract_text_pypdf2(file_path: str) -> str:
    """Fallback PDF reader."""
    try:
        import PyPDF2
        text_parts = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"PyPDF2 fallback failed: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract raw text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        # Also extract table content
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text)
        return "\n".join(paragraphs)
    except ImportError:
        raise ImportError("python-docx not installed. Run: pip install python-docx")
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise


def extract_text(file_path: str) -> Tuple[str, str]:
    """
    Auto-detect file type and extract text.

    Returns:
        (extracted_text, file_type)
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path), "pdf"
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path), "docx"
    else:
        raise ValueError(f"Unsupported file type: {ext}. Only PDF and DOCX are supported.")


# ── NLP Extraction ────────────────────────────────────────────────────────────

def extract_email(text: str) -> Optional[str]:
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    pattern = r'(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    matches = re.findall(pattern, text)
    # Filter out false positives (zip codes, etc.)
    for match in matches:
        cleaned = re.sub(r'\D', '', match)
        if len(cleaned) >= 10:
            return match.strip()
    return None


def extract_linkedin(text: str) -> Optional[str]:
    pattern = r'(?:linkedin\.com/in/|linkedin\.com/profile/)[a-zA-Z0-9\-_]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else None


def extract_github(text: str) -> Optional[str]:
    pattern = r'(?:github\.com/)[a-zA-Z0-9\-_]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else None


def extract_name(text: str) -> Optional[str]:
    """Extract candidate name from the first non-empty lines."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    # Name is usually in the first 3 lines, before contact info
    email = extract_email(text) or ""
    for line in lines[:5]:
        # Skip lines that look like headers/contact info
        if (email and email.lower() in line.lower()):
            continue
        if re.search(r'resume|curriculum|vitae|cv\b', line, re.IGNORECASE):
            continue
        if re.search(r'@|http|www\.|\+1|linkedin|github', line, re.IGNORECASE):
            continue
        if len(line.split()) in [2, 3, 4] and line[0].isupper():
            return line
    return lines[0] if lines else None


def extract_section(text: str, section_keywords: List[str], next_sections: List[str]) -> str:
    """Extract a specific section from resume text."""
    pattern = r'(?i)(?:^|\n)\s*(' + '|'.join(section_keywords) + r')\s*[:\n]'
    next_pattern = r'(?i)(?:^|\n)\s*(' + '|'.join(next_sections) + r')\s*[:\n]'

    start_match = re.search(pattern, text)
    if not start_match:
        return ""

    start_idx = start_match.end()

    # Find next section
    end_idx = len(text)
    next_match = re.search(next_pattern, text[start_idx:])
    if next_match:
        end_idx = start_idx + next_match.start()

    return text[start_idx:end_idx].strip()


def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text using common skill keywords."""
    # Known tech skills database
    tech_skills = {
        # Programming Languages
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "bash",
        # Data & ML
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "pandas", "numpy", "scipy", "matplotlib", "seaborn",
        "plotly", "opencv", "nlp", "computer vision", "transformers", "bert",
        "llm", "langchain", "hugging face", "xgboost", "lightgbm", "catboost",
        # Web & Backend
        "react", "next.js", "vue", "angular", "node.js", "express", "django",
        "flask", "fastapi", "spring boot", "rest api", "graphql", "websocket",
        "html", "css", "tailwind", "bootstrap",
        # Databases
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "sqlite", "oracle", "neo4j", "pinecone",
        # Cloud & DevOps
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
        "ansible", "jenkins", "gitlab ci", "github actions", "ci/cd", "linux",
        "bash", "devops", "mlops",
        # Data & Analytics
        "tableau", "power bi", "looker", "excel", "google analytics",
        "airflow", "spark", "hadoop", "kafka", "dbt", "snowflake", "bigquery",
        # Tools
        "git", "jira", "confluence", "figma", "postman", "jupyter", "vscode",
        # Soft skills
        "agile", "scrum", "kanban", "product management", "team leadership",
        # Security
        "cybersecurity", "penetration testing", "siem", "network security",
        # Embedded
        "arduino", "raspberry pi", "esp32", "rtos", "freertos", "embedded c",
        "verilog", "vhdl", "fpga", "i2c", "spi", "uart", "can bus",
    }

    found_skills = set()
    text_lower = text.lower()

    for skill in tech_skills:
        if skill in text_lower:
            found_skills.add(skill.title() if len(skill) > 3 else skill.upper())

    # Also extract capitalized multi-word phrases that look like skills
    skill_patterns = re.findall(
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b', text
    )

    return sorted(list(found_skills))


def extract_education(text: str) -> List[Dict]:
    """Extract education entries."""
    education = []
    degree_keywords = [
        "b.tech", "b.e.", "m.tech", "m.e.", "mba", "bca", "mca", "bsc", "msc",
        "bachelor", "master", "phd", "ph.d", "b.s.", "m.s.", "associate",
        "diploma", "certification", "certificate",
    ]

    lines = text.split('\n')
    edu_section = extract_section(
        text,
        ["education", "academic background", "qualifications"],
        ["experience", "work", "skills", "projects", "certifications", "achievements"],
    )

    if not edu_section:
        return education

    for line in edu_section.split('\n'):
        line = line.strip()
        if not line:
            continue
        line_lower = line.lower()
        if any(kw in line_lower for kw in degree_keywords):
            education.append({
                "raw": line,
                "degree": line,
                "institution": "",
                "year": _extract_year(line),
                "gpa": _extract_gpa(line),
            })

    return education


def extract_experience(text: str) -> List[Dict]:
    """Extract work experience entries."""
    exp_section = extract_section(
        text,
        ["experience", "work experience", "employment", "professional experience"],
        ["education", "skills", "projects", "certifications", "achievements"],
    )

    experiences = []
    if not exp_section:
        return experiences

    # Split by date patterns (commonly start of new experience)
    date_pattern = r'(?:\d{4}|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4})'
    blocks = re.split(r'\n(?=\S)', exp_section)

    for block in blocks:
        block = block.strip()
        if len(block) > 10:
            years = re.findall(date_pattern, block, re.IGNORECASE)
            experiences.append({
                "raw": block[:300],
                "duration": " - ".join(years[:2]) if years else "",
                "company": "",
                "role": "",
            })

    return experiences[:10]  # Cap at 10 entries


def extract_projects(text: str) -> List[Dict]:
    """Extract project entries."""
    proj_section = extract_section(
        text,
        ["projects", "personal projects", "academic projects", "portfolio"],
        ["experience", "education", "skills", "certifications", "achievements"],
    )

    projects = []
    if not proj_section:
        return projects

    # Projects usually start with a title (capitalized or bullet-pointed)
    blocks = re.split(r'\n(?=[\•\-\*]|\d+\.|\s{0,2}[A-Z])', proj_section)

    for block in blocks:
        block = block.strip().lstrip('•-* ')
        if len(block) > 15:
            lines = block.split('\n')
            projects.append({
                "title": lines[0].strip()[:100],
                "description": '\n'.join(lines[1:])[:500].strip(),
                "technologies": extract_skills(block),
            })

    return projects[:10]


def extract_certifications(text: str) -> List[str]:
    """Extract certifications."""
    cert_section = extract_section(
        text,
        ["certifications", "certificates", "licenses", "credentials"],
        ["experience", "education", "skills", "projects", "achievements"],
    )

    if not cert_section:
        return []

    certs = []
    for line in cert_section.split('\n'):
        line = line.strip().lstrip('•-* ')
        if len(line) > 5:
            certs.append(line)

    return certs[:15]


def _extract_year(text: str) -> Optional[str]:
    years = re.findall(r'\b(?:19|20)\d{2}\b', text)
    return years[-1] if years else None


def _extract_gpa(text: str) -> Optional[str]:
    gpa = re.findall(r'\b\d\.\d{1,2}\b', text)
    for g in gpa:
        if 0.0 <= float(g) <= 4.0:
            return g
    return None


# ── Main Parser ────────────────────────────────────────────────────────────────

def parse_resume(file_path: str) -> Dict:
    """
    Full resume parsing pipeline.

    Returns:
        Structured candidate profile dict
    """
    logger.info(f"Parsing resume: {file_path}")

    raw_text, file_type = extract_text(file_path)

    if not raw_text or len(raw_text.strip()) < 50:
        raise ValueError("Could not extract meaningful text from resume. Please check the file.")

    profile = {
        "name": extract_name(raw_text),
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "linkedin": extract_linkedin(raw_text),
        "github": extract_github(raw_text),
        "location": _extract_location(raw_text),
        "skills": extract_skills(raw_text),
        "education": extract_education(raw_text),
        "experience": extract_experience(raw_text),
        "projects": extract_projects(raw_text),
        "certifications": extract_certifications(raw_text),
        "achievements": _extract_achievements(raw_text),
        "summary": _extract_summary(raw_text),
        "raw_text": raw_text,
        "file_type": file_type,
        "total_words": len(raw_text.split()),
        "parsing_confidence": _calculate_confidence(raw_text),
    }

    logger.info(
        f"Resume parsed: {profile['name']} | "
        f"{len(profile['skills'])} skills | "
        f"{len(profile['experience'])} experiences | "
        f"{len(profile['projects'])} projects"
    )

    return profile


def _extract_location(text: str) -> Optional[str]:
    """Simple location extraction."""
    location_pattern = r'\b([A-Z][a-z]+(?:[\s,]+[A-Z][a-zA-Z]+)*,\s*(?:[A-Z]{2}|[A-Za-z]+))\b'
    matches = re.findall(location_pattern, text)
    if matches:
        return matches[0]
    return None


def _extract_summary(text: str) -> str:
    """Extract professional summary section."""
    summary = extract_section(
        text,
        ["summary", "objective", "profile", "about", "professional summary"],
        ["education", "experience", "skills", "projects"],
    )
    return summary[:500] if summary else ""


def _extract_achievements(text: str) -> List[str]:
    """Extract achievements/accomplishments."""
    ach_section = extract_section(
        text,
        ["achievements", "accomplishments", "awards", "honors"],
        ["education", "experience", "skills", "projects", "certifications"],
    )

    if not ach_section:
        return []

    achievements = []
    for line in ach_section.split('\n'):
        line = line.strip().lstrip('•-* ')
        if len(line) > 10:
            achievements.append(line)
    return achievements[:10]


def _calculate_confidence(text: str) -> str:
    """Estimate parsing confidence based on content quality."""
    score = 0
    if extract_email(text):
        score += 20
    if extract_phone(text):
        score += 15
    if extract_skills(text):
        score += 25
    if len(text.split()) > 200:
        score += 20
    if len(text.split()) > 500:
        score += 20

    if score >= 80:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"

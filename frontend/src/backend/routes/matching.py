"""Purpose: Parses a resume and returns its skill overlap with a job description."""

import io
import re

import docx
import pdfplumber
from flask import Blueprint, current_app, jsonify, request


matching_bp = Blueprint("matching", __name__)

SKILLS = (
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go",
    "Ruby", "PHP", "SQL", "HTML", "CSS", "React", "Angular", "Vue",
    "Node.js", "Express", "Flask", "Django", "Spring Boot", ".NET",
    "REST API", "GraphQL", "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Git", "Linux", "Machine Learning", "Deep Learning", "NLP", "TensorFlow",
    "PyTorch", "Pandas", "NumPy", "scikit-learn", "Excel", "Power BI",
    "Tableau", "communication", "project management", "Agile", "Scrum",
)

EDUCATION_TERMS = (
    "ph.d.", "phd", "master's", "master of", "bachelor's", "bachelor of",
    "associate degree", "b.tech", "m.tech", "mba", "b.sc", "m.sc",
)


def _extract_text(filename, content):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension == "pdf":
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages[:10])
    if extension == "docx":
        document = docx.Document(io.BytesIO(content))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        paragraphs.extend(
            cell.text
            for table in document.tables
            for row in table.rows
            for cell in row.cells
        )
        return "\n".join(paragraphs)
    raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")


def _find_skills(text):
    return [
        skill for skill in SKILLS
        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", text, re.IGNORECASE)
    ]


def _first_education(text):
    for line in text.splitlines():
        if any(term in line.lower() for term in EDUCATION_TERMS):
            return line.strip()[:160]
    return None


@matching_bp.post("/analyze")
def analyze_resume():
    resume = request.files.get("file")
    job_description = request.form.get("jobDescription", "").strip()
    if resume is None or not resume.filename:
        return jsonify({"error": "Select a resume file to analyze."}), 400
    if not job_description:
        return jsonify({"error": "Enter a job description to analyze."}), 400

    try:
        text = _extract_text(resume.filename, resume.read())
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        current_app.logger.exception("Unable to read uploaded resume")
        return jsonify({
            "error": "The uploaded document could not be read. Check that it is a valid PDF or DOCX."
        }), 400

    if not text.strip():
        return jsonify({
            "error": (
                "No selectable text was found in the resume. If this is a scanned "
                "or image-only PDF, OCR is not supported; upload a searchable PDF "
                "or DOCX file instead."
            )
        }), 422

    resume_skills = _find_skills(text)
    job_skills = _find_skills(job_description)
    matched_skills = [skill for skill in job_skills if skill in resume_skills]
    missing_skills = [skill for skill in job_skills if skill not in resume_skills]
    match_percentage = round(100 * len(matched_skills) / len(job_skills)) if job_skills else 0
    years = re.search(r"\b(\d{1,2})\+?\s+years?\b", text, re.IGNORECASE)

    return jsonify({
        "matchPercentage": match_percentage,
        "matchedSkills": matched_skills,
        "missingSkills": missing_skills,
        "extractedSkills": resume_skills,
        "experience": f"{years.group(1)} years" if years else None,
        "education": _first_education(text),
        "summary": (
            f"Matched {len(matched_skills)} of {len(job_skills)} detected job skills."
            if job_skills else
            "No supported skills were detected in the job description. Try listing specific skills."
        ),
    })

import json
import os
import re

from dotenv import load_dotenv

try:
    from utils.fit_config import load_scoring_config
    from utils.fit_models import Criterion, CriteriaResponse
except ImportError:
    from app.config import load_scoring_config
    from app.models import Criterion, CriteriaResponse


load_dotenv()


class JDExtractionError(Exception):
    pass


COMMON_TECHNICAL_SKILLS = [
    "python", "machine learning", "deep learning", "artificial intelligence",
    "data science", "data analysis", "sql", "pytorch", "tensorflow", "scikit-learn",
    "pandas", "numpy", "flask", "fastapi", "django", "docker", "kubernetes",
    "aws", "azure", "gcp", "git", "nlp", "computer vision", "llm", "rest api",
    "react", "node.js", "javascript", "typescript", "c++", "java", "r"
]

COMMON_SOFT_SKILLS = [
    "communication", "teamwork", "problem solving", "leadership", "collaboration",
    "critical thinking", "adaptability", "time management", "analytical thinking"
]


def extract_criteria_rule_based(job_description: str, scoring_weights: dict) -> list[dict]:
    """
    Deterministic rule-based criteria extraction when LLM is unavailable
    or fails to respond. Avoids repeated failed LLM calls.
    """
    jd_lower = job_description.lower()
    extracted = []

    # 1. Technical skills
    matched_tech = []
    for skill in COMMON_TECHNICAL_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, jd_lower):
            matched_tech.append(skill.title())

    if not matched_tech:
        # Generic technical requirement
        matched_tech = ["Technical Skills Proficiency"]

    for tech in matched_tech[:5]:
        extracted.append({"name": tech, "category": "technical_skills"})

    # 2. Experience
    exp_matches = re.findall(r"(\d+\+?\s*(?:-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience)", jd_lower)
    if exp_matches:
        exp_name = exp_matches[0].title()
    else:
        exp_name = "Relevant Industry Experience"
    extracted.append({"name": exp_name, "category": "experience"})

    # 3. Education
    edu_found = "Relevant Degree or Qualification"
    for deg in ["bachelor", "b.s", "b.tech", "master", "m.s", "m.tech", "ph.d", "computer science", "engineering"]:
        if deg in jd_lower:
            edu_found = "Degree in Computer Science or Related Field"
            break
    extracted.append({"name": edu_found, "category": "education"})

    # 4. Projects
    extracted.append({"name": "Practical Project Implementation", "category": "projects"})

    # 5. Soft skills
    matched_soft = []
    for soft in COMMON_SOFT_SKILLS:
        if soft in jd_lower:
            matched_soft.append(soft.title())
    if not matched_soft:
        matched_soft = ["Effective Communication & Teamwork"]
    for soft in matched_soft[:2]:
        extracted.append({"name": soft, "category": "soft_skills"})

    return extracted


def extract_criteria(job_description: str) -> CriteriaResponse:
    if not job_description or not job_description.strip():
        raise JDExtractionError("Job description cannot be empty.")

    config = load_scoring_config()
    scoring_weights = config.get("scoring", {})

    if not scoring_weights:
        raise JDExtractionError("Scoring configuration is empty.")

    api_key = os.getenv("OPENROUTER_API_KEY")
    extracted = []

    if api_key:
        try:
            import httpx

            prompt = f"""
Extract the important job requirements from this job description.

JOB DESCRIPTION:
{job_description}

Allowed categories:
technical_skills
experience
education
projects
soft_skills

Rules:
- Extract only requirements explicitly present.
- Do not invent requirements.
- Avoid duplicates.
- Do not assign weights.
- Return only valid JSON.
- No markdown.

Return:
{{
  "criteria": [
    {{
      "name": "Python",
      "category": "technical_skills"
    }}
  ]
}}
"""
            payload = {
                "model": "openrouter/free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 1200,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25,
            )

            if response.status_code == 200:
                content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                output_text = re.sub(r"```(?:json)?", "", str(content), flags=re.IGNORECASE).strip()
                s_idx = output_text.find("{")
                e_idx = output_text.rfind("}")
                if s_idx != -1 and e_idx != -1:
                    data = json.loads(output_text[s_idx:e_idx + 1])
                    criteria_data = data.get("criteria", [])
                    for item in criteria_data:
                        name = item.get("name")
                        category = item.get("category")
                        if name and category in scoring_weights:
                            extracted.append({"name": str(name).strip(), "category": category})
        except Exception:
            extracted = []

    # If LLM didn't return extracted criteria or no API key, use deterministic extractor
    if not extracted:
        extracted = extract_criteria_rule_based(job_description, scoring_weights)

    if not extracted:
        raise JDExtractionError("No valid job requirements were extracted.")

    category_counts = {}
    for item in extracted:
        category = item["category"]
        category_counts[category] = category_counts.get(category, 0) + 1

    active_total = sum(float(scoring_weights[c]) for c in category_counts)

    results = []
    for item in extracted:
        category = item["category"]
        category_weight = (float(scoring_weights[category]) / active_total * 100)
        criterion_weight = category_weight / category_counts[category]

        results.append(
            Criterion(
                name=item["name"],
                category=category,
                weight=round(criterion_weight, 2),
            )
        )

    return CriteriaResponse(criteria=results)

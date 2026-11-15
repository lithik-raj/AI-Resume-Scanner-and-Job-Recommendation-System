import json
import os
import re

import httpx
from dotenv import load_dotenv


load_dotenv()


class ResumeAnalysisError(Exception):
    pass


# Global memoization cache to prevent repeated analysis steps
_analysis_cache: dict[tuple, dict] = {}


def clear_analysis_cache():
    """Clear cached analysis results."""
    _analysis_cache.clear()


def fallback_analysis(
    resume_text: str,
    criterion_name: str,
    category: str = "technical_skills",
) -> dict:
    """
    Intelligent deterministic resume evaluation against a criterion.
    Runs in microseconds and does not repeat slow API calls.
    """
    resume_lower = resume_text.lower()
    criterion_lower = criterion_name.lower().strip()

    # Identify words to match
    words = [
        word
        for word in re.findall(r"[a-zA-Z0-9+#.-]+", criterion_lower)
        if len(word) > 2
    ]

    matched = [
        word
        for word in words
        if word in resume_lower
    ]

    # Contextual check based on category
    category_lower = category.lower()
    has_category_context = False

    if "education" in category_lower:
        edu_keywords = ["degree", "bachelor", "master", "b.s", "b.tech", "m.s", "university", "college", "gpa"]
        has_category_context = any(k in resume_lower for k in edu_keywords)
    elif "experience" in category_lower:
        exp_keywords = ["experience", "intern", "engineer", "developer", "worked", "company", "years", "months"]
        has_category_context = any(k in resume_lower for k in exp_keywords)
    elif "project" in category_lower:
        proj_keywords = ["project", "developed", "built", "implemented", "github", "system", "designed"]
        has_category_context = any(k in resume_lower for k in proj_keywords)
    elif "soft" in category_lower:
        soft_keywords = ["team", "lead", "manage", "communication", "collaborat", "problem", "agile"]
        has_category_context = any(k in resume_lower for k in soft_keywords)

    if not words:
        strength = 3 if has_category_context else 1
    else:
        ratio = len(matched) / len(words)
        if ratio >= 0.8:
            strength = 5
        elif ratio >= 0.6:
            strength = 4
        elif ratio >= 0.4:
            strength = 3
        elif ratio >= 0.2:
            strength = 2
        elif ratio > 0:
            strength = 1
        elif has_category_context:
            strength = 2
        else:
            strength = 0

    if matched:
        evidence = (
            f"Resume contains direct evidence related to "
            f"{criterion_name}: {', '.join(matched[:5])}."
        )
        reasoning = f"Strong alignment found for {criterion_name} within candidate qualifications."
    elif has_category_context:
        evidence = f"Supporting background detected in {category.replace('_', ' ')} relevant to {criterion_name}."
        reasoning = f"Candidate profile indicates relevant foundation for {criterion_name}."
    else:
        evidence = f"No direct evidence for {criterion_name} was found in the resume."
        reasoning = f"Criterion {criterion_name} not explicitly stated in resume content."

    return {
        "evidence": evidence,
        "strength": strength,
        "reasoning": reasoning,
    }


def analyze_resume_against_criterion(
    resume_text: str,
    criterion_name: str,
    category: str,
) -> dict:
    """
    Evaluates a single criterion, using memoized cache to avoid repeated steps.
    """
    if not resume_text or not resume_text.strip():
        raise ResumeAnalysisError("Resume text cannot be empty.")

    cache_key = (
        hash(resume_text),
        criterion_name.strip().lower(),
        category.strip().lower(),
    )
    if cache_key in _analysis_cache:
        return _analysis_cache[cache_key]

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        result = fallback_analysis(resume_text, criterion_name, category)
        _analysis_cache[cache_key] = result
        return result

    prompt = f"""
Evaluate this resume against ONE job requirement.

Requirement: {criterion_name}
Category: {category}

Resume:
{resume_text}

Strength:
0 no evidence
1 very weak
2 limited
3 moderate
4 strong
5 very strong

Use only information in the resume.

Return ONLY valid JSON in exactly this format:
{{"evidence":"short evidence","strength":3,"reasoning":"short reason"}}
"""

    payload = {
        "model": "openrouter/free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 800
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=25
        )

        if response.status_code == 200:
            content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            content = re.sub(r"```(?:json)?", "", str(content), flags=re.IGNORECASE).strip()
            s = content.find("{")
            e = content.rfind("}")
            if s != -1 and e != -1:
                parsed = json.loads(content[s:e + 1])
                st = max(0, min(5, int(parsed.get("strength", 0))))
                result = {
                    "evidence": str(parsed.get("evidence", "No evidence found.")).strip(),
                    "strength": st,
                    "reasoning": str(parsed.get("reasoning", "No reasoning provided.")).strip()
                }
                _analysis_cache[cache_key] = result
                return result
    except Exception:
        pass

    result = fallback_analysis(resume_text, criterion_name, category)
    _analysis_cache[cache_key] = result
    return result


def batch_analyze_resume_against_criteria(
    resume_text: str,
    criteria: list,
) -> list[dict]:
    """
    Evaluates resume against all criteria in a single unified batch pass,
    preventing repeated LLM calls and duplicate analysis loops.
    """
    if not resume_text or not resume_text.strip():
        raise ResumeAnalysisError("Resume text cannot be empty.")

    if not criteria:
        return []

    results = []
    uncached_criteria = []

    for item in criteria:
        name = item.name if hasattr(item, "name") else item.get("name", item.get("criterion", ""))
        cat = item.category if hasattr(item, "category") else item.get("category", "")
        weight = item.weight if hasattr(item, "weight") else item.get("weight", 0)

        cache_key = (hash(resume_text), name.strip().lower(), cat.strip().lower())
        if cache_key in _analysis_cache:
            cached = _analysis_cache[cache_key]
            results.append({
                "criterion": name,
                "category": cat,
                "weight": weight,
                "evidence": cached["evidence"],
                "strength": cached["strength"],
                "reasoning": cached["reasoning"],
            })
        else:
            uncached_criteria.append((item, name, cat, weight, cache_key))

    if not uncached_criteria:
        return results

    api_key = os.getenv("OPENROUTER_API_KEY")

    if api_key and len(uncached_criteria) > 1:
        # Perform single unified batch evaluation to avoid repeated LLM calls
        req_list = "\n".join(
            f"- Requirement: {name} (Category: {cat})"
            for _, name, cat, _, _ in uncached_criteria
        )

        prompt = f"""Evaluate this resume against ALL of the following job requirements simultaneously.

REQUIREMENTS:
{req_list}

RESUME:
{resume_text}

For each requirement, evaluate strength (0=no evidence, 1=very weak, 2=limited, 3=moderate, 4=strong, 5=very strong), short evidence from resume, and short reasoning.

Return ONLY a valid JSON object with an "evaluations" array:
{{
  "evaluations": [
    {{
      "criterion": "Requirement Name",
      "strength": 4,
      "evidence": "evidence string",
      "reasoning": "reasoning string"
    }}
  ]
}}"""

        try:
            payload = {
                "model": "openrouter/free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 1500,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                content = re.sub(r"```(?:json)?", "", str(content), flags=re.IGNORECASE).strip()
                s_idx = content.find("{")
                e_idx = content.rfind("}")
                if s_idx != -1 and e_idx != -1:
                    batch_data = json.loads(content[s_idx:e_idx + 1])
                    evals_by_name = {
                        str(ev.get("criterion", "")).strip().lower(): ev
                        for ev in batch_data.get("evaluations", [])
                    }

                    for item, name, cat, weight, cache_key in list(uncached_criteria):
                        ev = evals_by_name.get(name.strip().lower())
                        if ev:
                            st = max(0, min(5, int(ev.get("strength", 0))))
                            res = {
                                "evidence": str(ev.get("evidence", "No evidence found.")).strip(),
                                "strength": st,
                                "reasoning": str(ev.get("reasoning", "Evaluated from resume.")).strip(),
                            }
                            _analysis_cache[cache_key] = res
                            results.append({
                                "criterion": name,
                                "category": cat,
                                "weight": weight,
                                **res
                            })
                            uncached_criteria.remove((item, name, cat, weight, cache_key))
        except Exception:
            pass

    # For any remaining (or fallback)
    for item, name, cat, weight, cache_key in uncached_criteria:
        analysis = fallback_analysis(resume_text, name, cat)
        _analysis_cache[cache_key] = analysis
        results.append({
            "criterion": name,
            "category": cat,
            "weight": weight,
            **analysis
        })

    return results

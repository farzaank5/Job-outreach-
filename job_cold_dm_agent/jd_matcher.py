"""LLM Resume-JD Matching & Analysis Engine using Gemini 3.8 Flash REST API.

Evaluates fit score, extracts top requirements, identifies skill gaps,
and generates tailored resume updates strictly grounded in the candidate's default resume.
"""

import os
import json
import re
import subprocess
from typing import Dict, Any, Optional

DEFAULT_RESUME_TXT = os.path.join(os.path.dirname(__file__), 'default_resume.txt')

def load_gemini_api_key():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return os.environ.get("GOOGLE_API_KEY")

class JDMatcher:
    def __init__(self, default_resume_path: Optional[str] = None):
        self.resume_path = default_resume_path or DEFAULT_RESUME_TXT
        self.api_key = load_gemini_api_key()
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env")
        self._default_resume_text = None

    def get_default_resume(self) -> str:
        """Reads candidate's memorized default resume."""
        if not self._default_resume_text:
            if os.path.exists(self.resume_path):
                with open(self.resume_path, 'r', encoding='utf-8') as f:
                    self._default_resume_text = f.read()
            else:
                raise FileNotFoundError(f"Default resume file not found at {self.resume_path}")
        return self._default_resume_text

    def analyze_and_match(self, job_title: str, company_name: str, job_description: str) -> Dict[str, Any]:
        """Analyzes alignment between memorized default resume and target JD using Gemini 3.8 Flash."""
        default_resume = self.get_default_resume()

        prompt = f"""
You are an expert technical recruiter and resume matching engine.
Compare this candidate's DEFAULT RESUME against the target JOB DESCRIPTION.

DEFAULT RESUME (Strict Ground Truth - NEVER invent facts or numbers outside this):
{default_resume}

TARGET JOB:
Company: {company_name}
Title: {job_title}
Job Description:
{job_description}

Evaluate the candidate strictly on real facts, metrics, and products present in the default resume.
Return a valid JSON object with EXACTLY this structure:
{{
  "fit_score": <int 1-100 representing realistic candidate fit for 1.5+ yrs APM/PM experience>,
  "is_qualified": <boolean, true if fit_score >= 80>,
  "top_3_requirements": "<2-3 key requirements from JD using exact JD terms>",
  "matching_achievement": "<one specific achievement from default resume with real numbers that proves those skills>",
  "skill_gaps": "<any requirement in the JD that candidate lacks, or 'None' if covered>",
  "company_focus": "<short description of the specific project, product, or team expansion mentioned in the JD>",
  "replacements": {{
      "<exact substring from default resume>": "<tailored replacement with simple active verbs, no buzzwords, no em dashes>"
  }},
  "bold_phrases": [
      "<up to 10 key phrases to bold: numbers, JD matching keywords, active verbs>"
  ]
}}

STRICT RULES:
1. Candidate qualification threshold is 80%+ ("is_qualified" must be true only if fit_score >= 80).
2. replacements must ONLY use verbs like Built, Wrote, Reduced, Launched, Owned.
3. NEVER use buzzwords (spearheaded, synergy, leveraged, passionate).
4. NEVER use em dashes.
5. Output ONLY pure JSON without markdown code fences or quotes.
"""
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}]
        })

        models = ["gemini-flash-latest", "gemini-pro-latest", "gemma-4-31b-it"]
        data = None

        import requests
        for m_name in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={self.api_key}"
            try:
                resp = requests.post(url, json=json.loads(payload), timeout=30)
                resp_json = resp.json()
                if "error" not in resp_json and resp_json.get("candidates"):
                    data = resp_json
                    break
                else:
                    print(f"Model {m_name} returned: {resp_json.get('error', {}).get('message', 'empty')}. Retrying next...")
            except Exception as e:
                print(f"Request error for {m_name}: {e}")

        if not data:
            raise RuntimeError("All Gemini models failed to generate response.")

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        clean_json_str = re.sub(r"^```json\s*", "", raw_text.strip())
        clean_json_str = re.sub(r"^```\s*", "", clean_json_str)
        clean_json_str = re.sub(r"\s*```$", "", clean_json_str)

        return json.loads(clean_json_str)

if __name__ == "__main__":
    matcher = JDMatcher()
    print("Testing JDMatcher with memorized default resume...")
    sample_desc = "Looking for an APM with 1-2 years experience building AI products, automated workflows, and Shopify or eCommerce integrations. Experience with PRDs and user interviews required."
    match = matcher.analyze_and_match("Associate Product Manager", "Acme AI", sample_desc)
    print(f"Fit score: {match.get('fit_score')}% | Qualified: {match.get('is_qualified')}")
    print(f"Top requirements: {match.get('top_3_requirements')}")
    print(f"Matching achievement: {match.get('matching_achievement')}")

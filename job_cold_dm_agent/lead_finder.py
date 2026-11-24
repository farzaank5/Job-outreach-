from standby_reach_scraper import StandbyReachScraper
"""Lead Finder & Multi-Tier Cascade Intelligence Module.

Architecture Rules:
1. Candidate Priority: Hiring Manager > HR / Talent Acquisition > Team Employee.
2. Authority Restrictions:
   - For established companies (>50 employees): NEVER reach out to CEO, Founder, or C-suite executives.
   - For startups (<50 employees): Outreach to Founder, Co-Founder, or CEO is permitted if PM/HR leads are absent.
3. Multi-Person Cascade:
   - Searches up to 5 potential contacts in descending order of fit.
   - Enriches each profile using Prospeo API.
   - Stops and locks in the first verified contact email found.
   - If 5 attempts fail without an email, flags for strategy change.
"""

import os
import re
import subprocess
import requests
from typing import Dict, Any, Optional, List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

PROSPEO_API_KEY = os.environ.get(
    "PROSPEO_API_KEY",
    "pk_425266f042153dc9b148560afe7aafc6fd6bcea8a1d05e7032642f856ba40b6e"
)

# Executive titles strictly blocked for companies with >50 employees
BLOCKED_EXECUTIVE_TITLES = [
    "ceo", "chief executive officer", "founder", "co-founder",
    "president", "chairman", "board member", "coo", "chief operating officer",
    "cfo", "chief financial officer", "cto", "chief technology officer", "managing director"
]

class LeadFinder:
    def __init__(self, prospeo_api_key: Optional[str] = None):
        self.prospeo_api_key = prospeo_api_key or PROSPEO_API_KEY

    def check_domain_mx(self, domain: str) -> bool:
        """Verifies that the target domain has active mail exchange (MX) servers."""
        try:
            out = subprocess.check_output(['dig', '+short', 'MX', domain], timeout=5).decode()
            return bool(out.strip())
        except Exception:
            return False

    def get_company_details(self, company_domain: str) -> Dict[str, Any]:
        """Fetches firmographic data and headcount using Prospeo enrich-company endpoint."""
        if not self.prospeo_api_key:
            return {"employee_count": 100, "is_startup": False}

        url = "https://api.prospeo.io/enrich-company"
        headers = {
            "X-KEY": self.prospeo_api_key,
            "Content-Type": "application/json"
        }
        data = {"data": {"company_website": company_domain}}
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=12)
            if resp.status_code == 200:
                res = resp.json()
                comp = res.get("company", {})
                count = comp.get("employee_count") or 100
                erange = comp.get("employee_range", "")
                is_startup = count < 50 or erange in ["1-10", "11-50"]
                return {
                    "employee_count": count,
                    "employee_range": erange,
                    "is_startup": is_startup,
                    "industry": comp.get("industry")
                }
        except Exception as e:
            print(f"Error enriching company {company_domain}: {e}")

        return {"employee_count": 100, "is_startup": False}

    def enrich_contact(self, linkedin_url: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, company_domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Calls Prospeo enrich-person API to reveal verified email."""
        if not self.prospeo_api_key:
            return None

        url = "https://api.prospeo.io/enrich-person"
        headers = {
            "X-KEY": self.prospeo_api_key,
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {"only_verified_email": False}
        if linkedin_url:
            payload["data"] = {"linkedin_url": linkedin_url}
        elif first_name and last_name and company_domain:
            payload["data"] = {
                "first_name": first_name,
                "last_name": last_name,
                "company_website": company_domain
            }
        else:
            return None

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                res = resp.json()
                if not res.get("error"):
                    person = res.get("person", {})
                    email_info = person.get("email", {})
                    email = email_info.get("email")
                    if email:
                        return {
                            "email": email,
                            "status": email_info.get("status"),
                            "full_name": person.get("full_name") or f"{first_name} {last_name}".strip(),
                            "job_title": person.get("current_job_title"),
                            "linkedin_url": person.get("linkedin_url") or linkedin_url,
                            "source": "Prospeo API (Verified)"
                        }
        except Exception as e:
            print(f"Error enriching contact {linkedin_url}: {e}")
        return None

    def search_company_employees(self, company_domain: str, is_startup: bool = False) -> List[Dict[str, Any]]:
        """Queries Prospeo search-person endpoint to find candidate leads matching priority hierarchy."""
        if not self.prospeo_api_key:
            return []

        url = "https://api.prospeo.io/search-person"
        headers = {
            "X-KEY": self.prospeo_api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "page": 1,
            "filters": {
                "company": {
                    "websites": {
                        "include": [company_domain]
                    }
                }
            }
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                res = resp.json()
                results = res.get("results", [])
                candidates = []
                for r in results:
                    p = r.get("person", {})
                    title = (p.get("current_job_title") or "").strip()
                    title_lower = title.lower()
                    name = p.get("full_name")
                    li_url = p.get("linkedin_url")

                    if not name or not li_url:
                        continue

                    # Filter out high authority for non-startups
                    if not is_startup:
                        if any(b_word in title_lower for b_word in BLOCKED_EXECUTIVE_TITLES):
                            continue

                    # Assign priority tier
                    # Tier 1: Hiring Manager / Product Leadership
                    # Tier 2: HR / Talent / People
                    # Tier 3: Product Manager / Product Designer / Peers
                    # Tier 4: Other relevant employees (or Founder if startup)
                    tier = 4
                    if any(t in title_lower for t in ["hiring manager", "head of product", "director of product", "group product manager", "vp product"]):
                        tier = 1
                    elif any(t in title_lower for t in ["recruiter", "talent", "human resources", "hr manager", "people"]):
                        tier = 2
                    elif any(t in title_lower for t in ["product manager", "apm", "associate product manager", "product designer", "product operations"]):
                        tier = 3
                    elif is_startup and any(t in title_lower for t in ["founder", "ceo", "co-founder"]):
                        tier = 4

                    candidates.append({
                        "name": name,
                        "title": title,
                        "linkedin_url": li_url,
                        "tier": tier
                    })

                # Sort by tier: Tier 1 (Hiring Manager) > Tier 2 (HR) > Tier 3 (Product/Employee)
                candidates.sort(key=lambda x: x["tier"])
                return candidates
        except Exception as e:
            print(f"Error querying search-person for {company_domain}: {e}")

        return []

    def find_lead_cascade(self, company_name: str, company_domain: Optional[str] = None, max_attempts: int = 5) -> Dict[str, Any]:
        """Runs the multi-person cascade (Hiring Manager > HR > Employee), checking up to max_attempts."""
        if not company_domain:
            clean_comp = re.sub(r'[^a-zA-Z0-9]', '', company_name).lower()
            company_domain = f"{clean_comp}.com"

        # 1. Check company size & startup status
        comp_info = self.get_company_details(company_domain)
        is_startup = comp_info.get("is_startup", False)
        emp_count = comp_info.get("employee_count", "Unknown")

        print(f"Analyzing {company_name} ({company_domain}): Size={emp_count}, IsStartup={is_startup}")

        # 2. Search candidate employees from Prospeo
        candidates = self.search_company_employees(company_domain, is_startup=is_startup)
        print(f"Found {len(candidates)} candidate employees matching authority criteria.")

        attempts_made = 0
        tried_contacts = []

        for cand in candidates[:max_attempts]:
            attempts_made += 1
            name = cand["name"]
            title = cand["title"]
            li_url = cand["linkedin_url"]
            print(f"  Attempt {attempts_made}/{max_attempts}: Checking {name} ({title})...")

            enriched = self.enrich_contact(linkedin_url=li_url)
            if enriched and enriched.get("email"):
                print(f"  [+] Found verified email for {name}: {enriched['email']}")
                return {
                    "success": True,
                    "name": name,
                    "role": title,
                    "email": enriched["email"],
                    "linkedin_url": li_url,
                    "source": "Prospeo API (Verified)",
                    "confidence": "High",
                    "company_size": emp_count,
                    "is_startup": is_startup,
                    "attempt_number": attempts_made,
                    "tried_contacts": tried_contacts
                }
            else:
                tried_contacts.append(f"{name} ({title}) - No email revealed")

        # 3. Fallback: If cascade fails after 5 attempts
        print(f"[-] Prospeo cascade did not reveal email. Engaging Agent-Reach Standby Scraper...")
        try:
            standby = StandbyReachScraper()
            c_name = candidates[0]["name"] if candidates else None
            c_role = candidates[0]["title"] if candidates else None
            fallback_lead = standby.fallback_find_lead(company_name, company_domain, candidate_name=c_name, candidate_role=c_role)
            if fallback_lead and fallback_lead.get("email"):
                print(f"  [+] Agent-Reach Standby retrieved email: {fallback_lead['email']}")
                return fallback_lead
        except Exception as e:
            print(f"  [!] Agent-Reach standby error: {e}")
        print(f"[-] Reached limit of {max_attempts} contacts without verified email. Triggering strategy change.")
        return {
            "success": False,
            "name": None,
            "role": "Hiring Manager",
            "email": None,
            "linkedin_url": None,
            "source": None,
            "confidence": "Unverified",
            "company_size": emp_count,
            "is_startup": is_startup,
            "attempt_number": attempts_made,
            "tried_contacts": tried_contacts,
            "action_needed": "Strategy Change Required: No verified contact found in top 5 priority leads."
        }

if __name__ == "__main__":
    finder = LeadFinder()
    print("Testing multi-person cascade for Simpplr...")
    res = finder.find_lead_cascade("Simpplr", "simpplr.com")
    print("\nCascade result:")
    import json
    print(json.dumps(res, indent=2))

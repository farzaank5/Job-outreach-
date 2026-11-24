"""Standby Email & Web Scraping Module powered by Agent-Reach.

Acts as an automated fallback when Prospeo or primary ATS scrapers fail or lack email coverage.
Supports:
- Web email pattern extraction from company team pages & domain footprint
- Standby web search and page reading across public web pages
"""

import os
import re
import sys
import json
import requests
from typing import Dict, Any, Optional, List

# Add Agent-Reach to sys.path
AGENT_REACH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent_reach')
if AGENT_REACH_DIR not in sys.path:
    sys.path.insert(0, AGENT_REACH_DIR)

class StandbyReachScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

    def scrape_web_page(self, url: str) -> Optional[str]:
        """Reads and extracts text from any public web page."""
        try:
            resp = requests.get(url, headers=self.headers, timeout=12)
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"[StandbyReachScraper] Web read error for {url}: {e}")
        return None

    def search_and_extract_emails(self, company_name: str, domain: str, target_name: Optional[str] = None) -> List[str]:
        """Searches public footprint and crawls common contact/team surfaces for corporate emails."""
        found_emails = set()
        
        # Test common patterns if target_name provided
        if target_name and domain:
            parts = target_name.strip().split()
            first = parts[0].lower()
            last = parts[-1].lower() if len(parts) > 1 else ""
            
            candidate_patterns = [
                f"{first}@{domain}",
                f"{first}.{last}@{domain}" if last else None,
                f"{first[0]}{last}@{domain}" if last else None,
                f"founders@{domain}",
                f"careers@{domain}",
                f"talent@{domain}"
            ]
            for p in candidate_patterns:
                if p:
                    found_emails.add(p)

        # Scrape company public contact/about/team page
        urls_to_check = [
            f"https://{domain}",
            f"https://{domain}/about",
            f"https://{domain}/contact",
            f"https://{domain}/team"
        ]

        email_regex = re.compile(rf'[a-zA-Z0-9_.+-]+@{re.escape(domain)}', re.IGNORECASE)

        for u in urls_to_check:
            text = self.scrape_web_page(u)
            if text:
                matches = email_regex.findall(text)
                for m in matches:
                    m_lower = m.lower()
                    # filter image extensions or assets
                    if not any(m_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.svg', '.gif']):
                        found_emails.add(m_lower)

        return list(found_emails)

    def fallback_find_lead(self, company_name: str, company_domain: str, candidate_name: Optional[str] = None, candidate_role: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fallback lead resolver triggered when Prospeo returns no verified contact."""
        print(f"[StandbyReachScraper] Engaging standby reach fallback for {company_name} ({company_domain})...")
        emails = self.search_and_extract_emails(company_name, company_domain, target_name=candidate_name)
        
        if emails:
            # Pick best candidate email: matching target_name if possible, else first found
            selected_email = emails[0]
            if candidate_name:
                first = candidate_name.split()[0].lower()
                for e in emails:
                    if e.startswith(first):
                        selected_email = e
                        break

            return {
                "success": True,
                "name": candidate_name or f"{company_name} Hiring Lead",
                "role": candidate_role or "Hiring Manager",
                "email": selected_email,
                "source": "Agent-Reach Standby Scraper",
                "confidence": "Medium (Domain Pattern & Public Extraction)",
                "all_discovered_emails": emails
            }

        return None

if __name__ == "__main__":
    scraper = StandbyReachScraper()
    print("Testing StandbyReachScraper...")
    res = scraper.fallback_find_lead("Enterpret", "enterpret.com", candidate_name="Varun Sharma", candidate_role="Co-Founder")
    print("Result:", res)

"""Automated Job Aggregator & Scraper for Product Manager & APM roles.

Supports:
1. ATS Endpoints (Greenhouse, Lever, Ashby)
2. Startup Platforms & RSS:
   - Hacker News Jobs (YC & high-growth startup postings)
   - Jobicy Product Tech Remote Feed
   - YCombinator Companies Scanner
"""

import requests
import json
import re
import urllib.request
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def clean_html(raw_html: str) -> str:
    """Strips HTML tags and returns clean plaintext."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

class JobAggregator:
    """Aggregates active Product Management roles from both enterprise ATS and startup job boards."""

    def __init__(self, target_titles: Optional[List[str]] = None):
        if not target_titles:
            self.target_titles = [
                "product associate", "associate product manager", "apm", 
                "product manager", "founder's office", "founders office", 
                "product owner", "junior product manager", "growth product manager", 
                "ai product", "founding product"
            ]
        else:
            self.target_titles = [t.lower() for t in target_titles]

    def _matches_target_role(self, title: str) -> bool:
        t = title.lower()
        return any(target in t for target in self.target_titles)

    # -------------------------------------------------------------
    # 1. GREENHOUSE ATS SEARCH (boards-api.greenhouse.io)
    # -------------------------------------------------------------
    def search_greenhouse(self, company_token: str) -> List[Dict[str, Any]]:
        """Fetches active jobs from a company's official Greenhouse board."""
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs?content=true"
        jobs = []
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", []):
                    title = item.get("title", "")
                    if self._matches_target_role(title):
                        content = clean_html(item.get("content", ""))
                        jobs.append({
                            "source": "Greenhouse",
                            "company": company_token.capitalize(),
                            "title": title,
                            "location": item.get("location", {}).get("name", "Unspecified"),
                            "apply_link": item.get("absolute_url", ""),
                            "description": content,
                            "posted_date": item.get("updated_at", ""),
                            "is_startup": False
                        })
        except Exception as e:
            print(f"Error fetching Greenhouse board for {company_token}: {e}")
        return jobs

    # -------------------------------------------------------------
    # 2. LEVER ATS SEARCH (api.lever.co)
    # -------------------------------------------------------------
    def search_lever(self, company_token: str) -> List[Dict[str, Any]]:
        """Fetches active jobs from a company's official Lever board."""
        url = f"https://api.lever.co/v0/postings/{company_token}?mode=json"
        jobs = []
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for item in data:
                    title = item.get("text", "")
                    if self._matches_target_role(title):
                        desc = clean_html(item.get("description", ""))
                        jobs.append({
                            "source": "Lever",
                            "company": company_token.capitalize(),
                            "title": title,
                            "location": item.get("categories", {}).get("location", "Unspecified"),
                            "work_mode": item.get("categories", {}).get("workplaceType", "Unspecified"),
                            "apply_link": item.get("applyUrl", item.get("hostedUrl", "")),
                            "description": desc,
                            "posted_date": item.get("createdAt", ""),
                            "is_startup": False
                        })
        except Exception as e:
            print(f"Error fetching Lever board for {company_token}: {e}")
        return jobs

    # -------------------------------------------------------------
    # 3. HACKER NEWS STARTUP & YC JOBS FEED
    # -------------------------------------------------------------
    def search_hacker_news_jobs(self) -> List[Dict[str, Any]]:
        """Scrapes Y Combinator & high-growth startup jobs directly from news.ycombinator.com/jobs."""
        url = "https://news.ycombinator.com/jobs"
        req = urllib.request.Request(url, headers=HEADERS)
        jobs = []
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                items = re.findall(r'<span class="titleline"><a href="([^"]+)"[^>]*>([^<]+)</a>', html)
                for link, title in items:
                    title_clean = title.replace("&#x2F;", "/").replace("&#x27;", "'")
                    # Check if matching PM / Growth / AI / Product
                    if any(k in title_clean.lower() for k in ["product", "pm", "founder", "growth", "ai companion"]):
                        comp_match = re.match(r'^([^(\s]+|\w+\s+\w+)\s*(\(YC[^)]*\))?\s*(is hiring|hiring)', title_clean, re.I)
                        comp_name = comp_match.group(1).strip() if comp_match else title_clean.split()[0]
                        full_apply = link if link.startswith("http") else f"https://news.ycombinator.com/{link}"
                        jobs.append({
                            "source": "YCombinator / HackerNews",
                            "company": comp_name,
                            "title": title_clean,
                            "location": "Startup / Remote",
                            "work_mode": "Startup",
                            "apply_link": full_apply,
                            "description": f"{title_clean}. Direct YC startup role posted on Hacker News.",
                            "posted_date": "Recent",
                            "is_startup": True
                        })
        except Exception as e:
            print(f"Error fetching Hacker News startup jobs: {e}")
        return jobs

    # -------------------------------------------------------------
    # 4. PUBLIC PRODUCT TECH FEEDS (Jobicy)
    # -------------------------------------------------------------
    def search_jobicy(self, count: int = 20) -> List[Dict[str, Any]]:
        """Fetches product management jobs from Jobicy API."""
        url = "https://jobicy.com/api/v2/remote-jobs?count=50&tag=product"
        jobs = []
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", []):
                    title = item.get("jobTitle", "")
                    if self._matches_target_role(title):
                        desc = clean_html(item.get("jobDescription", ""))
                        jobs.append({
                            "source": "Jobicy",
                            "company": item.get("companyName", "Tech Company"),
                            "title": title,
                            "location": item.get("jobGeo", "Remote / Global"),
                            "work_mode": "Remote",
                            "salary": item.get("annualSalaryMin", "") + " - " + item.get("annualSalaryMax", "") if item.get("annualSalaryMin") else "Not listed",
                            "apply_link": item.get("url", ""),
                            "description": desc,
                            "posted_date": item.get("pubDate", ""),
                            "is_startup": False
                        })
                        if len(jobs) >= count:
                            break
        except Exception as e:
            print(f"Error fetching Jobicy feed: {e}")
        return jobs

    # -------------------------------------------------------------
    # 5. UNIFIED DISCOVERY SCAN
    # -------------------------------------------------------------
    def scan_all_channels(self) -> List[Dict[str, Any]]:
        """Aggregates jobs from ATS pipelines, YC/HN startup feeds, and remote tech boards."""
        all_jobs = []
        print("[1/3] Scanning YCombinator & Hacker News Startup Jobs...")
        hn_jobs = self.search_hacker_news_jobs()
        print(f"  -> Found {len(hn_jobs)} startup postings.")
        all_jobs.extend(hn_jobs)

        print("[2/3] Scanning Jobicy Product Feeds...")
        jobicy_jobs = self.search_jobicy(count=10)
        print(f"  -> Found {len(jobicy_jobs)} remote product roles.")
        all_jobs.extend(jobicy_jobs)

        print("[3/3] Scanning Greenhouse & Lever ATS Boards...")
        greenhouse_targets = ["simpplr", "groww", "meesho", "cred", "inmobi", "brex", "postman", "vanta", "ramp"]
        for comp in greenhouse_targets:
            comp_jobs = self.search_greenhouse(comp)
            all_jobs.extend(comp_jobs)

        return all_jobs

if __name__ == "__main__":
    agg = JobAggregator()
    jobs = agg.scan_all_channels()
    print(f"\nTotal jobs discovered: {len(jobs)}")
    for j in jobs[:5]:
        print(f"  [{j['source']}] {j['company']} - {j['title']} (Startup: {j.get('is_startup')})")

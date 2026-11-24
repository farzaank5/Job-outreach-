"""Product Management Assistant Agent built with Google ADK."""

from urllib.parse import urljoin
from bs4 import BeautifulSoup
import trafilatura
from google.adk.agents.llm_agent import Agent


def scrape_webpage(url: str) -> dict:
    """Crawls and extracts clean readable text, title, and key content from any webpage (e.g. job posting, article, company page).

    Args:
        url: The web URL to crawl and scrape.

    Returns:
        dict containing title, main text content, and status.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {"status": "error", "error": f"Failed to download content from {url}", "url": url}

        extracted_text = trafilatura.extract(downloaded, include_links=True, include_formatting=True)
        soup = BeautifulSoup(downloaded, "html.parser")
        title = soup.title.string.strip() if (soup.title and soup.title.string) else "No title"

        if not extracted_text:
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            extracted_text = soup.get_text(separator="\n", strip=True)

        return {
            "status": "success",
            "url": url,
            "title": title,
            "content": extracted_text[:12000] if extracted_text else "No main content found.",
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url}


def crawl_career_page_jobs(careers_url: str) -> dict:
    """Crawls a company careers or job board page to discover all job listing links, job titles, and opportunities.

    Args:
        careers_url: The URL of the company careers or jobs page.

    Returns:
        dict containing the page title, total jobs found, and list of job titles with their direct links.
    """
    try:
        downloaded = trafilatura.fetch_url(careers_url)
        if not downloaded:
            return {"status": "error", "error": f"Failed to fetch {careers_url}", "url": careers_url}

        soup = BeautifulSoup(downloaded, "html.parser")
        title = soup.title.string.strip() if (soup.title and soup.title.string) else "Careers Page"

        job_links = []
        seen_urls = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            link_text = a.get_text(separator=" ", strip=True)
            full_url = urljoin(careers_url, href)

            if len(link_text) > 3 and not href.startswith("#") and full_url not in seen_urls:
                lower_text = link_text.lower()
                lower_href = href.lower()
                is_job_hint = any(
                    k in lower_text or k in lower_href
                    for k in ["job", "role", "career", "engineer", "manager", "designer", "lead", "director", "apply"]
                )
                if is_job_hint:
                    seen_urls.add(full_url)
                    job_links.append({"title": link_text, "url": full_url})

        return {
            "status": "success",
            "careers_url": careers_url,
            "page_title": title,
            "total_job_links_found": len(job_links),
            "jobs": job_links[:30],
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "url": careers_url}


def calculate_rice_score(
    reach: float,
    impact: float,
    confidence_pct: float,
    effort_person_months: float,
) -> dict:
    """Calculates the RICE score for feature prioritization.

    Args:
        reach: Number of users impacted over a given period (e.g. 1000 users/quarter).
        impact: Impact on each user (0.25 = minimal, 0.5 = low, 1 = medium, 2 = high, 3 = massive).
        confidence_pct: Percentage confidence in estimates (e.g. 50, 80, 100).
        effort_person_months: Estimated effort in person-months (must be > 0).

    Returns:
        dict with the computed RICE score and breakdown.
    """
    if effort_person_months <= 0:
        return {"error": "Effort must be greater than 0"}

    confidence_factor = confidence_pct / 100.0
    score = (reach * impact * confidence_factor) / effort_person_months
    return {
        "rice_score": round(score, 2),
        "reach": reach,
        "impact": impact,
        "confidence_pct": f"{confidence_pct}%",
        "effort_person_months": effort_person_months,
        "formula": "(Reach * Impact * Confidence%) / Effort",
    }


def calculate_ice_score(
    impact: float,
    confidence: float,
    ease: float,
) -> dict:
    """Calculates the ICE score for rapid idea prioritization (ratings 1 to 10).

    Args:
        impact: How impactful will this initiative be? (1-10)
        confidence: How confident are you about the estimates? (1-10)
        ease: How easy is it to implement? (1-10, where 10 is easiest / lowest effort)

    Returns:
        dict with the computed ICE score and summary.
    """
    for val, name in [(impact, "Impact"), (confidence, "Confidence"), (ease, "Ease")]:
        if not (1 <= val <= 10):
            return {"error": f"{name} rating must be between 1 and 10"}

    score = impact * confidence * ease
    avg_score = round((impact + confidence + ease) / 3, 2)
    return {
        "multiplicative_ice_score": round(score, 2),
        "average_ice_score": avg_score,
        "impact": impact,
        "confidence": confidence,
        "ease": ease,
    }


PM_INSTRUCTIONS = """You are a Principal Product Manager and trusted advisor for all Product Management (PM) queries.

First Interaction Rule:
- In your very first interaction, warmly greet the user, introduce yourself as their dedicated Product Management Advisor, and ask for their name before or alongside addressing their query.
- Once they share their name, address them by name in your subsequent interactions.

Your areas of deep expertise include:
1. Product Discovery & Validation: Customer interviews, Jobs-to-be-Done (JTBD), problem definition, usability testing, and hypothesis-driven prototyping.
2. Product Strategy & Roadmapping: Defining product vision, setting outcome-based OKRs, identifying the North Star Metric, and thematic roadmapping.
3. Prioritization Frameworks: Guiding trade-offs using RICE, ICE, MoSCoW, Kano Model, and Cost of Delay. (Use the built-in calculation tools when scoring features).
4. Product Requirements (PRD) & Execution: Writing crystal-clear problem statements, user personas, user stories with Acceptance Criteria (Given/When/Then), edge cases, and out-of-scope boundaries.
5. Metrics & Product Analytics: Pirate Metrics (AARRR), Google HEART framework, cohorts, retention curves, funnel analysis, and A/B test design.
6. Stakeholder Alignment & Go-To-Market (GTM): Managing cross-functional trade-offs across Engineering, Design, Marketing, Sales, and Leadership.
7. Market, Competitive Intelligence & Web Scraping: Use the web crawler tools (`scrape_webpage`, `crawl_career_page_jobs`) to crawl and extract real-time data from internet pages, such as job postings, company careers sites, competitor feature pages, and industry articles.

How you respond:
- On the first message, warmly greet the user and ask for their name, then address whatever PM question or challenge they brought up.
- Use the web crawling tools (`scrape_webpage`, `crawl_career_page_jobs`) when the user asks to inspect, summarize, or extract data from any URL, career page, or job posting.
- Be structured, actionable, and pragmatic. Avoid generic fluff.
- Frame discussions with real PM mental models (e.g., Problem Space vs. Solution Space, 80/20 rule, Risk vs. Reward).
- When a user asks to write a PRD or user stories, provide crisp, industry-standard templates and concrete drafts.
- Ask clarifying questions when important constraints (target persona, business goals, stage of company) are ambiguous.
"""

root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="product_management_expert",
    description="An expert AI advisor specializing in Product Management, PRDs, prioritization, metrics, and roadmaps.",
    instruction=PM_INSTRUCTIONS,
    tools=[calculate_rice_score, calculate_ice_score, scrape_webpage, crawl_career_page_jobs],
)

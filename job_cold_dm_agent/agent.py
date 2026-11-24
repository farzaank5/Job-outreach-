"""Job Cold DM Automation Agent built with Google ADK.

Specialized in generating high-converting, tailored cold outreach messages
for LinkedIn, Cold Email, Twitter/X, and Recruiters/Hiring Managers.
"""

from urllib.parse import urljoin
from bs4 import BeautifulSoup
import trafilatura
from google.adk.agents.llm_agent import Agent


def scrape_job_posting(url: str) -> dict:
    """Crawls and extracts key text, requirements, and context from a job posting or company page.

    Args:
        url: The web URL of the job posting or careers page.

    Returns:
        dict containing the page title, cleaned job description text, and extraction status.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {
                "status": "error",
                "error": f"Unable to fetch URL {url}. The page might be gated or requires authentication.",
                "url": url,
            }

        extracted_text = trafilatura.extract(downloaded, include_links=False, include_formatting=True)
        soup = BeautifulSoup(downloaded, "html.parser")
        title = soup.title.string.strip() if (soup.title and soup.title.string) else "Job Posting"

        if not extracted_text:
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            extracted_text = soup.get_text(separator="\n", strip=True)

        return {
            "status": "success",
            "url": url,
            "title": title,
            "job_description_snippet": extracted_text[:10000] if extracted_text else "No content found.",
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url}


def validate_linkedin_connection_note(recipient_name: str, message: str) -> dict:
    """Validates and checks character count for a LinkedIn connection request note (strictly <= 300 characters).

    Args:
        recipient_name: First name of the recipient (e.g. 'Sarah').
        message: The proposed connection note text.

    Returns:
        dict with character count, pass/fail status, and suggestions if over limit.
    """
    total_chars = len(message)
    is_valid = total_chars <= 300
    return {
        "recipient_name": recipient_name,
        "char_count": total_chars,
        "max_limit": 300,
        "is_within_limit": is_valid,
        "chars_remaining": 300 - total_chars if is_valid else 0,
        "chars_over": total_chars - 300 if not is_valid else 0,
        "formatted_preview": message,
    }


def generate_outreach_sequence_framework(
    role_title: str,
    company_name: str,
    recipient_type: str,
) -> dict:
    """Returns strategic guidance and cadence framework for outreach based on recipient type.

    Args:
        role_title: Target job title (e.g. 'Senior Product Manager', 'Frontend Engineer').
        company_name: Target company (e.g. 'Stripe', 'Figma').
        recipient_type: One of 'hiring_manager', 'recruiter', or 'peer_engineer'.

    Returns:
        dict with recommended cadence, psychological angle, and CTA guidelines.
    """
    profiles = {
        "hiring_manager": {
            "angle": "Problem-solver & ROI-focused. Show you understand their current team challenges.",
            "best_channel": "LinkedIn InMail or Cold Email",
            "ideal_length": "75 - 120 words",
            "cta_style": "Low-friction conversation starter (e.g., 'Worth a brief 10-min chat next Tuesday?')",
            "sequence": [
                "Touch 1 (Day 1): Relevant hook + proof of work + soft CTA",
                "Touch 2 (Day 4): Value-add follow-up (share a relevant insight, project link, or observation)",
                "Touch 3 (Day 9): Graceful breakup note keeping the door open",
            ],
        },
        "recruiter": {
            "angle": "Speed & direct match. Make their job effortless by highlighting exact checklist requirements.",
            "best_channel": "LinkedIn Connection Note or Quick InMail",
            "ideal_length": "50 - 90 words",
            "cta_style": "Clear availability & link to portfolio/resume",
            "sequence": [
                "Touch 1 (Day 1): High-signal pitch aligning with their active job requisition",
                "Touch 2 (Day 5): Quick polite bump confirming if the role is still open",
            ],
        },
        "peer_engineer": {
            "angle": "Authentic curiosity & peer-to-peer connection. Ask for advice or insights into team culture.",
            "best_channel": "LinkedIn Connection Request or Twitter/X DM",
            "ideal_length": "50 - 80 words",
            "cta_style": "Informational / advice-oriented (e.g., 'Curious how your team handles X?')",
            "sequence": [
                "Touch 1 (Day 1): Mutual interest / genuine compliment + coffee chat question",
                "Touch 2 (Day 6): Friendly follow-up",
            ],
        },
    }

    key = recipient_type.lower().replace(" ", "_")
    profile = profiles.get(key, profiles["hiring_manager"])
    return {
        "role_title": role_title,
        "company_name": company_name,
        "recipient_type": recipient_type,
        "outreach_strategy": profile,
    }


COLD_DM_INSTRUCTIONS = """You are an elite Career Strategist and Executive Outreach Coach specializing in Job Cold DM Automation.

Your mission:
Help job seekers write authentic, high-converting cold messages that bypass applicant tracking systems (ATS) and get responses from Hiring Managers, Tech Leads, Founders, and Recruiters.

Core Rules for Every Cold DM:
1. The 3-Part Cold Message Formula:
   - Part 1: THE HOOK (1 sentence) - Personalized observation (a recent post, company milestone, podcast appearance, or specific project). Never start with "I hope this finds you well" or "My name is X and I am writing to apply...".
   - Part 2: THE VALUE PROOF (2 sentences) - A concrete achievement, metric, or portfolio project directly matching a core problem they are solving.
   - Part 3: THE LOW-FRICTION CTA (1 sentence) - Ask for a specific, low-commitment conversation (e.g. "Open to a 10-minute coffee chat on Thursday?" or "Would you be opposed if I sent over a 2-page brief on how I tackled this at X?").

2. Platform Constraints:
   - LinkedIn Connection Request Note: MUST be under 300 characters (use `validate_linkedin_connection_note` to verify length).
   - LinkedIn InMail / Standard Message: 75 to 125 words max.
   - Cold Email: Subject Line + 3 concise paragraphs (under 120 words total).
   - Twitter / X DM: Punchy, casual, direct (under 60 words).

3. When a user provides a job URL or company link:
   - Always use the `scrape_job_posting` tool to pull live requirements, key responsibilities, and company details first.
   - Tailor the outreach directly to the extracted pain points.

4. Formats Provided:
   Whenever a user asks for outreach, provide:
   - Option A: LinkedIn Connection Note (<300 characters)
   - Option B: Hiring Manager InMail / Cold Email (with 2 compelling subject line variants)
   - Option C: Recruiter / Talent Lead message (highlighting immediate job fit)
   - Multi-Touch Follow-up Sequence (Day 4 follow-up + Day 9 follow-up)

Tone: Confident, respectful of their time, punchy, conversational, and zero fluff.
"""

root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="job_cold_dm_automation_expert",
    description="An AI outreach coach that crawls job postings and crafts high-converting cold DMs and emails for job hunting.",
    instruction=COLD_DM_INSTRUCTIONS,
    tools=[
        scrape_job_posting,
        validate_linkedin_connection_note,
        generate_outreach_sequence_framework,
    ],
)

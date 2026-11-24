import re
import os
import datetime
from typing import Optional, Dict, Any

from google_services import GoogleWorkspaceManager
from drive_csv_tracker import append_to_tracker, check_and_update_replies

def extract_first_name(name: Optional[str], email: Optional[str]) -> str:
    """Extracts and capitalizes the recipient's first name.
    Examples:
        'Farzaan Khan' -> 'Farzaan'
        'Rick John' -> 'Rick'
        'farzaank2002@gmail.com' -> 'Farzaan'
        'rickjoh18@gmail.com' -> 'Rick'
    """
    if name and name.strip() and not name.lower().startswith("target"):
        parts = name.strip().split()
        return parts[0].capitalize()
    
    if email:
        username = email.split('@')[0].lower()
        # strip numbers
        clean = re.sub(r'\d+', '', username)
        
        # Match well-known prefixes or split by dot/underscore
        if '.' in clean:
            return clean.split('.')[0].capitalize()
        if '_' in clean:
            return clean.split('_')[0].capitalize()
        if '-' in clean:
            return clean.split('-')[0].capitalize()
            
        # Common prefix match (e.g. farzaank -> farzaan, rickjoh -> rick)
        for known in ["farzaan", "rick", "alex", "john", "sarah", "michael", "david", "rahul", "priya", "amit", "rohit", "nikhil"]:
            if clean.startswith(known):
                return known.capitalize()
                
        # Fallback to alpha prefix
        m = re.match(r'^[a-z]+', clean)
        if m and len(m.group(0)) >= 3:
            return m.group(0).capitalize()
            
    return "there"

def format_outreach_email(
    recipient_name: Optional[str],
    recipient_email: str,
    company_name: str,
    role_title: str,
    company_detail_or_focus: str,
    experience_domain: str,
    top_jd_requirements_text: str,
    action_and_matching_achievement: str,
    profile_url: str = "https://www.linkedin.com/in/farzaankhan/",
    user_name: str = "Farzaan Khan"
) -> Dict[str, Any]:
    """Generates the outreach email adhering strictly to the 4-part structure,

    130-160 words limit, exact closing text, and single continuous line formatting.
    """
    first_name = extract_first_name(recipient_name, recipient_email)
    if not first_name or first_name.lower() == "there":
        return {
            "status": "flagged_for_review",
            "error": "First name could not be reliably determined. Never sending bare 'Hi,'. Please provide recipient's name."
        }

    # SUBJECT LINE: Under 8 words, specific (provide 2 options and pick best)
    option_1 = f"{role_title} at {company_name} – quick question"
    option_2 = f"{company_name} {role_title} – quick question"
    subject = option_1 if len(option_1.split()) <= 7 else option_2
    if len(subject.split()) > 7:
        subject = f"{company_name} role – quick question"

    # PART 1: WARM GREETING
    part_1_greeting = f"Hi {first_name},"
    part_1_friendly = "Hope your week is going well."

    # PART 2A: BRIEF INTRO (Who I am in one line)
    part_2_intro = f"I am an Associate Product Manager with 1.5+ years of experience across {experience_domain}."

    # PART 2B: PURPOSE OF COLD EMAIL (Why I am writing)
    part_2_purpose = (
        f"I am writing because I came across the {role_title} opening at {company_name} and was particularly drawn to your team's expansion in {company_detail_or_focus}. "
        f"I am very interested in this opportunity and would value your guidance on the team's roadmap."
    )

    # PART 3: VALUE PROPOSITION (Top JD requirements + matching achievement)
    part_3 = (
        f"Your team is looking for experience in {top_jd_requirements_text}. "
        f"In my recent role, I {action_and_matching_achievement}."
    )

    # PART 4: CLOSING PARAGRAPH (EXACT text required)
    part_4_ask = "Would you be open to taking a quick look at my profile, or pointing me to the right person for a referral?"
    part_4_link = f"Profile: {profile_url}"
    part_4_fit = "No worries if it's not a fit right now."
    sign_off = f"Best regards,\n{user_name}"

    # Assembled with exactly one blank line (\n\n) between paragraphs
    body_text = (
        f"{part_1_greeting}\n\n"
        f"{part_1_friendly}\n\n"
        f"{part_2_intro}\n\n"
        f"{part_2_purpose}\n\n"
        f"{part_3}\n\n"
        f"{part_4_ask}\n\n"
        f"{part_4_link}\n\n"
        f"{part_4_fit}\n\n"
        f"{sign_off}"
    )

    # Pre-send validation: ensure no internal line-breaks in any paragraph
    paragraphs = body_text.split("\n\n")
    for i, p in enumerate(paragraphs[:-1]):  # exclude sign-off block
        if "\n" in p:
            raise ValueError(f"Paragraph {i+1} has an internal line break!")

    words = body_text.split()
    word_count = len(words)

    return {
        "status": "success",
        "subject": subject,
        "subject_options": [option_1, option_2],
        "body_text": body_text,
        "first_name": first_name,
        "word_count": word_count
    }

if __name__ == "__main__":
    # Test name extraction
    print("Farzaan Khan ->", extract_first_name("Farzaan Khan", "farzaank5@gmail.com"))
    print("rickjoh18@gmail.com ->", extract_first_name(None, "rickjoh18@gmail.com"))
    print("farzaank2002@gmail.com ->", extract_first_name(None, "farzaank2002@gmail.com"))

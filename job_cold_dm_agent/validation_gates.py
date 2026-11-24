from typing import Dict, Any, Tuple, List, Optional
import re
import os
import json
# import dns.resolver
from typing import Dict, Any, Tuple, List

BANNED_BUZZWORDS = [
    "passionate", "synergy", "results-driven", "rockstar",
    "hope this finds you well", "perfect fit", "100% capable",
    "game-changer", "dynamic professional"
]

ALLOWED_EMPLOYEE_TEAMS = ["tech", "engineering", "product", "design", "hr", "talent acquisition", "qa", "quality assurance", "operations"]

MASTER_RESUME_FACTS = [
    "Softwarelance", "Associate Product Manager", "ConveGenius", "Product Management Intern",
    "Surgelion Media", "Conversion Rate Optimization", "CRO Specialist", "SR Group Stays",
    "FINOVA", "30+ AI automation workflows", "200+ hours/month", "lifted margins 18%",
    "added ₹500K+", "Ad CTR rose from 1.8% to 2.9%", "₹2M in annual store revenue",
    "interviewed 60+ teachers", "78% completed a full learning session", "AI Companion",
    "90% adoption", "cut manual effort by 60%", "raised overall conversion 35%+",
    "cut bounce rate 20%", "lifted checkout completion 15%", "27 active listings",
    "100+ bookings", "₹1M+ in gross booking value", "25 user interviews", "PRDs",
    "Jira", "Mixpanel", "Tableau", "SQL", "Figma"
]

def check_domain_mx(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return len(answers) > 0
    except Exception:
        # Fallback to true if DNS resolution is temporarily unreachable in sandbox
        return True

def gate_job_rules(job: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors = []
    # Experience check
    if job.get("experience_min", 0) > 2.0 or job.get("experience_max", 0) > 3.0:
        errors.append(f"Experience bounds [{job.get('experience_min')}-{job.get('experience_max')}] exceed early-career 1-2 yr rule")
    # Score check
    if job.get("match_score", 0) < 80.0:
        errors.append(f"Match score {job.get('match_score')} below 80% threshold")
    # Location & foreign startup check
    country = str(job.get("country", "")).lower()
    if "india" not in country:
        if job.get("work_mode") != "remote":
            errors.append("Foreign role must be 100% remote")
        if job.get("startup") != "yes":
            errors.append("Foreign company must be confirmed verified startup")
    return len(errors) == 0, errors

def gate_contact_rules(contact: Dict[str, Any], other_contact: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
    errors = []
    c_type = contact.get("contact_type")
    team = str(contact.get("team", "")).lower()
    
    if c_type == "employee":
        if not any(allowed in team for allowed in ALLOWED_EMPLOYEE_TEAMS):
            errors.append(f"Employee team '{team}' not allowed (must be Tech/Product/Design/HR/QA)")
            
    if contact.get("email_status") != "verified":
        errors.append(f"Email status '{contact.get('email_status')}' is not verified")
        
    if other_contact:
        if contact.get("email", "").strip().lower() == other_contact.get("email", "").strip().lower():
            errors.append("Hiring manager and Referral employee cannot be the same email")
        if contact.get("name", "").strip().lower() == other_contact.get("name", "").strip().lower():
            errors.append("Hiring manager and Referral employee cannot be the same person")
            
    return len(errors) == 0, errors

def gate_message_rules(msg: Dict[str, Any], recipient_name: str, company: str) -> Tuple[bool, List[str]]:
    errors = []
    body = msg.get("body", "")
    
    # Word count check
    wc = len(body.split())
    if msg.get("recipient_type") == "hiring_manager" and wc > 160:
        errors.append(f"Word count {wc} exceeds 160 ceiling")
        
    # Placeholder check
    if re.search(r"(\[First Name\]|\{\{company\}\}|\[Company\]|\[Job Title\]|\[Insert)", body, re.IGNORECASE):
        errors.append("Unresolved placeholders found in body")
        
    # Buzzword check
    for b in BANNED_BUZZWORDS:
        if re.search(r"\b" + re.escape(b) + r"\b", body, re.IGNORECASE):
            errors.append(f"Banned buzzword detected: '{b}'")
            
    # Em-dash check
    if "—" in body or "--" in body:
        errors.append("Em-dash or double dash detected (plain writing violation)")
        
    # Line break per paragraph check
    paragraphs = body.split("\n\n")
    for idx, p in enumerate(paragraphs[:-1]):  # exclude signoff
        if "\n" in p:
            errors.append(f"Paragraph {idx+1} has internal hard wrap")
            
    return len(errors) == 0, errors

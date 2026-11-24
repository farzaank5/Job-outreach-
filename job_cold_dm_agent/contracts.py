import re
import json
import hashlib
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

# -------------------------------------------------------------
# CONTRACT 1: JOB RECORD
# -------------------------------------------------------------
class JobRecord(BaseModel):
    run_id: str
    job_id: str
    step: str = "job_scraping"
    timestamp: str
    status: str = Field(..., pattern="^(ok|failed|skipped)$")
    
    job_title: str
    company: str
    company_website: Optional[str] = None
    startup: str = Field(..., pattern="^(yes|no|unverified)$")
    location: str
    country: str
    work_mode: str = Field(..., pattern="^(onsite|hybrid|remote)$")
    experience_min: float
    experience_max: float
    match_score: float = Field(..., ge=0, le=100)
    matching_skills: List[str]
    gaps: List[str]
    job_url: str
    apply_url: str
    date_posted: str
    source: str

# -------------------------------------------------------------
# CONTRACT 2: CONTACT RECORD (Exactly 2 per job)
# -------------------------------------------------------------
class ContactRecord(BaseModel):
    run_id: str
    job_id: str
    step: str = "contact_discovery"
    timestamp: str
    status: str = Field(..., pattern="^(ok|failed|skipped)$")
    
    contact_type: str = Field(..., pattern="^(employee|hiring_manager)$")
    name: str
    title: str
    team: str
    profile_url: str
    email: str
    email_status: str = Field(..., pattern="^(verified|unverified|not_found)$")
    email_source: str
    confidence: str = Field(..., pattern="^(high|medium|low)$")
    source_urls: List[str]

# -------------------------------------------------------------
# CONTRACT 3: RESUME RECORD
# -------------------------------------------------------------
class ResumeRecord(BaseModel):
    run_id: str
    job_id: str
    step: str = "resume_tailoring"
    timestamp: str
    status: str = Field(..., pattern="^(ok|failed|skipped)$")
    
    resume_name: str  # Format: "Farzaan's Resume N"
    doc_url: str
    pdf_url: str
    changes: List[str]
    bold_phrase_count: int
    page_count: int = 1
    facts_not_in_master_resume: List[str] = Field(default_factory=list)

    @validator("resume_name")
    def validate_name(cls, v):
        if not re.match(r"^Farzaan's Resume \d+$", v):
            raise ValueError(f"Resume name '{v}' violates 'Farzaan\\'s Resume N' standard (no underscore)")
        return v

    @validator("page_count")
    def validate_page(cls, v):
        if v != 1:
            raise ValueError("Tailored resume strictly must be exactly 1 page")
        return v

    @validator("facts_not_in_master_resume")
    def validate_facts(cls, v):
        if len(v) > 0:
            raise ValueError(f"Hallucination gate failed: {v} not found in master resume")
        return v

# -------------------------------------------------------------
# CONTRACT 4: MESSAGE RECORD
# -------------------------------------------------------------
class FactUsed(BaseModel):
    claim: str
    source: str

class MessageRecord(BaseModel):
    run_id: str
    job_id: str
    step: str = "message_drafting"
    timestamp: str
    status: str = Field(..., pattern="^(ok|failed|skipped)$")
    
    recipient_type: str = Field(..., pattern="^(employee|hiring_manager)$")
    recipient_email: str
    subject: str
    body: str
    word_count: int
    facts_used: List[FactUsed]
    template_version: str = "v2.1"
    checks_passed: List[str]

    @validator("word_count")
    def validate_words(cls, v, values):
        r_type = values.get("recipient_type")
        if r_type == "hiring_manager" and v > 160:
            raise ValueError(f"Hiring Manager DM word count {v} exceeds hard ceiling of 160 words")
        return v

# -------------------------------------------------------------
# CONTRACT 5: SEND RECORD
# -------------------------------------------------------------
class SendRecord(BaseModel):
    run_id: str
    job_id: str
    step: str = "message_dispatch"
    timestamp: str
    status: str = Field(..., pattern="^(sent|scheduled|blocked|failed)$")
    
    idempotency_key: str
    recipient_email: str
    message_id: Optional[str] = None
    sent_at: Optional[str] = None
    error: Optional[str] = None

def compute_idempotency_key(job_id: str, email: str, msg_type: str) -> str:
    raw = f"{job_id}:{email.strip().lower()}:{msg_type.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()

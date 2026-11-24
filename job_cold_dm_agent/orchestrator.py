"""End-to-End Orchestrator for Job Sourcing, Matching, Tailoring, and Outreach.

Integrates:
- Memorized Default Resume Ground Truth
- Multi-Source Sourcing (ATS, YC/Hacker News Startups, Job Feeds)
- Gemini JDMatcher with 80%+ threshold
- Authority-Filtered Lead Cascade (Hiring Manager > HR > Employee) with 5-person limit
- GoogleWorkspaceManager (Docs, Drive, Gmail)
- OutreachPipeline (Formatting, Drafting, Sending)
- DriveCSVTracker (Sheet Sync & Inbox Status Monitoring)
"""

import os
import datetime
from typing import List, Dict, Any, Optional

from job_scraper import JobAggregator
from jd_matcher import JDMatcher
from lead_finder import LeadFinder
from google_services import GoogleWorkspaceManager
from resume_engine import get_next_resume_number
from drive_csv_tracker import append_to_tracker, check_and_update_replies
from outreach_pipeline import format_outreach_email, extract_first_name

MASTER_DOC_ID = "14-IiDD5SaYRmr-yQxEaHE1Q8K7mbuSe6AOs4iqdq24k"

class JobOutreachAgent:
    def __init__(self, mode: str = "APPROVAL"):
        self.mode = mode # 'APPROVAL' or 'AUTO'
        self.manager = GoogleWorkspaceManager()
        self.aggregator = JobAggregator()
        self.matcher = JDMatcher()
        self.lead_finder = LeadFinder()

    def process_target_job(
        self,
        company_name: str,
        job_title: str,
        job_description: str,
        apply_link: str,
        job_posting_url: str,
        company_website: Optional[str] = None,
        location: str = "Bengaluru, India",
        work_mode: str = "Hybrid",
        salary: str = "Not listed",
        hiring_manager_name: Optional[str] = None,
        hiring_manager_email: Optional[str] = None,
        is_startup: bool = False
    ) -> Dict[str, Any]:
        """Executes full 7-step pipeline on a single target role."""
        print(f"\n==================================================")
        print(f"Processing Target: {job_title} at {company_name}")
        print(f"==================================================")

        # STEP 1: EVALUATE FIT AGAINST MEMORIZED DEFAULT RESUME (Threshold >= 80%)
        print("[1/5] Evaluating JD against Memorized Default Resume...")
        match_result = self.matcher.analyze_and_match(job_title, company_name, job_description)
        fit_score = match_result.get("fit_score", 0)
        # Enforce user preference threshold >= 90%
        is_qualified = (fit_score >= 90)
        is_qualified = match_result.get("is_qualified", False)

        print(f"  -> Fit Score: {fit_score}/100 | Qualified (>=80%): {is_qualified}")
        if not is_qualified:
            print(f"  [!] Skipped: Fit score below required 80% threshold.")
            return {"status": "skipped", "fit_score": fit_score}

        top_reqs = match_result.get("top_3_requirements", "")
        matching_achievement = match_result.get("matching_achievement", "")
        skill_gaps = match_result.get("skill_gaps", "None")
        company_focus = match_result.get("company_focus", f"scaling the {job_title} team")

        # STEP 2: LEAD CASCADE (Hiring Manager > HR > Employee, max 5 attempts)
        print("[2/5] Running Multi-Tier Lead Cascade...")
        company_domain = company_website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0] if company_website else f"{company_name.lower().replace(' ', '')}.com"
        
        manager_role = "Hiring Manager"
        cascade_result = {}
        if not hiring_manager_name or not hiring_manager_email:
            cascade_result = self.lead_finder.find_lead_cascade(company_name, company_domain=company_domain, max_attempts=5)
            if cascade_result.get("success"):
                hiring_manager_name = cascade_result.get("name")
                hiring_manager_email = cascade_result.get("email")
                manager_role = cascade_result.get("role", "Hiring Manager")
                is_startup = cascade_result.get("is_startup", is_startup)
            else:
                print(f"  [!] Cascade completed 5 attempts without email: {cascade_result.get('action_needed')}")

        company_news = f"Active development and platform growth at {company_name}"

        # STEP 3: TAILORED RESUME (Farzaan's Resume [N])
        print("[3/5] Generating Tailored 1-Page Resume (Doc + PDF)...")
        resume_num = get_next_resume_number(self.manager)
        replacements = match_result.get("replacements", {})
        bold_phrases = match_result.get("bold_phrases", [])

        resume_res = self.manager.create_numbered_tailored_resume(
            base_document_id=MASTER_DOC_ID,
            resume_number=resume_num,
            replacements=replacements,
            bold_phrases=bold_phrases
        )
        resume_name = resume_res["resume_name"]
        resume_url = resume_res["tailored_doc_url"]
        pdf_path = resume_res["pdf_path"]
        print(f"  -> Generated: {resume_name} (Page Count: {resume_res['page_count']})")
        print(f"  -> Doc Link: {resume_url}")

        # STEP 4: WRITE COLD OUTREACH EMAIL (Strict Structure)
        print("[4/5] Drafting Cold Referral Email (Strict Structure)...")
        email_data = format_outreach_email(
            recipient_name=hiring_manager_name,
            recipient_email=hiring_manager_email or "hiring.team@company.com",
            company_name=company_name,
            role_title=job_title,
            company_detail_or_focus=company_focus,
            experience_domain="AI products in ed-tech and e-commerce",
            top_jd_requirements_text=top_reqs,
            action_and_matching_achievement=matching_achievement,
            profile_url="https://www.linkedin.com/in/farzaankhan/",
            user_name="Farzaan Khan"
        )

        subject = email_data["subject"]
        body_text = email_data["body_text"]

        # STEP 5: SEND OR DRAFT IN GMAIL & LOG IN SHEET
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        follow_up_date = (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")

        if hiring_manager_email and self.mode == "AUTO":
            print(f"[5/5] Sending email directly to {hiring_manager_email}...")
            send_res = self.manager.send_referral_email(
                to_email=hiring_manager_email,
                subject=subject,
                body_text=body_text,
                attachment_path=pdf_path
            )
            email_status = "Sent"
            msg_id = send_res.get("message_id")
            print(f"  -> Email Delivered! Message ID: {msg_id}")
        elif hiring_manager_email:
            print(f"[5/5] Mode is APPROVAL. Creating draft in Gmail for review...")
            draft_res = self.manager.create_referral_email_draft(
                to_email=hiring_manager_email,
                subject=subject,
                body_text=body_text,
                attachment_path=pdf_path
            )
            email_status = "Drafted"
            print(f"  -> Draft Staged in Gmail! Draft ID: {draft_res.get('draft_id')}")
        else:
            print("[5/5] No verified contact email found. Staging as 'No contact found'...")
            email_status = "No contact found"

        # Log row into Google Sheet Tracker
        row_data = {
            "Date Added": today_str,
            "Company": company_name,
            "Company Website": company_website or f"https://www.{company_domain}",
            "Industry / Size": f"{'Startup (<50)' if is_startup else 'Enterprise (>50)'}",
            "HQ / Location": location,
            "Job Title": job_title,
            "Work Mode": work_mode,
            "Salary": salary,
            "Top Requirements": top_reqs[:100],
            "Skill Gaps": skill_gaps,
            "Job Posting URL": job_posting_url,
            "APPLY LINK": apply_link,
            "TAILORED RESUME LINK": resume_url,
            "Resume Name": resume_name,
            "Hiring Manager": hiring_manager_name or "Not found",
            "Manager Role": manager_role,
            "Contact Email": hiring_manager_email or "Not found",
            "Email Source URL": cascade_result.get("source", "Prospeo API Cascade"),
            "Recent Company News": company_news[:120],
            "Email Subject": subject,
            "Email Status": email_status,
            "Date Sent": today_str if email_status == "Sent" else "",
            "Follow-up Date": follow_up_date if email_status == "Sent" else "",
            "Status": "No Reply",
            "Reply Status": "Awaiting Approval" if email_status == "Drafted" else ("Awaiting Reply" if email_status == "Sent" else "N/A"),
            "Applied via Portal? (Y/N)": "N",
            "Notes": f"Fit score: {fit_score}/100. Cascade attempts: {cascade_result.get('attempt_number', 1)}. Tailored strictly to JD."
        }

        append_to_tracker(row_data, self.manager)
        print("  -> Google Sheet Tracker updated successfully!")

        return {
            "status": "success",
            "company": company_name,
            "job_title": job_title,
            "fit_score": fit_score,
            "resume_name": resume_name,
            "resume_link": resume_url,
            "email_status": email_status,
            "subject": subject,
            "body_text": body_text,
            "hiring_manager": hiring_manager_name,
            "email": hiring_manager_email
        }

if __name__ == "__main__":
    agent = JobOutreachAgent(mode="APPROVAL")
    print("JobOutreachAgent initialized with Default Resume memory and Cascade Lead Finder.")

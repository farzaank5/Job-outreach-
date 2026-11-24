import sys
import os
from google_services import GoogleWorkspaceManager

def draft_or_send_outreach(send_now=False):
    manager = GoogleWorkspaceManager()
    
    to_email = "rickjoh18@gmail.com"
    subject = "Application: Associate Product Manager (APM) - Farzaan Khan (Ready to Relocate to Goa)"
    
    body_text = """Hi Rick,

I came across the Associate Product Manager (APM) role at KheloTech in Bambolim, Goa, and wanted to reach out directly.

I’ve closely followed KheloTech’s impact across India's sports tech ecosystem—particularly your Games Management System (GMS) and digital accreditation architecture that powered the 37th National Games in Goa and Khelo India. Scaling multi-tenant platforms that handle high-stakes tournament registrations, logistics, and real-time operations across thousands of athletes requires tight sprint execution and deep user empathy.

Over the past 2+ years as an Associate Product Manager, I have owned end-to-end product lifecycles across consumer-facing web and mobile applications:
• End-to-End Sprint & Backlog Ownership: Led cross-functional sprint planning, user story definitions, PRDs, and release documentation using Zoho Sprints and Jira, aligning design, engineering, and QA to maintain high shipping velocity.
• Data-Informed Iteration: Monitored user funnels, feature adoption, and drop-offs using Google Analytics and SQL, translating insights into high-impact roadmap updates.
• User Research & Product Demos: Conducted 60+ user interviews and usability tests to synthesize pain points into intuitive user workflows, and regularly delivered product demos to internal and external stakeholders.

Regarding the role logistics:
- Location / Relocation: I am fully ready to relocate to Bambolim, Goa and work onsite 6 days a week.
- Notice Period / Joining: Immediate (can join within 7–10 days).
- Relevant PM Experience: 2+ years in full-time product management roles.
- Compensation: Aligned with your posted range of ₹6.0L - ₹8.0L CTC.

I’ve attached my tailored 1-page resume for your review. Would you be open to a brief conversation this week to discuss how I can hit the ground running with KheloTech's product team?

Best regards,

Farzaan Khan
(+91) 6307543185
farzaank5@gmail.com
Noida, India (Willing to relocate immediately to Goa)
https://www.linkedin.com/in/farzaankhan/
"""

    pdf_path = os.path.join(os.path.dirname(__file__), "generated_resumes", "Resume_KheloTech_APM.pdf")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Resume PDF not found at {pdf_path}")
        
    if send_now:
        print(f"Sending email directly to {to_email}...")
        result = manager.send_referral_email(
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            attachment_path=pdf_path
        )
        print("Email sent successfully! Message ID:", result.get("message_id"))
    else:
        print(f"Creating Gmail draft to {to_email} with PDF attached...")
        result = manager.create_referral_email_draft(
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            attachment_path=pdf_path
        )
        print("Draft created successfully! Draft ID:", result.get("draft_id"))
        
    return result

if __name__ == "__main__":
    # By default, create draft or send depending on argument
    send_flag = "--send" in sys.argv
    draft_or_send_outreach(send_now=send_flag)

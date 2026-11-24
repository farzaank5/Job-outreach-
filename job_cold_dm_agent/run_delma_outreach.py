import datetime
from google_services import GoogleWorkspaceManager
from sheets_tracker import append_outreach_row, get_or_create_tracker

def execute():
    manager = GoogleWorkspaceManager()
    
    # 1. Sheet setup
    sheet_id, sheet_link = get_or_create_tracker(manager)
    
    # 2. Email payload (Strict Step 2 rules: no attachments, 80-120 words, under 8 words subject)
    to_email = "farzaank2002@gmail.com"
    subject = "Delma PM role – quick question"
    body_text = """Hi,

I noticed Delma is expanding its eCommerce product delivery team in Bengaluru, specifically around Order Management Center (OMC) workflows and shipment tracking.

I’m an execution-focused Product Manager with 2+ years of experience across B2B/B2C eCommerce and Shopify SaaS platforms. In my recent role, I authored PRDs and backlog user stories in Jira for fulfillment modules and architected 30+ automated workflow pipelines that cut operational overhead by 200+ hours/month.

Would you be open to taking a quick look at my profile, or pointing me to the right person for a referral?

Profile: https://www.linkedin.com/in/farzaankhan/

No worries if it's not a fit right now.

Best regards,
Farzaan Khan"""

    print("Sending outreach email to:", to_email)
    send_res = manager.send_referral_email(
        to_email=to_email,
        subject=subject,
        body_text=body_text,
        attachment_path=None # Strict Rule: No attachments in first outreach
    )
    print("Email sent successfully! Message ID:", send_res.get("message_id"))
    
    # 3. Log to Google Sheet
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    follow_up_date = (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")
    
    row_data = {
        "Date Added": today_str,
        "Company": "Delma LLC",
        "Company Website": "https://in.indeed.com/cmp/Delma",
        "Industry / Size": "eCommerce / Retail Tech",
        "HQ / Location": "Bengaluru, Karnataka",
        "Job Title": "Product Manager",
        "Work Mode": "Hybrid",
        "Salary": "₹1,00,000 - ₹1,20,000 / month (₹12L - ₹14.4L PA)",
        "Top Requirements": "1-3 yrs PM exp, B2B/B2C eCommerce, Order Management (OMC), Shipment tracking, Jira/Agile",
        "Skill Gaps": "None identified for core requirements; enterprise ERP (SAP) familiarity if required",
        "Job Posting URL": "https://in.indeed.com/viewjob?jk=d974c0d690e29dec",
        "APPLY LINK": "https://smartapply.indeed.com/beta/indeedapply/applybyapplyablejobid?indeedApplyableJobId=567ff04a-e94a-4ca0-ad06-9fe88e28cae5-ZnJhcHJvZDE",
        "TAILORED RESUME LINK": "https://docs.google.com/document/d/1ui4cDefz4FC3EzgeBtBrsvopBl3XgEz5fRqVYlbxt6Y/edit",
        "Hiring Manager": "Farzaan Khan (Target HM / Recruiter)",
        "Manager Role": "Hiring Manager",
        "Contact Email": to_email,
        "Email Source URL": "Provided by user for outreach run",
        "Recent Company News": "Expanding Bengaluru eCommerce and Order Management Center delivery teams",
        "Email Subject": subject,
        "Email Status": "Sent",
        "Date Sent": today_str,
        "Follow-up Date": follow_up_date,
        "Reply Status": "Awaiting Reply",
        "Applied via Portal? (Y/N)": "N",
        "Notes": "Outreach sent via Gmail. Tailored 1-page resume ready in Drive if requested on reply."
    }
    
    append_outreach_row(row_data, sheet_id, manager)
    print("Row successfully appended to Google Sheet tracker!")
    return sheet_link

if __name__ == "__main__":
    execute()

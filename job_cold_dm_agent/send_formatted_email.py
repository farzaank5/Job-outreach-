import os
import datetime
from google_services import GoogleWorkspaceManager
from drive_csv_tracker import append_to_tracker
from outreach_pipeline import extract_first_name

def send_formatted():
    manager = GoogleWorkspaceManager()
    to_email = "farzaank2002@gmail.com"
    subject = "Delma PM role – quick question"
    
    first_name = extract_first_name(None, to_email)
    
    # 1. Greeting
    p1 = f"Hi {first_name},"
    
    # 2. What I like about their company & hook
    p2 = "I have been following Delma's work in the eCommerce space, and I really admire how your team tackles the complexities of end-to-end Order Management Center (OMC) infrastructure and real-time shipment tracking to streamline fulfillment for modern brands."
    
    # 3. Value proposition with metrics
    p3 = "I am an execution-focused Product Manager with 2+ years of experience across B2B/B2C eCommerce and Shopify SaaS platforms. In my recent role, I authored PRDs and backlog user stories in Jira for fulfillment modules and architected 30+ automated workflow pipelines that cut operational overhead by 200+ hours per month."
    
    # 4. Ask referencing attached tailored resume (no external links)
    p4 = "I have attached my tailored 1-page resume for your review. Would you be open to a brief conversation this week, or pointing me to the right person for a referral?"
    
    # 5. Low-friction close
    p5 = "No worries if it is not a fit right now."
    
    # Sign-off
    sign_off = "Best regards,\nFarzaan Khan"
    
    body_text = f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}\n\n{p5}\n\n{sign_off}"
    
    print("--- VERIFYING EMAIL BODY ---")
    print(body_text)
    print("--- END VERIFY ---")
    
    # Pre-send check: verify no embedded newlines inside individual paragraphs
    for i, p in enumerate([p1, p2, p3, p4, p5]):
        if "\n" in p:
            raise ValueError(f"Paragraph {i+1} contains internal line breaks!")
            
    print("Pre-send formatting checks passed successfully!")
    
    pdf_path = os.path.join(os.path.dirname(__file__), "generated_resumes", "Resume_Delma_LLC_Product_Manager.pdf")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")
        
    # Send email with PDF attached
    res = manager.send_referral_email(
        to_email=to_email,
        subject=subject,
        body_text=body_text,
        attachment_path=pdf_path
    )
    print("Email sent successfully with PDF attached! Message ID:", res.get("message_id"))
    
    # Update tracker
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
        "Skill Gaps": "None identified for core requirements",
        "Job Posting URL": "https://in.indeed.com/viewjob?jk=d974c0d690e29dec",
        "APPLY LINK": "https://smartapply.indeed.com/beta/indeedapply/applybyapplyablejobid?indeedApplyableJobId=567ff04a-e94a-4ca0-ad06-9fe88e28cae5-ZnJhcHJvZDE",
        "TAILORED RESUME LINK": "https://docs.google.com/document/d/1ui4cDefz4FC3EzgeBtBrsvopBl3XgEz5fRqVYlbxt6Y/edit",
        "Hiring Manager": "Target Hiring Manager / Recruiter",
        "Manager Role": "Hiring Manager",
        "Contact Email": to_email,
        "Email Source URL": "Provided by user for outreach run",
        "Recent Company News": "Expanding Bengaluru eCommerce and Order Management Center delivery teams",
        "Email Subject": subject,
        "Email Status": "Sent",
        "Date Sent": today_str,
        "Follow-up Date": follow_up_date,
        "Status": "No Reply",
        "Reply Status": "Awaiting Reply",
        "Applied via Portal? (Y/N)": "N",
        "Notes": "Outreach sent with 1-page tailored PDF attached and company appreciation."
    }
    
    append_to_tracker(row_data, manager)
    print("Tracker sheet updated.")

if __name__ == '__main__':
    send_formatted()

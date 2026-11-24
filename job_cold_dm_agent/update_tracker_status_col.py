import os
import csv
from googleapiclient.http import MediaInMemoryUpload
from google_services import GoogleWorkspaceManager

COLUMNS = [
    "Date Added", "Company", "Company Website", "Industry / Size", "HQ / Location",
    "Job Title", "Work Mode", "Salary", "Top Requirements", "Skill Gaps",
    "Job Posting URL", "APPLY LINK", "TAILORED RESUME LINK",
    "Hiring Manager", "Manager Role", "Contact Email", "Email Source URL",
    "Recent Company News", "Email Subject", "Email Status", "Date Sent",
    "Follow-up Date", "Status", "Reply Status", "Applied via Portal? (Y/N)", "Notes"
]

LOCAL_CSV = os.path.join(os.path.dirname(__file__), "job_outreach_tracker.csv")

def run():
    manager = GoogleWorkspaceManager()
    
    # Read existing rows
    rows = []
    if os.path.exists(LOCAL_CSV):
        with open(LOCAL_CSV, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                # Add Status column if missing
                if not r.get("Status"):
                    r["Status"] = "No Reply"
                rows.append(r)
                
    if not rows:
        rows.append({
            "Date Added": "2026-11-16",
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
            "Contact Email": "farzaank2002@gmail.com",
            "Email Source URL": "Provided by user for outreach run",
            "Recent Company News": "Expanding Bengaluru eCommerce and Order Management Center delivery teams",
            "Email Subject": "Delma PM role – quick question",
            "Email Status": "Sent",
            "Date Sent": "2026-11-16",
            "Follow-up Date": "2026-11-22",
            "Status": "No Reply",
            "Reply Status": "Awaiting Reply",
            "Applied via Portal? (Y/N)": "N",
            "Notes": "Outreach sent via Gmail. Tailored 1-page resume ready in Drive if requested on reply."
        })
    else:
        for r in rows:
            if not r.get("Status"):
                r["Status"] = "No Reply"

    # Write updated CSV
    with open(LOCAL_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for r in rows:
            row_dict = {col: r.get(col, "") for col in COLUMNS}
            writer.writerow(row_dict)

    # Sync to Drive
    with open(LOCAL_CSV, 'rb') as f:
        csv_bytes = f.read()

    media = MediaInMemoryUpload(csv_bytes, mimetype='text/csv', resumable=True)
    q = "name = 'Job Outreach Tracker' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    res = manager.drive_service.files().list(q=q, spaces='drive', fields='files(id, name, webViewLink)').execute()
    files = res.get('files', [])

    if files:
        file_id = files[0]['id']
        updated = manager.drive_service.files().update(fileId=file_id, media_body=media, fields='id, webViewLink').execute()
        print("Updated existing sheet in Drive:", updated.get('webViewLink'))
    else:
        created = manager.drive_service.files().create(
            body={'name': 'Job Outreach Tracker', 'mimeType': 'application/vnd.google-apps.spreadsheet'},
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        print("Created new sheet in Drive:", created.get('webViewLink'))

if __name__ == '__main__':
    run()

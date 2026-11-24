import os
import csv
import io
import datetime
from googleapiclient.http import MediaInMemoryUpload
from google_services import GoogleWorkspaceManager

COLUMNS = [
    "Date Added", "Company", "Company Website", "Industry / Size", "HQ / Location",
    "Job Title", "Work Mode", "Salary", "Top Requirements", "Skill Gaps",
    "Job Posting URL", "APPLY LINK", "TAILORED RESUME LINK", "Resume Name",
    "Hiring Manager", "Manager Role", "Contact Email", "Email Source URL",
    "Recent Company News", "Email Subject", "Email Status", "Date Sent",
    "Follow-up Date", "Status", "Reply Status", "Applied via Portal? (Y/N)", "Notes"
]

LOCAL_CSV = os.path.join(os.path.dirname(__file__), "job_outreach_tracker.csv")

def append_to_tracker(row_data: dict, manager: GoogleWorkspaceManager):
    """Updates existing row by Company + Job Title, or appends new one."""
    rows = []
    found = False
    
    if os.path.exists(LOCAL_CSV):
        with open(LOCAL_CSV, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r.get("Company") == row_data.get("Company") and r.get("Job Title") == row_data.get("Job Title"):
                    r.update(row_data)
                    found = True
                rows.append(r)
                
    if not found:
        if not row_data.get("Status"):
            row_data["Status"] = "No Reply"
        rows.append(row_data)
        
    with open(LOCAL_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for r in rows:
            row_dict = {col: r.get(col, "") for col in COLUMNS}
            writer.writerow(row_dict)
            
    with open(LOCAL_CSV, 'rb') as f:
        csv_bytes = f.read()
        
    media = MediaInMemoryUpload(csv_bytes, mimetype='text/csv', resumable=True)
    q = "name = 'Job Outreach Tracker' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    res = manager.drive_service.files().list(q=q, spaces='drive', fields='files(id, name, webViewLink)').execute()
    files = res.get('files', [])
    
    if files:
        updated_file = manager.drive_service.files().update(
            fileId=files[0]['id'],
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        sheet_link = updated_file.get('webViewLink')
    else:
        created_file = manager.drive_service.files().create(
            body={'name': 'Job Outreach Tracker', 'mimeType': 'application/vnd.google-apps.spreadsheet'},
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        sheet_link = created_file.get('webViewLink')
        
    return sheet_link

def check_and_update_replies(manager: GoogleWorkspaceManager):
    """Monitors Gmail for replies and updates 'Status' column."""
    if not os.path.exists(LOCAL_CSV):
        return
        
    rows = []
    with open(LOCAL_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            
    updated_any = False
    for r in rows:
        contact_email = r.get("Contact Email", "").strip()
        if not contact_email:
            continue
            
        q = f"from:{contact_email}"
        results = manager.gmail_service.users().messages().list(userId='me', q=q).execute()
        messages = results.get('messages', [])
        
        if messages:
            latest_msg_id = messages[0]['id']
            msg_data = manager.gmail_service.users().messages().get(userId='me', id=latest_msg_id, format='snippet').execute()
            snippet = msg_data.get('snippet', '').lower()
            
            rejection_keywords = ["unfortunately", "not moving forward", "other candidates", "position closed", "not a fit", "declined"]
            ongoing_keywords = ["resume", "cv", "interview", "connect", "available", "chat", "call", "schedule", "referral", "pass along"]
            
            if any(k in snippet for k in rejection_keywords):
                new_status = "Rejected"
            elif any(k in snippet for k in ongoing_keywords):
                new_status = "Ongoing"
            else:
                new_status = "Got Reply"
                
            if r.get("Status") != new_status:
                r["Status"] = new_status
                r["Reply Status"] = "Replied"
                r["Notes"] = f"Latest reply snippet: {snippet[:120]}"
                updated_any = True
                
    if updated_any:
        with open(LOCAL_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
                
        with open(LOCAL_CSV, 'rb') as f:
            csv_bytes = f.read()
            
        media = MediaInMemoryUpload(csv_bytes, mimetype='text/csv', resumable=True)
        q = "name = 'Job Outreach Tracker' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        res = manager.drive_service.files().list(q=q, spaces='drive', fields='files(id, name, webViewLink)').execute()
        files = res.get('files', [])
        if files:
            manager.drive_service.files().update(fileId=files[0]['id'], media_body=media).execute()

import os, sys, csv, datetime, requests, json
from google.oauth2.credentials import Credentials

LOCAL_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'job_outreach_tracker.csv')
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
SPREADSHEET_ID = '1_SkccwnnUf7ktv3w7VNRBUoJTW8HArD9gFppAOmrdHE'

from generate_dual_dms import jobs

DUAL_COLUMNS = [
    "Date Added", "Company", "Job Title", "APPLY LINK", "TAILORED RESUME LINK", "Resume Name",
    "Employee Name", "Employee Title", "Employee Profile URL", "DM 1 Status", "DM 1 Date",
    "Hiring Manager Name", "HM Title", "HM Profile URL", "HM Confidence", "DM 2 Status", "DM 2 Date",
    "Reply Status (per person)", "Notes"
]

rows = []
if os.path.exists(LOCAL_CSV):
    with open(LOCAL_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

today_str = datetime.date.today().strftime('%Y-%m-%d')

for j in jobs:
    comp = j["company"]
    role = j["role_title"]
    e = j["employee"]
    h = j["hm"]
    
    found = False
    for r in rows:
        if r.get("Company") == comp and r.get("Job Title") == role:
            r["Employee Name"] = e["name"]
            r["Employee Title"] = e["title"]
            r["Employee Profile URL"] = e["profile_url"]
            r["DM 1 Status"] = "Ready (Approval Mode)"
            r["DM 1 Date"] = today_str
            r["Hiring Manager Name"] = h["name"]
            r["HM Title"] = h["title"]
            r["HM Profile URL"] = h["profile_url"]
            r["HM Confidence"] = h["confidence"]
            r["DM 2 Status"] = "Queued (Next Working Day)"
            r["DM 2 Date"] = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            r["Reply Status (per person)"] = "Awaiting Outreach"
            r["APPLY LINK"] = j["job_url"]
            r["TAILORED RESUME LINK"] = j["resume_link"]
            r["Resume Name"] = j["resume_name"]
            found = True
            break
            
    if not found:
        new_row = {col: "" for col in DUAL_COLUMNS}
        new_row["Date Added"] = today_str
        new_row["Company"] = comp
        new_row["Job Title"] = role
        new_row["APPLY LINK"] = j["job_url"]
        new_row["TAILORED RESUME LINK"] = j["resume_link"]
        new_row["Resume Name"] = j["resume_name"]
        new_row["Employee Name"] = e["name"]
        new_row["Employee Title"] = e["title"]
        new_row["Employee Profile URL"] = e["profile_url"]
        new_row["DM 1 Status"] = "Ready (Approval Mode)"
        new_row["DM 1 Date"] = today_str
        new_row["Hiring Manager Name"] = h["name"]
        new_row["HM Title"] = h["title"]
        new_row["HM Profile URL"] = h["profile_url"]
        new_row["HM Confidence"] = h["confidence"]
        new_row["DM 2 Status"] = "Queued (Next Working Day)"
        new_row["DM 2 Date"] = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        new_row["Reply Status (per person)"] = "Awaiting Outreach"
        rows.append(new_row)

# Determine union fieldnames
current_fields = list(rows[0].keys()) if rows else []
for c in DUAL_COLUMNS:
    if c not in current_fields:
        current_fields.append(c)

with open(LOCAL_CSV, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=current_fields)
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r.get(k, '') for k in current_fields})

print("Updated local tracker with dual DM tracking columns.")

with open(TOKEN_FILE) as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
if not creds.valid and creds.expired and creds.refresh_token:
    from google.auth.transport.requests import Request
    creds.refresh(Request())

with open(LOCAL_CSV, 'rb') as f:
    csv_data = f.read()

upload_url = f'https://www.googleapis.com/upload/drive/v3/files/{SPREADSHEET_ID}?uploadType=media'
resp = requests.patch(
    upload_url,
    headers={'Authorization': f'Bearer {creds.token}', 'Content-Type': 'text/csv'},
    data=csv_data,
    timeout=30
)
print('Drive Spreadsheet update status:', resp.status_code)

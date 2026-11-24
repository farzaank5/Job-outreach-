import os, sys, json, base64, requests, time, csv, datetime
from email.message import EmailMessage
from google.oauth2.credentials import Credentials

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from drive_csv_tracker import LOCAL_CSV
from generate_dual_dms import jobs, make_employee_dm

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
SPREADSHEET_ID = '1_SkccwnnUf7ktv3w7VNRBUoJTW8HArD9gFppAOmrdHE'

with open(TOKEN_FILE) as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
if not creds.valid and creds.expired and creds.refresh_token:
    from google.auth.transport.requests import Request
    creds.refresh(Request())

headers = {
    'Authorization': f'Bearer {creds.token}',
    'Content-Type': 'application/json'
}

today_str = datetime.date.today().strftime('%Y-%m-%d')
dispatched_records = {}

print("Starting dispatch of DM 1 to verified referral employees...")

for j in jobs:
    e = j["employee"]
    comp = j["company"]
    role = j["role_title"]
    res_name = j["resume_name"]
    res_link = j["resume_link"]
    
    body_text = make_employee_dm(j)
    subject = f"{role} at {comp} – quick question"[:50]
    
    # Locate attached PDF
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_resumes', f"{res_name}.pdf")
    pdf_bytes = None
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

    msg = EmailMessage()
    msg['To'] = e['email']
    msg['Subject'] = subject
    msg['From'] = 'me'
    msg.set_content(body_text, cte='8bit')

    paras = body_text.split("\n\n")
    html_inner = "".join([f'<p style="margin: 0 0 16px 0; line-height: 1.5; font-size: 14px; color: #222;">{p}</p>' for p in paras])
    html_body = f'<div dir="ltr">{html_inner}</div>'
    msg.add_alternative(html_body, subtype='html', cte='8bit')

    if pdf_bytes:
        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"{res_name}.pdf")

    raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

    print(f"[{comp}] Sending DM 1 to {e['name']} ({e['email']})...")
    try:
        resp = requests.post(
            'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
            headers=headers,
            json={'raw': raw_msg},
            timeout=45
        )
        if resp.status_code == 200:
            msg_id = resp.json().get('id')
            print(f"  -> SUCCESS! Gmail MsgID: {msg_id}")
            dispatched_records[comp + "_" + role] = {
                'msg_id': msg_id,
                'status': 'Sent',
                'date': today_str
            }
        else:
            print(f"  [!] HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as ex:
        print(f"  [!] Error sending to {e['email']}: {ex}")

    time.sleep(2)

print(f"\nDispatched {len(dispatched_records)}/10 employee referral DMs!")

# Update Google Sheets & local CSV
rows = []
if os.path.exists(LOCAL_CSV):
    with open(LOCAL_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

for j in jobs:
    comp = j["company"]
    role = j["role_title"]
    key = comp + "_" + role
    if key in dispatched_records:
        rec = dispatched_records[key]
        for r in rows:
            if r.get("Company") == comp and r.get("Job Title") == role:
                r["DM 1 Status"] = "Sent"
                r["DM 1 Date"] = rec["date"]
                r["Notes"] = (r.get("Notes", "") + f" | DM 1 sent (MsgID: {rec['msg_id']})").strip(" | ")
                break

fieldnames = list(rows[0].keys()) if rows else []
with open(LOCAL_CSV, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r.get(k, '') for k in fieldnames})

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

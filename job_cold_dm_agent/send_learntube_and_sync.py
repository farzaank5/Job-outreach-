import os, sys, json, base64, requests, time, csv, datetime
from email.message import EmailMessage
from google.oauth2.credentials import Credentials

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from drive_csv_tracker import LOCAL_CSV, COLUMNS

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

# 1. Send LearnTube.ai
pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_resumes', "Farzaan's Resume 20.pdf")
with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

cfg = {
    'company': 'LearnTube.ai',
    'role_title': 'Associate Product Manager',
    'contact_name': 'Shubham',
    'email': 'shubham@learntube.ai',
    'experience_domain': 'AI ed-tech products, learner engagement optimization, and adaptive modules',
    'domain_focus': 'AI-powered edutainment, bite-sized learning courses, and user retention loops',
    'jd_skills': 'ed-tech user discovery, prototype delivery, retention experiments, and sprint management',
    'achievement': 'piloted an AI learning prototype with 120 students across 5 schools achieving 78% full-session completion, and drove delivery of an AI Companion reaching 90% organizational adoption'
}

first_name = 'Shubham'
subject = 'LearnTube.ai Associate Product Manager – quick question'

p1 = f"Hi {first_name},"
p2 = "Hope your week is going well."
p3 = f"I am an Associate Product Manager with 1.5+ years of experience across {cfg['experience_domain']}."
p4 = f"I came across the {cfg['role_title']} opening at {cfg['company']} and was particularly drawn to your team's expansion in {cfg['domain_focus']}. I would value your perspective on the team's roadmap."
p5 = f"Your team is looking for proven expertise in {cfg['jd_skills']}. In my recent work, I {cfg['achievement']}."
p6 = "I have attached my tailored 1-page resume for your review. Would you be open to taking a quick look, or pointing me to the right person for a referral?"
p7 = "No worries if it's not a fit right now."
sign_off = "Best regards,\nFarzaan Khan"

body_text = f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}\n\n{p5}\n\n{p6}\n\n{p7}\n\n{sign_off}"

msg = EmailMessage()
msg['To'] = cfg['email']
msg['Subject'] = subject
msg['From'] = 'me'
msg.set_content(body_text, cte='8bit')

paras = [p1, p2, p3, p4, p5, p6, p7, "Best regards,<br>Farzaan Khan"]
inner = "".join([f'<p style="margin: 0 0 16px 0; line-height: 1.5; font-size: 14px; color: #222;">{p}</p>' for p in paras])
html_body = f'<div dir="ltr">{inner}</div>'
msg.add_alternative(html_body, subtype='html', cte='8bit')
msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename="Farzaan's Resume 20.pdf")

raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

resp = requests.post(
    'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
    headers=headers,
    json={'raw': raw_msg},
    timeout=45
)
learntube_msg_id = resp.json().get('id')
print(f"LearnTube.ai dispatch status: {resp.status_code}, MsgID: {learntube_msg_id}")

# 2. Comprehensive Sync of all 10 roles
dispatched_all = [
    {
        'company': 'Stable Money', 'role': 'Associate Product Manager – Platform Products',
        'name': 'Saurabh Jain', 'contact_role': 'Co-Founder', 'email': 'saurabh@stablemoney.in',
        'doc_url': 'https://docs.google.com/document/d/1yGpdhawztS_7TQHCFGGR40oPQm438lA-Q1uLVplIrZs/edit',
        'resume_name': "Farzaan's Resume 14", 'msg_id': '1a1e8e7c04acebb6'
    },
    {
        'company': 'Weekday', 'role': "Founder's Office",
        'name': 'Amit Singh', 'contact_role': 'CEO & Co-Founder', 'email': 'amit@weekday.works',
        'doc_url': 'https://docs.google.com/document/d/1dyhuSxZA-LGSyPoG5Woz5UsizG_bYdhUaRavwsD_Vmk/edit',
        'resume_name': "Farzaan's Resume 15", 'msg_id': '1a1e8e7f2a844267'
    },
    {
        'company': 'Dozee', 'role': 'Associate Product Manager',
        'name': 'Mudit Dandwate', 'contact_role': 'Co-Founder', 'email': 'mudit@dozee.health',
        'doc_url': 'https://docs.google.com/document/d/1OtaDEkyXqruDOBm1OM4aJ6L9Wb_NXf030pMDHs2G9ro/edit',
        'resume_name': "Farzaan's Resume 16", 'msg_id': '1a1e8e81c7d57ca6'
    },
    {
        'company': 'Karya', 'role': 'Associate Product Manager',
        'name': 'Manu Chopra', 'contact_role': 'CEO', 'email': 'manu@karya.in',
        'doc_url': 'https://docs.google.com/document/d/13s5PxwLtzrKPa42I1BW2CewxwT3CKu0aunDBx3FjM7Q/edit',
        'resume_name': "Farzaan's Resume 17", 'msg_id': '1a1e8e8531347220'
    },
    {
        'company': 'Emergence AI', 'role': 'Product Owner (India Pod)',
        'name': 'Satya', 'contact_role': 'Head of Product', 'email': 'satya@emergence.ai',
        'doc_url': 'https://docs.google.com/document/d/1Dr4andyni7LlbS74peX5NRk0hNREvB3Dmvt3w2s4JU4/edit',
        'resume_name': "Farzaan's Resume 18", 'msg_id': '1a1e8e8893725549'
    },
    {
        'company': 'ToolJet', 'role': 'Associate Product Manager (Technical)',
        'name': 'Navaneeth PK', 'contact_role': 'CEO', 'email': 'navaneeth@tooljet.com',
        'doc_url': 'https://docs.google.com/document/d/1tpwd91MmGhAyHHCYt2QGCAECqxEzUYMzQ3hRKHQ-rrE/edit',
        'resume_name': "Farzaan's Resume 19", 'msg_id': '1a1e8e8b96ac9067'
    },
    {
        'company': 'LearnTube.ai', 'role': 'Associate Product Manager',
        'name': 'Shubham', 'contact_role': 'Founder', 'email': 'shubham@learntube.ai',
        'doc_url': 'https://docs.google.com/document/d/1sXWlHoesTSF61h9X3sN_OpYLrGzqOsxr46aZ6EhcTok/edit',
        'resume_name': "Farzaan's Resume 20", 'msg_id': learntube_msg_id
    },
    {
        'company': 'Karya', 'role': "Associate – Founder's Office",
        'name': 'Manu Chopra', 'contact_role': 'CEO', 'email': 'manu@karya.in',
        'doc_url': 'https://docs.google.com/document/d/153AALKFHWSa2lJ53wRIxJ9wJXRhe2YVj2NZdCbt2KKE/edit',
        'resume_name': "Farzaan's Resume 21", 'msg_id': '1a1e8ea11275f67c'
    },
    {
        'company': 'Spring Street', 'role': 'Associate Product Manager',
        'name': 'Founder', 'contact_role': 'Founding Team', 'email': 'founder@springstreet.in',
        'doc_url': 'https://docs.google.com/document/d/1ic5mPa0P63PcSzIABxqXieF-dPM6L7eLzJINRTk0fL8/edit',
        'resume_name': "Farzaan's Resume 22", 'msg_id': '1a1e8eafe43aecf2'
    },
    {
        'company': 'Quros Tech', 'role': 'Associate Product Manager',
        'name': 'Founder', 'contact_role': 'Founding Team', 'email': 'founder@quros.in',
        'doc_url': 'https://docs.google.com/document/d/18p34BKarSozJ1DXBZK_0mMmZ53SMtpa2cAixLS4TxGU/edit',
        'resume_name': "Farzaan's Resume 23", 'msg_id': '1a1e8eb3938d67ff'
    }
]

today_str = datetime.date.today().strftime('%Y-%m-%d')
follow_up_str = (datetime.date.today() + datetime.timedelta(days=4)).strftime('%Y-%m-%d')

rows = []
if os.path.exists(LOCAL_CSV):
    with open(LOCAL_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

for item in dispatched_all:
    found = False
    for r in rows:
        if r.get('Company') == item['company'] and r.get('Job Title') == item['role']:
            r['Hiring Manager'] = item['name']
            r['Manager Role'] = item['contact_role']
            r['Contact Email'] = item['email']
            r['Email Subject'] = f"{item['company']} {item['role']} – quick question"[:50]
            r['TAILORED RESUME LINK'] = item['doc_url']
            r['Resume Name'] = item['resume_name']
            r['Email Status'] = 'Sent'
            r['Date Sent'] = today_str
            r['Follow-up Date'] = follow_up_str
            r['Status'] = 'Sent'
            r['Reply Status'] = 'Awaiting Reply'
            r['Notes'] = f"Sent tailored 1-page resume ({item['resume_name']}). Gmail MsgID: {item['msg_id']}"
            found = True
            break
    if not found:
        new_row = {col: '' for col in COLUMNS}
        new_row['Date Added'] = today_str
        new_row['Company'] = item['company']
        new_row['Job Title'] = item['role']
        new_row['Hiring Manager'] = item['name']
        new_row['Manager Role'] = item['contact_role']
        new_row['Contact Email'] = item['email']
        new_row['Email Subject'] = f"{item['company']} {item['role']} – quick question"[:50]
        new_row['TAILORED RESUME LINK'] = item['doc_url']
        new_row['Resume Name'] = item['resume_name']
        new_row['Email Status'] = 'Sent'
        new_row['Date Sent'] = today_str
        new_row['Follow-up Date'] = follow_up_str
        new_row['Status'] = 'Sent'
        new_row['Reply Status'] = 'Awaiting Reply'
        new_row['Notes'] = f"Sent tailored 1-page resume ({item['resume_name']}). Gmail MsgID: {item['msg_id']}"
        rows.append(new_row)

with open(LOCAL_CSV, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    for r in rows:
        writer.writerow({col: r.get(col, '') for col in COLUMNS})

print(f"Updated local tracker CSV with all 10 entries.")

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

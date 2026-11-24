import os, sys, datetime, json, base64, time
import requests
from email.message import EmailMessage
from google.oauth2.credentials import Credentials

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from google_services import GoogleWorkspaceManager
from outreach_pipeline import extract_first_name
from drive_csv_tracker import LOCAL_CSV, COLUMNS
from resume_engine import get_next_resume_number

BASE_DOC_ID = "14-IiDD5SaYRmr-yQxEaHE1Q8K7mbuSe6AOs4iqdq24k"
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
SPREADSHEET_ID = '1_SkccwnnUf7ktv3w7VNRBUoJTW8HArD9gFppAOmrdHE'

manager = GoogleWorkspaceManager()

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

# Specification of 10 roles with tailored configurations
roles_config = [
    {
        'company': 'Enterpret',
        'role_title': 'Founder’s Office: Revenue Operations & Systems',
        'contact_name': 'Adarsh Pk',
        'contact_role': 'Head of Talent and People Ops',
        'email': 'adarsh@enterpret.com',
        'domain_focus': 'revenue workflows, CRM integrations, and AI agent architectures',
        'experience_domain': 'AI automation workflows, integrations, and startup operations',
        'jd_skills': 'automated workflow pipelines, CRM system handoffs, and SQL-driven metrics',
        'achievement': 'built 30+ automated workflow systems saving 200+ hours/month, cutting operational overhead 30%, and led cross-functional discovery working directly with founders',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager & Operations Specialist with 1.5+ years of experience building AI automation workflows, systems integrations, and operational tools. Built 30+ automated workflows saving 200+ hours/month and cut operational overhead by 30%. Comfortable partnering with founders, managing cross-functional handoffs, and writing engineering-ready PRDs.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Owned operational systems, workflow automations, and feature roadmaps for an AI-powered SaaS platform, partnering directly with founders on cross-functional alignment.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Defined clear system specifications, API handoff documentation, and metrics tracking dashboards, translating operational pain points into prioritized engineering sprints."
        },
        'bold_phrases': ["AI automation workflows", "30+ automated workflows", "200+ hours/month", "30%", "PRDs", "cross-functional", "Built", "Owned"]
    },
    {
        'company': 'Supernova AI',
        'role_title': 'Associate Product Manager (Acads)',
        'contact_name': 'Luke Zapart',
        'contact_role': 'CEO / Founder',
        'email': 'luke@supernova.ai',
        'domain_focus': 'AI-driven language copilot and adaptive speech learning loops',
        'experience_domain': 'AI ed-tech products, speech recognition, and conversational companions',
        'jd_skills': 'speech AI prototype delivery, user interview synthesis, and feature adoption',
        'achievement': 'interviewed 60+ users to shape AI learning modules, piloted a speech recognition edutainment prototype with 78% session completion, and drove delivery of an AI Companion reaching 90% adoption',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience building AI products in ed-tech and conversational AI. Shipped an AI Companion feature reaching 90% adoption, prototyped an AI speech recognition learning product with 78% completion across schools, and interviewed 60+ users to translate pain points into crisp PRDs.",
            "Led 0-to-1 product discovery for multimodal AI search and learning models, mapping complex AI capabilities into clear PRDs, wireframes, and workflows that supported a $7M funding round.":
            "Interviewed 60+ teachers and students across Tier 1-3 markets to shape AI learning roadmaps, requirements, and pedagogy feature priorities.",
            "Drove delivery of a core AI Companion feature: coordinated cross-functional stakeholders, ran sprint planning and tracked milestones. Also built 10 AI tools that cut manual effort by 60% and reached 90% adoption within the organisation.":
            "Shipped a core AI Companion feature reaching 90% adoption within the organization, managing cross-functional milestones and sprint execution."
        },
        'bold_phrases': ["AI Companion feature", "90% adoption", "AI speech recognition", "78% completion", "60+ users", "PRDs", "Shipped"]
    },
    {
        'company': 'Spacewire Tech',
        'role_title': 'Associate Product Manager – Growth & Monetization',
        'contact_name': 'Founding Team',
        'contact_role': 'Head of Product',
        'email': 'careers@spacewire.tech',
        'domain_focus': 'subscription conversion, onboarding optimization, and paywall experiments for Indian mobile users',
        'experience_domain': 'conversion rate optimization (CRO), user journeys, and funnel metrics',
        'jd_skills': 'funnel drop-off reduction, paywall A/B testing, and checkout optimization',
        'achievement': 'raised overall conversion 35%+, cut bounce rate 20%, and lifted checkout completion 15% through rigorous funnel experimentation, pricing tests, and user behavior analysis',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience in product growth, conversion rate optimization (CRO), and user funnel analytics. Raised overall conversion 35%+, cut bounce rate 20%, and lifted checkout completion 15% across e-commerce platforms. Skilled in A/B testing, Mixpanel, and user journey optimization.",
            "Ran conversion-funnel experiments across Shopify stores, looking at drop-off points, activation metrics and checkout behavior to find where buyers were leaving and fix it.":
            "Ran conversion-funnel experiments across user funnels, analyzing drop-off points, activation metrics, and checkout behavior to eliminate conversion friction.",
            "Raised overall conversion 35%+, cut bounce rate 20% and lifted checkout completion 15% by optimizing the pricing page, testing CTAs and redesigning the checkout flow.":
            "Raised overall conversion 35%+, cut bounce rate 20%, and lifted checkout completion 15% by optimizing pricing displays, testing CTAs, and redesigning payment flows."
        },
        'bold_phrases': ["conversion 35%+", "cut bounce rate 20%", "checkout completion 15%", "A/B testing", "Mixpanel", "Raised", "Ran"]
    },
    {
        'company': 'Pronto',
        'role_title': 'Associate Product Manager – Supply',
        'contact_name': 'Supply Product Lead',
        'contact_role': 'Head of Supply Product',
        'email': 'talent@pronto.co.in',
        'domain_focus': 'supply-side operational logistics and internal partner tooling',
        'experience_domain': 'operations workflows, internal tooling, and agile execution',
        'jd_skills': 'workflow automation, SLA tracking, PRDs, and SQL analytics',
        'achievement': 'built 30+ automated workflow pipelines saving 200+ hours/month, managed operator tooling for hotel management SaaS (27 active listings, 100+ bookings), and authored engineering specs',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience building operational workflows, internal tools, and automated system pipelines. Built 30+ workflow automations saving 200+ hours/month, led discovery for operator SaaS supporting ₹1M+ GBV, and managed engineering backlogs in Jira.",
            "SR Group Stays (Hotel Management SaaS) : Led discovery and development of an internal hotel management SaaS, turning operator workflows into listing, booking and payment features. In 2 months it supported 27 active listings, 100+ bookings and ₹1M+ in gross booking value.":
            "SR Group Stays (Operator Management SaaS): Led discovery and development of an internal operator SaaS, turning partner workflows into listing, booking, and payment modules, supporting 27 active listings and ₹1M+ GBV in 2 months."
        },
        'bold_phrases': ["30+ workflow automations", "200+ hours/month", "operator SaaS", "₹1M+ GBV", "PRDs", "Jira", "Built", "Led"]
    },
    {
        'company': 'Binocs',
        'role_title': 'Associate Product Manager',
        'contact_name': 'Shilpi Shrivastava',
        'contact_role': 'HR Manager',
        'email': 'shilpi@binocs.co',
        'domain_focus': 'AI-driven portfolio tracking and financial workflow management',
        'experience_domain': 'fintech discovery, financial SaaS, and API workflow automation',
        'jd_skills': 'customer discovery interviews, user journey prioritization, and spec-to-release execution',
        'achievement': 'led product discovery for a fintech personal finance MVP based on 25 user interviews, designed listing and payment workflows, and authored engineering PRDs and acceptance criteria',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience across fintech products and AI workflow automations. Led product discovery for a fintech MVP based on 25 user interviews, built 30+ automated workflow pipelines, and authored technical PRDs and user stories.",
            "FINOVA (Fintech & Personal Finance App): Independently led product discovery for a fintech MVP: prioritized the core user journeys, reviewed wireframes and defined a launch strategy for Tier-2 users, based on 25 user interviews..":
            "FINOVA (Fintech & Personal Finance App): Independently led product discovery for a fintech MVP, prioritizing core user journeys, reviewing Figma wireframes, and defining a launch strategy based on 25 user interviews."
        },
        'bold_phrases': ["fintech MVP", "25 user interviews", "core user journeys", "30+ automated workflow pipelines", "PRDs", "Led", "Built"]
    },
    {
        'company': 'BitScale',
        'role_title': 'Associate Product Manager - AI',
        'contact_name': 'Nazar E Moin Sheikh',
        'contact_role': 'Founding Product Designer',
        'email': 'nazar@bitscale.ai',
        'domain_focus': 'signal-first sales intelligence agents and autonomous B2B GTM workflows',
        'experience_domain': 'AI agent workflows, LLM prompt engineering, and rapid product prototyping',
        'jd_skills': 'autonomous AI workflow design, prompt engineering, and agile sprint delivery',
        'achievement': 'architected and scaled 30+ AI automation workflows cutting operating overhead 30% and adding ₹500K+ in profit, while shipping a core AI Companion feature reaching 90% adoption',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager - AI with 1.5+ years of experience building autonomous AI workflows and LLM applications. Built and scaled 30+ AI automation workflows saving 200+ hours/month, shipped an AI Companion feature reaching 90% adoption, and collaborated directly with founders from user discovery to release.",
            "Built and scaled 30+ AI automation workflows across product and operations. They save 200+ hours/month, cut operating overhead 30% against the pre-automation baseline, lifted margins 18% and added ₹500K+ in incremental profit.":
            "Built and scaled 30+ AI automation workflows leveraging LLMs, prompt engineering, and APIs, saving 200+ hours/month, reducing overhead 30%, and lifting margins 18%."
        },
        'bold_phrases': ["autonomous AI workflows", "30+ AI automation workflows", "200+ hours/month", "90% adoption", "LLMs", "Built", "Shipped"]
    },
    {
        'company': 'Troopod',
        'role_title': 'Founder\'s Office (Growth & Operations)',
        'contact_name': 'Juhi Jain',
        'contact_role': 'Associate Director - Business',
        'email': 'juhi@troopod.io',
        'domain_focus': 'AI-native website growth engines, landing page performance, and D2C brand conversion',
        'experience_domain': 'Shopify e-commerce CRO, founder strategy, and growth experiments',
        'jd_skills': 'conversion optimization, checkout flow redesign, and rapid cross-functional experimentation',
        'achievement': 'raised overall conversion 35%+, cut bounce rate 20%, lifted checkout completion 15%, and scaled ad CTR from 1.8% to 2.9% across 12 e-commerce stores contributing to ₹2M revenue',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience partnering directly with founders on e-commerce CRO and automated workflows. Raised conversion 35%+, cut bounce rate 20%, and lifted checkout completion 15% across Shopify stores, generating ₹2M in annual store revenue.",
            "Grew several e-commerce stores through experiments, conversion rate optimization (CRO) and customer-feedback analysis. Ad CTR rose from 1.8% to 2.9% across 12 stores, contributing to ₹2M in annual store revenue.":
            "Grew several e-commerce stores through CRO experiments and customer feedback, lifting ad CTR from 1.8% to 2.9% across 12 stores and generating ₹2M in revenue."
        },
        'bold_phrases': ["conversion 35%+", "checkout completion 15%", "₹2M in annual store revenue", "1.8% to 2.9%", "Shopify", "Raised", "Grew"]
    },
    {
        'company': 'Catalogus',
        'role_title': 'Product Manager',
        'contact_name': 'Vipin Kumar Singh',
        'contact_role': 'Co-Founder & CEO',
        'email': 'vipin@catalogus.ai',
        'domain_focus': 'AI-enabled e-commerce cataloging and product experience management',
        'experience_domain': 'e-commerce SaaS, product discovery, and spec-to-release execution',
        'jd_skills': 'customer discovery, PRDs and acceptance criteria, and agile backlog prioritization',
        'achievement': 'owned product execution from spec to release for an AI-powered Shopify SaaS, authoring PRDs and user stories to align engineering with business goals',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Product Manager with 1.5+ years of experience building e-commerce SaaS platforms and AI automation workflows. Owned product execution from spec to release for an AI Shopify SaaS, authored engineering PRDs and user stories, and collaborated closely with founders to validate product-market fit.",
            "Owned product strategy, roadmap and GTM for an AI-powered Shopify SaaS. Ran user discovery, competitive analysis and feature prioritization to validate product-market fit.":
            "Owned product strategy and GTM for an AI-powered e-commerce SaaS, running customer discovery and feature prioritization to validate product-market fit."
        },
        'bold_phrases': ["e-commerce SaaS", "PRDs", "user stories", "product-market fit", "Shopify", "Owned", "Ran"]
    },
    {
        'company': 'GreyOrange',
        'role_title': 'Associate Product Manager',
        'contact_name': 'Suryansh Agrawal',
        'contact_role': 'Senior Product Manager',
        'email': 'suryansh.agrawal@greyorange.com',
        'domain_focus': 'fulfillment automation, warehouse software systems, and retail supply chain orchestration',
        'experience_domain': 'fulfillment workflows, automation pipelines, and agile execution',
        'jd_skills': 'PRD documentation, Jira sprint backlog management, and metrics-driven prioritization',
        'achievement': 'architected 30+ automated workflow pipelines saving 200+ hours/month, managed operator modules in internal SaaS (100+ bookings), and authored user stories and acceptance criteria',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience in product execution, workflow automation, and agile delivery. Built 30+ automated workflow systems saving 200+ hours/month, authored detailed PRDs and user stories in Jira, and collaborated cross-functionally with engineering and design.",
            "Ran product execution from spec to release: wrote PRDs and user stories, set acceptance criteria and managed the backlog so engineering work matched business goals.":
            "Ran product execution from spec to release: authored PRDs, user stories, and acceptance criteria in Jira to ensure engineering deliverables met business goals."
        },
        'bold_phrases': ["PRDs", "user stories", "Jira", "30+ automated workflow systems", "200+ hours/month", "Ran", "Built"]
    },
    {
        'company': 'Spaceout Agency',
        'role_title': 'Founder\'s Office Associate',
        'contact_name': 'Rajat',
        'contact_role': 'Founder & CEO',
        'email': 'founders@spaceout.agency',
        'domain_focus': 'outbound growth infrastructure, B2B pipeline automation, and startup operations',
        'experience_domain': 'workflow automations, cross-functional operations, and founder collaboration',
        'jd_skills': 'operational systems, process automation, and high-agency execution',
        'achievement': 'built and scaled 30+ automated workflows saving 200+ hours/month, cut operating overhead 30%, and worked directly with founders on discovery, roadmaps, and execution',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Founder's Office & Operations Associate with 1.5+ years of experience partnering directly with founders on automation workflows and business operations. Built 30+ automated workflow pipelines saving 200+ hours/month and cutting operational overhead 30%. High agency, bias for action, and hands-on execution.",
            "Owned product strategy, roadmap and GTM for an AI-powered Shopify SaaS. Ran user discovery, competitive analysis and feature prioritization to validate product-market fit.":
            "Partnered directly with founders on business strategy, operational workflows, and feature prioritization to drive measurable business outcomes."
        },
        'bold_phrases': ["30+ automated workflow pipelines", "200+ hours/month", "overhead 30%", "High agency", "Partnered", "Built"]
    }
]

today_str = datetime.date.today().strftime('%Y-%m-%d')
follow_up_str = (datetime.date.today() + datetime.timedelta(days=6)).strftime('%Y-%m-%d')

sent_dict = {}

# Execute tailoring, PDF generation, and email dispatch sequentially
for idx, cfg in enumerate(roles_config):
    resume_num = get_next_resume_number(manager)
    resume_name = f"Farzaan's Resume {resume_num}"
    print(f"\n[{idx+1}/10] Generating Tailored Resume: {resume_name} for {cfg['company']}...")
    
    try:
        resume_res = manager.create_numbered_tailored_resume(
            base_document_id=BASE_DOC_ID,
            resume_number=resume_num,
            replacements=cfg['replacements'],
            bold_phrases=cfg['bold_phrases']
        )
        pdf_path = resume_res['pdf_path']
        doc_url = resume_res['tailored_doc_url']
        print(f"  -> Generated: {resume_name} | Doc: {doc_url} | PDF: {pdf_path}")
    except Exception as e:
        print(f"  [!] Tailoring error for {cfg['company']}: {e}")
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_resumes', "Farzaan's Resume 2.pdf")
        doc_url = "https://docs.google.com/document/d/14-IiDD5SaYRmr-yQxEaHE1Q8K7mbuSe6AOs4iqdq24k/edit"

    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    first_name = extract_first_name(cfg['contact_name'], cfg['email'])
    subject = f"{cfg['company']} {cfg['role_title']} – quick question"[:50]
    
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
    
    html_paras = [f'<p style="margin: 0 0 16px 0; line-height: 1.5; font-size: 14px; color: #222;">{p}</p>' for p in [p1, p2, p3, p4, p5, p6, p7, "Best regards,<br>Farzaan Khan"]]
    html_body = f'<div dir="ltr">{"".join(html_paras)}</div>'
    msg.add_alternative(html_body, subtype='html', cte='8bit')
    msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"{resume_name}.pdf")
    
    raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    
    print(f"  Sending email to {cfg['contact_name']} ({cfg['email']})...")
    try:
        resp = requests.post(
            'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
            headers=headers,
            json={'raw': raw_msg},
            timeout=45
        )
        if resp.status_code == 200:
            msg_id = resp.json().get('id')
            print(f"  -> SUCCESS! Email dispatched. Gmail MsgID: {msg_id}")
            sent_dict[cfg['company']] = {
                'email': cfg['email'],
                'name': cfg['contact_name'],
                'role': cfg['contact_role'],
                'subject': subject,
                'msg_id': msg_id,
                'doc_url': doc_url,
                'resume_name': resume_name,
                'status': 'Sent'
            }
        else:
            print(f"  [!] HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"  [!] Dispatch error for {cfg['email']}: {e}")
    time.sleep(1)

print(f"\nDispatched {len(sent_dict)}/10 tailored outreach emails!")

# Update LOCAL_CSV
rows = []
with open(LOCAL_CSV, mode='r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        comp = r.get('Company')
        if comp in sent_dict:
            s_info = sent_dict[comp]
            r['Hiring Manager'] = s_info['name']
            r['Manager Role'] = s_info['role']
            r['Contact Email'] = s_info['email']
            r['Email Subject'] = s_info['subject']
            r['TAILORED RESUME LINK'] = s_info['doc_url']
            r['Resume Name'] = s_info['resume_name']
            r['Email Status'] = 'Sent'
            r['Date Sent'] = today_str
            r['Follow-up Date'] = follow_up_str
            r['Status'] = 'Sent'
            r['Reply Status'] = 'Awaiting Reply'
            r['Notes'] = f"Sent tailored 1-page resume ({s_info['resume_name']}). Gmail MsgID: {s_info['msg_id']}"
        rows.append(r)

with open(LOCAL_CSV, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    for r in rows:
        writer.writerow({col: r.get(col, '') for col in COLUMNS})

print("Updated local tracker CSV.")

# Upload CSV to Google Drive
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

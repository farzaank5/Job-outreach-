import os, sys, datetime, json, base64, time
import requests
from email.message import EmailMessage
from google.oauth2.credentials import Credentials

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from google_services import GoogleWorkspaceManager
from outreach_pipeline import extract_first_name
from drive_csv_tracker import LOCAL_CSV, COLUMNS
from resume_engine import get_next_resume_number, set_pdf_metadata

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

roles_config = [
    {
        'company': 'Stable Money',
        'role_title': 'Associate Product Manager – Platform Products',
        'contact_name': 'Saurabh Jain',
        'contact_role': 'Co-Founder',
        'email': 'saurabh@stablemoney.in',
        'domain_focus': 'fixed-income marketplace infrastructure and high-traffic investor conversion funnels',
        'experience_domain': 'fintech platforms, user onboarding flows, and conversion rate optimization',
        'jd_skills': 'shipping core features to production, conversion funnel experiments, and PRD ownership',
        'achievement': 'lifted checkout completion 15% and raised conversion 35%+ through funnel experimentation, while leading product discovery for a fintech MVP based on 25 user interviews',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience across fintech discovery and conversion-rate optimization. Led product discovery for a fintech MVP and raised conversion 35%+ across digital funnels. Adept at shipping core platform features, writing clear PRDs, and running user-centric experiments.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Owned product execution for consumer and SaaS platforms: translated user drop-off insights into PRDs, defined sprint backlogs, and aligned cross-functional teams to launch high-conversion platform features.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Conducted user research and behavioral analysis across financial funnels, turning checkout analytics into actionable roadmap items and rigorous A/B experiments."
        },
        'bold_phrases': ["fintech discovery", "conversion 35%+", "fintech MVP", "clear PRDs", "A/B experiments", "checkout analytics"]
    },
    {
        'company': 'Weekday',
        'role_title': "Founder's Office",
        'contact_name': 'Amit Singh',
        'contact_role': 'CEO & Co-Founder',
        'email': 'amit@weekday.works',
        'domain_focus': 'AI-native recruiting automation and talent database workflows',
        'experience_domain': 'AI automation workflows, 0-to-1 startup operations, and founder strategy',
        'jd_skills': 'high-agency execution, cross-functional problem solving, and autonomous workflows',
        'achievement': 'built 30+ AI automation workflows saving 200+ hours/month, cut operating overhead 30%, and worked directly alongside founders on roadmap validation and GTM strategy',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "High-agency Founder's Office Associate & APM with 1.5+ years of experience partnering directly with founders on AI automations and product operations. Built 30+ workflows saving 200+ hours/month, cut overhead 30%, and validated 0-to-1 GTM strategies in fast-paced startup environments.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Partnered directly with founders across product strategy, operations, and GTM: owned roadmap priorities, unblocked cross-functional bottlenecks, and executed high-priority company initiatives.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Diagnosed operational inefficiencies and user pain points, deploying automated tools and streamlined processes that cut manual work by 60% with 90% team adoption."
        },
        'bold_phrases': ["High-agency Founder's Office", "partnering directly with founders", "30+ workflows", "saving 200+ hours/month", "cut overhead 30%", "GTM strategies"]
    },
    {
        'company': 'Dozee',
        'role_title': 'Associate Product Manager',
        'contact_name': 'Mudit Dandwate',
        'contact_role': 'Co-Founder',
        'email': 'mudit@dozee.health',
        'domain_focus': 'AI-powered contactless patient monitoring and clinical alert intelligence',
        'experience_domain': 'AI companion products, user research synthesis, and rapid prototyping',
        'jd_skills': 'customer interviews, requirement gathering, and cross-functional agile delivery',
        'achievement': 'interviewed 60+ users to extract product insights, prototyped an AI system with 78% completion across pilots, and coordinated sprint planning for core AI features reaching 90% adoption',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience driving AI product discovery, customer interviews, and agile delivery. Interviewed 60+ stakeholders to shape AI feature requirements and delivered prototypes reaching 78% pilot completion. Experienced in PRDs, user stories, and cross-functional sprints.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Managed sprint cycles, backlog grooming, and acceptance criteria for AI products, coordinating cross-functional engineering and design pods to ship reliable user-facing features.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Transformed user research and customer interviews into detailed PRDs, user flows, and acceptance criteria, ensuring tight alignment between clinical/user needs and engineering delivery."
        },
        'bold_phrases': ["AI product discovery", "customer interviews", "Interviewed 60+ stakeholders", "78% pilot completion", "PRDs, user stories", "cross-functional sprints"]
    },
    {
        'company': 'Karya',
        'role_title': 'Associate Product Manager',
        'contact_name': 'Manu Chopra',
        'contact_role': 'CEO',
        'email': 'manu@karya.in',
        'domain_focus': 'ethical AI data platforms and speech dataset generation across India',
        'experience_domain': 'speech AI systems, multi-tier user interviews, and agile product lifecycles',
        'jd_skills': 'PRD translation, sprint planning, Jira management, and end-to-end product delivery',
        'achievement': 'piloted an AI speech recognition prototype with 120 users achieving 78% completion, interviewed 60+ stakeholders across Tier-1/2/3 markets, and guided cross-functional sprints for an AI feature with 90% adoption',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience shipping AI speech products and conducting field research across Tier-1, 2, and 3 markets. Built speech prototypes with 78% pilot completion and coordinated cross-functional sprints for an AI Companion reaching 90% adoption.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Ran sprint planning, standups, and backlog prioritization using Jira and Notion, steering engineering and design pods through the full lifecycle of data-driven AI learning products.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Translated field interviews and ambiguous user requirements into actionable PRDs, user stories, and acceptance criteria, optimizing usability for diverse user demographics."
        },
        'bold_phrases': ["AI speech products", "Tier-1, 2, and 3 markets", "speech prototypes", "78% pilot completion", "90% adoption", "Jira and Notion", "PRDs, user stories"]
    },
    {
        'company': 'Emergence AI',
        'role_title': 'Product Owner (India Pod)',
        'contact_name': 'Satya',
        'contact_role': 'Head of Product',
        'email': 'satya@emergence.ai',
        'domain_focus': 'autonomous multi-agent AI systems and enterprise agent orchestration',
        'experience_domain': 'AI automation workflows, LLM prompt engineering, and agile pod delivery',
        'jd_skills': 'defining specs for AI agents, maintaining evals/acceptance criteria, and sprint execution',
        'achievement': 'built 30+ automated AI workflow systems saving 200+ hours/month, created 10 internal AI tools with 90% adoption, and owned backlog execution and acceptance criteria across engineering pods',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Product Owner & APM with 1.5+ years of experience building with AI workflows, LLM applications, and agile engineering pods. Engineered 30+ automated workflows saving 200+ hours/month and built 10 AI tools reaching 90% organizational adoption. Skilled in writing evals, acceptance criteria, and clear specs.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Acted as the product link to engineering pods: translated customer signals into PRDs, defined strict acceptance criteria and evals for AI tools, and managed sprint delivery.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Designed prompt engineering workflows, system evaluations, and user acceptance tests, ensuring shipped AI agents met production benchmarks before deployment."
        },
        'bold_phrases': ["AI workflows", "LLM applications", "30+ automated workflows", "saving 200+ hours/month", "acceptance criteria and evals", "engineering pods"]
    },
    {
        'company': 'ToolJet',
        'role_title': 'Associate Product Manager (Technical)',
        'contact_name': 'Navaneeth PK',
        'contact_role': 'CEO',
        'email': 'navaneeth@tooljet.com',
        'domain_focus': 'open-source low-code/internal tool platforms and enterprise integrations',
        'experience_domain': 'B2B SaaS platforms, developer workflows, and system integrations',
        'jd_skills': 'technical PRDs, API integration workflows, database schemas, and feature backlog prioritization',
        'achievement': 'managed product execution for an AI SaaS from spec to release, built 30+ automation workflows cutting overhead 30%, and led technical discovery for an internal hotel management SaaS with 27 properties',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Technical Associate Product Manager with 1.5+ years of experience shipping SaaS products, API integrations, and workflow automation platforms. Led product discovery and delivery for internal SaaS tools handling ₹1M+ GBV. Skilled in technical PRDs, user stories, databases, and agile execution.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Spearheaded technical product execution: wrote architectural specs, managed API integrations, and guided engineering sprints to build internal tools and workflow systems.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Translated operator and developer workflows into detailed functional specifications, database logic, and acceptance criteria, validating usability prior to deployment."
        },
        'bold_phrases': ["Technical Associate Product Manager", "API integrations", "workflow automation platforms", "technical PRDs", "developer workflows", "acceptance criteria"]
    },
    {
        'company': 'LearnTube.ai',
        'role_title': 'Associate Product Manager',
        'contact_name': 'Shubham',
        'contact_role': 'Founder',
        'email': 'shubham@learntube.ai',
        'domain_focus': 'AI-powered edutainment, bite-sized learning courses, and user retention loops',
        'experience_domain': 'AI ed-tech products, learner engagement optimization, and adaptive modules',
        'jd_skills': 'ed-tech user discovery, prototype delivery, retention experiments, and sprint management',
        'achievement': 'piloted an AI learning prototype with 120 students across 5 schools achieving 78% full-session completion, and drove delivery of an AI Companion reaching 90% organizational adoption',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience building AI learning products and driving user engagement in ed-tech. Conducted 60+ user interviews to build AI edutainment prototypes with 78% completion, and shipped an AI Companion reaching 90% adoption. Experienced in retention and PRDs.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Ran sprint delivery and roadmap execution for interactive AI products: aligned design and engineering teams to iterate on gamified learning flows and adaptive learning modules.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Synthesized student and educator feedback into structured PRDs and acceptance criteria, prioritizing features that directly improved session completion and retention."
        },
        'bold_phrases': ["AI learning products", "60+ user interviews", "78% completion", "90% adoption", "gamified learning flows", "retention"]
    },
    {
        'company': 'Karya',
        'role_title': "Associate – Founder's Office",
        'contact_name': 'Manu Chopra',
        'contact_role': 'CEO',
        'email': 'manu@karya.in',
        'domain_focus': 'ethical AI data ecosystems, partner expansion, and rural economic empowerment',
        'experience_domain': '0-to-1 startup operations, founder collaboration, and workflow optimization',
        'jd_skills': 'high-agency problem solving, ambiguous cross-functional ownership, and analytical rigor',
        'achievement': 'built 30+ automated workflows saving 200+ hours/month and cutting overhead 30%, partnered directly with founders on roadmap priorities, and conducted 60+ user interviews across Tier-1/2/3 markets',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Resourceful Founder's Associate & APM with 1.5+ years of experience executing cross-functional initiatives and operational systems. Partnered directly with founders to validate roadmaps, built 30+ automated workflows saving 200+ hours/month, and led user discovery across Tier-1, 2, and 3 markets.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Operated across strategy, product, and operations to tackle high-priority ambiguous challenges, streamlining organizational workflows and cutting operational overhead by 30%.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Diagnosed complex operational and product bottlenecks, designing structured processes and automated tools that cut manual effort by 60% with 90% team adoption."
        },
        'bold_phrases': ["Resourceful Founder's Associate", "cross-functional initiatives", "Partnered directly with founders", "30+ automated workflows", "Tier-1, 2, and 3 markets", "cutting operational overhead by 30%"]
    },
    {
        'company': 'Spring Street',
        'role_title': 'Associate Product Manager',
        'contact_name': 'Founder',
        'contact_role': 'Founding Team',
        'email': 'founder@springstreet.in',
        'domain_focus': 'consumer-facing digital commerce and high-velocity product execution',
        'experience_domain': 'e-commerce product execution, conversion rate optimization, and PRD ownership',
        'jd_skills': 'cross-functional execution, conversion funnel analysis, user stories, and feature prioritization',
        'achievement': 'lifted checkout completion 15%, cut bounce rates 20%, and improved ad CTR from 1.8% to 2.9% across 12 stores contributing to ₹2M in revenue, while managing sprints and PRDs',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience driving e-commerce product growth, conversion funnel optimization, and agile delivery. Raised checkout completion 15% and cut bounce rates 20% across digital storefronts. Skilled in PRDs, user stories, and cross-functional execution.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Owned end-to-end product execution from spec to release: managed backlogs, prioritized features with founders, and ran sprint cycles to match business growth targets.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Analyzed customer drop-off data and activation metrics, writing comprehensive PRDs and running conversion experiments that added ₹2M in annual store revenue."
        },
        'bold_phrases': ["e-commerce product growth", "conversion funnel optimization", "Raised checkout completion 15%", "PRDs, user stories", "₹2M in annual store revenue"]
    },
    {
        'company': 'Quros Tech',
        'role_title': 'Associate Product Manager',
        'contact_name': 'Founder',
        'contact_role': 'Founding Team',
        'email': 'founder@quros.in',
        'domain_focus': 'end-to-end client product solutions, SaaS platforms, and digital transformation',
        'experience_domain': 'product discovery, client demos, PRDs, and cross-functional agile delivery',
        'jd_skills': 'client requirement gathering, functional documentation, sprint planning, and developer alignment',
        'achievement': 'led product discovery and execution for a SaaS platform turning operator workflows into booking/payment features (₹1M+ GBV), and built 30+ workflows saving 200+ hours/month',
        'replacements': {
            "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
            "Associate Product Manager with 1.5+ years of experience in product planning, client communication, and cross-functional execution. Led discovery and development for a hotel SaaS handling ₹1M+ GBV, and built 30+ workflows saving 200+ hours/month. Skilled in PRDs, client demos, and developer handoffs.",
            "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
            "Managed end-to-end product delivery with engineering and design pods: gathered client requirements, translated them into sprint stories, and conducted launch demos.",
            "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
            "Authored clear functional specifications, acceptance criteria, and workflow diagrams, ensuring seamless translation from business objectives to production software."
        },
        'bold_phrases': ["product planning, client communication", "hotel SaaS handling ₹1M+ GBV", "30+ workflows saving 200+ hours/month", "PRDs, client demos", "functional specifications"]
    }
]

def make_tailored_resume(cfg, resume_num):
    resume_name = f"Farzaan's Resume {resume_num}"
    print(f"\n[{resume_name}] Tailoring for {cfg['company']} ({cfg['role_title']})...")
    
    copy_resp = requests.post(
        f'https://www.googleapis.com/drive/v3/files/{BASE_DOC_ID}/copy',
        headers=headers,
        json={'name': resume_name},
        timeout=30
    )
    copy_resp.raise_for_status()
    new_doc_id = copy_resp.json()['id']
    
    requests_list = []
    for target, rep in cfg['replacements'].items():
        requests_list.append({
            'replaceAllText': {
                'containsText': {'text': target, 'matchCase': True},
                'replaceText': rep
            }
        })
        
    for phrase in cfg['bold_phrases']:
        requests_list.append({
            'updateTextStyle': {
                'textStyle': {'bold': True},
                'fields': 'bold',
                'range': {
                    'segmentId': ''
                }
            }
        })

    patch_resp = requests.post(
        f'https://docs.googleapis.com/v1/documents/{new_doc_id}:batchUpdate',
        headers=headers,
        json={'requests': requests_list},
        timeout=30
    )
    
    requests.post(
        f'https://www.googleapis.com/drive/v3/files/{new_doc_id}/permissions',
        headers=headers,
        json={'role': 'reader', 'type': 'anyone'},
        timeout=30
    )
    
    pdf_resp = requests.get(
        f'https://www.googleapis.com/drive/v3/files/{new_doc_id}/export?mimeType=application/pdf',
        headers={'Authorization': f'Bearer {creds.token}'},
        timeout=45
    )
    pdf_resp.raise_for_status()
    
    resumes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_resumes')
    os.makedirs(resumes_dir, exist_ok=True)
    pdf_path = os.path.join(resumes_dir, f"{resume_name}.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(pdf_resp.content)
        
    set_pdf_metadata(pdf_path, resume_name)
    doc_url = f"https://docs.google.com/document/d/{new_doc_id}/edit"
    return resume_name, doc_url, pdf_path

start_num = get_next_resume_number(manager)
today_str = datetime.date.today().strftime('%Y-%m-%d')
follow_up_str = (datetime.date.today() + datetime.timedelta(days=4)).strftime('%Y-%m-%d')

sent_dict = {}

for idx, cfg in enumerate(roles_config):
    resume_num = start_num + idx
    try:
        resume_name, doc_url, pdf_path = make_tailored_resume(cfg, resume_num)
        print(f"  -> Generated: {resume_name} | Doc: {doc_url}")
    except Exception as e:
        print(f"  [!] Tailoring error for {cfg['company']}: {e}")
        continue

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
            sent_dict[cfg['company'] + "_" + cfg['role_title']] = {
                'company': cfg['company'],
                'role': cfg['role_title'],
                'email': cfg['email'],
                'name': cfg['contact_name'],
                'contact_role': cfg['contact_role'],
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

# Update or append in LOCAL_CSV
rows = []
if os.path.exists(LOCAL_CSV):
    with open(LOCAL_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

for key, s_info in sent_dict.items():
    found = False
    for r in rows:
        if r.get('Company') == s_info['company'] and r.get('Job Title') == s_info['role']:
            r['Hiring Manager'] = s_info['name']
            r['Manager Role'] = s_info['contact_role']
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
            found = True
            break
    if not found:
        new_row = {col: '' for col in COLUMNS}
        new_row['Date Added'] = today_str
        new_row['Company'] = s_info['company']
        new_row['Job Title'] = s_info['role']
        new_row['Hiring Manager'] = s_info['name']
        new_row['Manager Role'] = s_info['contact_role']
        new_row['Contact Email'] = s_info['email']
        new_row['Email Subject'] = s_info['subject']
        new_row['TAILORED RESUME LINK'] = s_info['doc_url']
        new_row['Resume Name'] = s_info['resume_name']
        new_row['Email Status'] = 'Sent'
        new_row['Date Sent'] = today_str
        new_row['Follow-up Date'] = follow_up_str
        new_row['Status'] = 'Sent'
        new_row['Reply Status'] = 'Awaiting Reply'
        new_row['Notes'] = f"Sent tailored 1-page resume ({s_info['resume_name']}). Gmail MsgID: {s_info['msg_id']}"
        rows.append(new_row)

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

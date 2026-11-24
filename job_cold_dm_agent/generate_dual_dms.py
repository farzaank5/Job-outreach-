import os, sys, json, re

# Pre-checks: tailored resume references & drive links
jobs = [
    {
        "id": 1,
        "company": "Stable Money",
        "role_title": "Associate Product Manager – Platform Products",
        "job_url": "https://jobs.lever.co/stable-money1/86ef4b73-ba13-405e-8639-e57162f8972f",
        "resume_name": "Farzaan's Resume 14",
        "resume_link": "https://docs.google.com/document/d/1yGpdhawztS_7TQHCFGGR40oPQm438lA-Q1uLVplIrZs/edit",
        "employee": {
            "name": "Tarang Deep Goel",
            "first_name": "Tarang",
            "title": "Product Manager",
            "team": "Product",
            "email": "tarang@stablemoney.in",
            "profile_url": "https://linkedin.com/in/tarang-deep-goel-6198701a9",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Saurabh Jain",
            "first_name": "Saurabh",
            "title": "Co-Founder",
            "team": "Executive / Product",
            "email": "saurabh@stablemoney.in",
            "profile_url": "https://linkedin.com/in/saurabh-jain-56747b1b",
            "confidence": "High",
            "company_detail": "simplifying fixed-income investment access and fixed deposit discovery",
            "experience_domain": "fintech discovery and conversion optimization",
            "jd_needs": "own PRDs, run conversion experiments, and ship core platform features",
            "proof": "raised conversion 35%+ and lifted checkout completion 15% through funnel experiments while discovering user journeys for a fintech MVP",
            "team_impact": "streamline investor onboarding and improve conversion across your platform"
        }
    },
    {
        "id": 2,
        "company": "Weekday",
        "role_title": "Founder's Office",
        "job_url": "https://jobs.lever.co/weekdayworks/ab4b6fe9-eace-4635-8e46-20567faf7b51",
        "resume_name": "Farzaan's Resume 15",
        "resume_link": "https://docs.google.com/document/d/1dyhuSxZA-LGSyPoG5Woz5UsizG_bYdhUaRavwsD_Vmk/edit",
        "employee": {
            "name": "Rounak Agarwal",
            "first_name": "Rounak",
            "title": "Senior Software Engineer",
            "team": "Tech / Engineering",
            "email": "rounak.agarwal@weekday.works",
            "profile_url": "https://linkedin.com/in/rounak-agarwal",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Amit Singh",
            "first_name": "Amit",
            "title": "CEO & Co-Founder",
            "team": "Founder's Office",
            "email": "amit@weekday.works",
            "profile_url": "https://linkedin.com/in/amit-singh-weekday",
            "confidence": "High",
            "company_detail": "AI-native recruiting automation and talent database workflows",
            "experience_domain": "AI automation workflows and founder operations",
            "jd_needs": "high-agency problem solving, autonomous execution, and cross-functional momentum",
            "proof": "built 30+ automated workflows saving 200+ hours monthly, cut operating overhead 30%, and partnered directly with founders on GTM execution",
            "team_impact": "tackle ambiguous operational bottlenecks and free up leadership bandwidth"
        }
    },
    {
        "id": 3,
        "company": "Dozee",
        "role_title": "Associate Product Manager",
        "job_url": "https://jobs.lever.co/dozee/54cf50b2-c25d-412c-a8ce-a047884f378e",
        "resume_name": "Farzaan's Resume 16",
        "resume_link": "https://docs.google.com/document/d/1OtaDEkyXqruDOBm1OM4aJ6L9Wb_NXf030pMDHs2G9ro/edit",
        "employee": {
            "name": "Shalin Agrawal",
            "first_name": "Shalin",
            "title": "Product Manager",
            "team": "Product",
            "email": "shalin.agrawal@dozee.health",
            "profile_url": "https://linkedin.com/in/shalin-agrawal",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Mudit Dandwate",
            "first_name": "Mudit",
            "title": "Co-Founder & CEO",
            "team": "Executive / Product",
            "email": "mudit@dozee.health",
            "profile_url": "https://linkedin.com/in/mudit-dandwate-939a9539",
            "confidence": "High",
            "company_detail": "AI-powered contactless patient monitoring and early clinical warning alerts",
            "experience_domain": "AI companion products and user research synthesis",
            "jd_needs": "conduct customer interviews, gather clinical requirements, and run agile sprints",
            "proof": "interviewed 60+ users to shape AI modules and steered prototypes reaching 78% completion across pilots",
            "team_impact": "turn complex stakeholder feedback into crisp PRDs and speed up delivery cycles"
        }
    },
    {
        "id": 4,
        "company": "Karya",
        "role_title": "Associate Product Manager",
        "job_url": "https://job-boards.greenhouse.io/karya/jobs/5205891008",
        "resume_name": "Farzaan's Resume 17",
        "resume_link": "https://docs.google.com/document/d/13s5PxwLtzrKPa42I1BW2CewxwT3CKu0aunDBx3FjM7Q/edit",
        "employee": {
            "name": "Aastha Bhandari",
            "first_name": "Aastha",
            "title": "Associate Product Manager",
            "team": "Product",
            "email": "aastha.bhandari@karya.in",
            "profile_url": "https://linkedin.com/in/aasthabhandari",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Manu Chopra",
            "first_name": "Manu",
            "title": "CEO",
            "team": "Executive / Product",
            "email": "manu@karya.in",
            "profile_url": "https://linkedin.com/in/manuchopra",
            "confidence": "High",
            "company_detail": "ethical AI datasets and speech platform expansion across rural India",
            "experience_domain": "speech AI prototypes and Tier-1 to 3 user discovery",
            "jd_needs": "translate user needs into PRDs, lead agile ceremonies, and own feature delivery",
            "proof": "prototyped an AI speech application with 120 users achieving 78% completion and coordinated sprints for a feature reaching 90% adoption",
            "team_impact": "accelerate product delivery and ensure mobile features resonate with underserved users"
        }
    },
    {
        "id": 5,
        "company": "Emergence AI",
        "role_title": "Product Owner (India Pod)",
        "job_url": "https://job-boards.greenhouse.io/emergenceai/jobs/4483641009",
        "resume_name": "Farzaan's Resume 18",
        "resume_link": "https://docs.google.com/document/d/1Dr4andyni7LlbS74peX5NRk0hNREvB3Dmvt3w2s4JU4/edit",
        "employee": {
            "name": "Karthik Vikram",
            "first_name": "Karthik",
            "title": "Staff AI Engineer",
            "team": "Tech / Engineering",
            "email": "karthik@emergence.ai",
            "profile_url": "https://linkedin.com/in/karthikvikram",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Satya",
            "first_name": "Satya",
            "title": "Head of Product",
            "team": "Product",
            "email": "satya@emergence.ai",
            "profile_url": "https://emergence.ai",
            "confidence": "Medium",
            "company_detail": "autonomous multi-agent AI systems and agent orchestration infrastructure",
            "experience_domain": "AI workflows, prompt engineering, and agile pod execution",
            "jd_needs": "define clear specs for AI agents, maintain evals, and verify shipped features",
            "proof": "built 30+ automated AI workflow systems saving 200+ hours monthly and engineered 10 internal tools with 90% team adoption",
            "team_impact": "bridge customer requirements to engineering pods with tight acceptance criteria"
        }
    },
    {
        "id": 6,
        "company": "ToolJet",
        "role_title": "Associate Product Manager (Technical)",
        "job_url": "https://wellfound.com/jobs/4465216-associate-product-manager-technical",
        "resume_name": "Farzaan's Resume 19",
        "resume_link": "https://docs.google.com/document/d/1tpwd91MmGhAyHHCYt2QGCAECqxEzUYMzQ3hRKHQ-rrE/edit",
        "employee": {
            "name": "Devang Agarwal",
            "first_name": "Devang",
            "title": "Senior Product Manager",
            "team": "Product",
            "email": "devang.agarwal@tooljet.com",
            "profile_url": "https://linkedin.com/in/devangagarwal",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Navaneeth PK",
            "first_name": "Navaneeth",
            "title": "CEO",
            "team": "Executive / Product",
            "email": "navaneeth@tooljet.com",
            "profile_url": "https://linkedin.com/in/navaneeth-pk",
            "confidence": "High",
            "company_detail": "open-source low-code tools and enterprise workflow integrations",
            "experience_domain": "technical PRDs, developer workflows, and SaaS integrations",
            "jd_needs": "gather technical requirements, write API specs, and manage release backlogs",
            "proof": "led product execution for a hotel SaaS handling ₹1M+ booking value and built 30+ automation pipelines cutting overhead 30%",
            "team_impact": "deliver intuitive builder features and maintain tight alignment with engineering"
        }
    },
    {
        "id": 7,
        "company": "LearnTube.ai",
        "role_title": "Associate Product Manager",
        "job_url": "https://wellfound.com/jobs/5085802-product-intern-clone",
        "resume_name": "Farzaan's Resume 20",
        "resume_link": "https://docs.google.com/document/d/1sXWlHoesTSF61h9X3sN_OpYLrGzqOsxr46aZ6EhcTok/edit",
        "employee": {
            "name": "Hiten Saxena",
            "first_name": "Hiten",
            "title": "Senior Product Designer",
            "team": "Design",
            "email": "hiten@learntube.ai",
            "profile_url": "https://linkedin.com/in/hitensaxena",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Shubham",
            "first_name": "Shubham",
            "title": "Founder",
            "team": "Executive / Product",
            "email": "shubham@learntube.ai",
            "profile_url": "https://wellfound.com/jobs/5085802-product-intern-clone",
            "confidence": "High",
            "company_detail": "AI-powered bite-sized courses and interactive gamified learning loops",
            "experience_domain": "ed-tech product discovery and learner retention loops",
            "jd_needs": "run rapid experiments, define feature user stories, and drive session completion",
            "proof": "piloted an edutainment prototype achieving 78% completion across 120 students and drove delivery of an AI feature reaching 90% adoption",
            "team_impact": "ship high-retention learner flows and turn student feedback into quick product wins"
        }
    },
    {
        "id": 8,
        "company": "Karya",
        "role_title": "Associate – Founder's Office",
        "job_url": "https://job-boards.greenhouse.io/karya/jobs/5464495008-0",
        "resume_name": "Farzaan's Resume 21",
        "resume_link": "https://docs.google.com/document/d/153AALKFHWSa2lJ53wRIxJ9wJXRhe2YVj2NZdCbt2KKE/edit",
        "employee": {
            "name": "Tulsi Bhikadia",
            "first_name": "Tulsi",
            "title": "Product Specialist",
            "team": "Product / Operations",
            "email": "tulsi.bhikadia@karya.in",
            "profile_url": "https://linkedin.com/in/tulsi-bhikadia",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Manu Chopra",
            "first_name": "Manu",
            "title": "CEO",
            "team": "Executive / Founder's Office",
            "email": "manu@karya.in",
            "profile_url": "https://linkedin.com/in/manuchopra",
            "confidence": "High",
            "company_detail": "scaling ethical digital work opportunities to millions across India",
            "experience_domain": "founder collaboration, operational workflows, and 0-to-1 execution",
            "jd_needs": "high-agency ownership in ambiguous environments, cross-functional execution, and analytical diagnosis",
            "proof": "built 30+ automated workflows saving 200+ hours monthly and diagnosed operational bottlenecks to cut manual effort 60%",
            "team_impact": "own critical cross-functional initiatives and unblock executive priorities"
        }
    },
    {
        "id": 9,
        "company": "Spring Street",
        "role_title": "Associate Product Manager",
        "job_url": "https://wellfound.com/jobs/4965714-associate-product-manager",
        "resume_name": "Farzaan's Resume 22",
        "resume_link": "https://docs.google.com/document/d/1ic5mPa0P63PcSzIABxqXieF-dPM6L7eLzJINRTk0fL8/edit",
        "employee": {
            "name": "Hritik Singh",
            "first_name": "Hritik",
            "title": "Software Engineer",
            "team": "Tech / Engineering",
            "email": "hritik.singh@springstreet.in",
            "profile_url": "https://linkedin.com/in/hriitz",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Founding Team",
            "first_name": "there",
            "title": "Founding Team",
            "team": "Executive / Product",
            "email": "founder@springstreet.in",
            "profile_url": "https://wellfound.com/jobs/4965714-associate-product-manager",
            "confidence": "Medium",
            "company_detail": "consumer commerce infrastructure and high-velocity digital product execution",
            "experience_domain": "e-commerce product execution and conversion optimization",
            "jd_needs": "prioritize product backlogs, analyze user journeys, and write clear PRDs",
            "proof": "lifted checkout completion 15%, cut bounce rates 20%, and grew annual store revenues by ₹2M through CRO experiments",
            "team_impact": "streamline digital conversion funnels and keep development sprints on schedule"
        }
    },
    {
        "id": 10,
        "company": "Quros Tech",
        "role_title": "Associate Product Manager",
        "job_url": "https://wellfound.com/jobs/5031234-associate-product-manager",
        "resume_name": "Farzaan's Resume 23",
        "resume_link": "https://docs.google.com/document/d/18p34BKarSozJ1DXBZK_0mMmZ53SMtpa2cAixLS4TxGU/edit",
        "employee": {
            "name": "Pritom Roy",
            "first_name": "Pritom",
            "title": "Product Manager",
            "team": "Product",
            "email": "pritom.roy@quros.in",
            "profile_url": "https://linkedin.com/in/pritom-roy-8903b4174",
            "confidence": "Medium"
        },
        "hm": {
            "name": "Founding Team",
            "first_name": "there",
            "title": "Founding Team",
            "team": "Executive / Product",
            "email": "founder@quros.in",
            "profile_url": "https://wellfound.com/jobs/5031234-associate-product-manager",
            "confidence": "Medium",
            "company_detail": "delivering end-to-end product architecture and client digital solutions",
            "experience_domain": "client discovery, PRD documentation, and agile execution",
            "jd_needs": "gather client requirements, translate needs into functional specs, and guide developers",
            "proof": "led discovery for an internal hotel management SaaS with 27 properties and built 30+ automation systems saving 200+ hours monthly",
            "team_impact": "ensure client requirements become release-ready specs without scope drift"
        }
    }
]

def make_employee_dm(j):
    e = j["employee"]
    fn = e["first_name"]
    comp = j["company"]
    role = j["role_title"]
    domain = j["hm"]["experience_domain"]
    focus = j["hm"]["company_detail"]
    skills = j["hm"]["jd_needs"]
    achieve = j["hm"]["proof"]
    
    body = (
        f"Hi {fn},\n\n"
        f"Hope your week is going well.\n\n"
        f"I am an Associate Product Manager with 1.5+ years of experience across {domain}.\n\n"
        f"I am writing because I came across the {role} opening at {comp} and was particularly drawn to your team's expansion in {focus}. I am very interested in this opportunity and would value your guidance on the team's roadmap.\n\n"
        f"Your team is looking for experience in {skills}. In my recent role, I {achieve}.\n\n"
        f"Would you be open to taking a quick look at my profile, or pointing me to the right person for a referral?\n\n"
        f"Profile: https://www.linkedin.com/in/farzaankhan/\n\n"
        f"No worries if it's not a fit right now.\n\n"
        f"Best regards,\nFarzaan Khan"
    )
    return body

def make_hm_dm(j):
    h = j["hm"]
    fn = h["first_name"]
    comp = j["company"]
    role = j["role_title"]
    
    greeting = f"Hi {fn},\n\nHope your week is going well."
    p2 = f"I'm Farzaan, an Associate Product Manager with 1.5+ years of experience in {h['experience_domain']}. I saw the {role} opening at {comp} and it caught my attention."
    p3 = f"I've been reading about {comp}'s work on {h['company_detail']}."
    p4 = f"Your team is looking for someone to {h['jd_needs']}. In my recent work, I {h['proof']}. This means I can {h['team_impact']}."
    p5 = "It would be really great if you would consider me for this position, and I'd be glad to share more.\n\nPFA my resume.\n\nLooking forward to hearing from you."
    signoff = "Best,\nFarzaan"
    
    # Each paragraph as one continuous line, separated by blank line
    dm2 = f"{greeting}\n\n{p2}\n\n{p3}\n\n{p4}\n\n{p5}\n\n{signoff}"
    return dm2

print("Generated dual DMs script loaded.")

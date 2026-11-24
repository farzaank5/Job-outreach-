import sys
import os
from google_services import GoogleWorkspaceManager
from resume_engine import get_next_resume_number

def run():
    manager = GoogleWorkspaceManager()
    base_doc_id = "14-IiDD5SaYRmr-yQxEaHE1Q8K7mbuSe6AOs4iqdq24k"
    
    resume_num = get_next_resume_number(manager)
    resume_name = f"Farzaan's Resume {resume_num}"
    print(f"Creating: {resume_name}")
    
    replacements = {
        # Summary: Tailored for AI Product Discovery & Strategy
        "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
        "Associate Product Manager with 1.5+ years of experience in product discovery, strategy, and user research for AI platforms. Proven track record conducting 60+ user interviews, validating early concepts, and writing engineering-ready PRDs that delivered 90% product adoption.",

        # Experience Bullets: Simple verbs, no buzzwords, no em dashes
        "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
        "Owned product discovery and roadmap strategy for AI-powered SaaS solutions, running competitor benchmarking and user interviews to validate product-market fit.",

        "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
        "Wrote detailed PRDs, wireframe specs in Figma, and user stories for AI workflows, translating customer feedback into prioritized backlogs.",

        "Hands-on architected and prototyped 30+ AI automation workflows using Python, n8n, and Make, saving 200+ hrs/mo and boosting system efficiency by 30%.":
        "Built 30+ automated workflow pipelines and API integrations, saving 200+ hours/month in operational overhead.",

        # ConveGenius: Teacher interviews & AI Companion
        "Led 0-to-1 product discovery for multimodal AI search and learning models, mapping complex AI capabilities into clear PRDs, wireframes, and workflows that supported a $7M funding round.":
        "Conducted in-depth customer interviews across 60+ users to size opportunities and translate unstructured pain points into prioritized product specs.",

        "Drove delivery of a core AI Companion feature: coordinated cross-functional stakeholders, ran sprint planning and tracked milestones. Also built 10 AI tools that cut manual effort by 60% and reached 90% adoption within the organisation.":
        "Launched a core AI Companion feature that reached 90% adoption within the organization, coordinating engineering, design, and QA across sprints.",

        # Skills & Tools: Discovery, PRDs, Figma, Jira, User Research
        "Mixpanel, Tableau, SQL, Figma, Jira, n8n, Make, Python, REST APIs, LLMs, RAG, Productboard":
        "Product Discovery, User Interviews, PRDs, Figma, Jira, User Stories, Rapid Prototyping, APIs, SQL, A/B Testing"
    }

    bold_phrases = [
        "product discovery",
        "60+ user interviews",
        "PRDs",
        "90% product adoption",
        "Figma",
        "Jira",
        "30+",
        "200+ hours/month",
        "Owned",
        "Built",
        "Wrote",
        "Launched"
    ]

    result = manager.create_numbered_tailored_resume(
        base_document_id=base_doc_id,
        resume_number=resume_num,
        replacements=replacements,
        bold_phrases=bold_phrases
    )

    print("\n--- RESUME GENERATION SUCCESS ---")
    print("Resume Name:", result["resume_name"])
    print("Google Doc Link:", result["tailored_doc_url"])
    print("PDF Path:", result["pdf_path"])
    print("Page Count:", result["page_count"])
    return result

if __name__ == '__main__':
    run()

import sys
import os
from google_services import GoogleWorkspaceManager
from resume_engine import get_next_resume_number
from drive_csv_tracker import append_to_tracker

def generate_step3_tailored_resume():
    manager = GoogleWorkspaceManager()
    base_doc_id = "14-IiDD5SaYRmr-yQxEaHE1Q8K7mbuSe6AOs4iqdq24k"
    
    # 1. Determine next sequential number
    resume_num = get_next_resume_number(manager)
    resume_name = f"Farzaan's Resume {resume_num}"
    print(f"Generating: {resume_name}")
    
    # 2. Content tailored with simple action verbs, plain words, no buzzwords, no em dashes
    replacements = {
        # Summary
        "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
        "Product Manager with 2 years of experience building B2B and B2C eCommerce platforms, Order Management Center workflows, and fulfillment systems. Skilled in writing PRDs and user stories in Jira, running Agile sprints with engineering, and tracking adoption.",

        # Experience Bullets (Simple verbs: Owned, Wrote, Built, Analyzed)
        "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
        "Owned product delivery and Agile sprint execution for eCommerce platforms, managing backlogs in Jira and working with engineering and design to ship on schedule.",

        "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
        "Wrote detailed PRDs, user stories, and acceptance criteria for Order Management Center modules and shipment tracking workflows.",

        "Hands-on architected and prototyped 30+ AI automation workflows using Python, n8n, and Make, saving 200+ hrs/mo and boosting system efficiency by 30%.":
        "Built 30+ automated workflow pipelines and REST API integrations, saving 200+ hours/month in manual operations and cutting fulfillment cycle times.",

        "Analyzed user funnels and checkout drop-off, partnering with cross-functional teams to design and implement automated post-purchase workflows.":
        "Analyzed user drop-off across checkout funnels and partnered with developers to launch automated order tracking workflows.",

        # Skills & Tools: Plain, relevant keywords
        "Mixpanel, Tableau, SQL, Figma, Jira, n8n, Make, Python, REST APIs, LLMs, RAG, Productboard":
        "Jira, Agile Scrum, B2B and B2C eCommerce, Order Management, Shipment Tracking, REST APIs, SQL, Figma, Python, UAT"
    }
    
    # 3. Strategic bolding list (10-12 total phrases across the whole page)
    # Numbers and results + JD matching keywords + key outcome words
    bold_phrases = [
        "Order Management Center",
        "Jira",
        "PRDs",
        "30+",
        "200+ hours/month",
        "REST APIs",
        "Owned",
        "Built",
        "Wrote",
        "Analyzed"
    ]
    
    result = manager.create_numbered_tailored_resume(
        base_document_id=base_doc_id,
        resume_number=resume_num,
        replacements=replacements,
        bold_phrases=bold_phrases
    )
    
    print("\n--- RESUME GENERATED SUCCESSFULLY ---")
    print("Resume Name:", result["resume_name"])
    print("Google Doc Link:", result["tailored_doc_url"])
    print("PDF Path:", result["pdf_path"])
    print("Page Count:", result["page_count"])
    return result

if __name__ == '__main__':
    generate_step3_tailored_resume()

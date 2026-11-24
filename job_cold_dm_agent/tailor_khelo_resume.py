import sys
import os
from google_services import GoogleWorkspaceManager

def tailor_resume():
    manager = GoogleWorkspaceManager()
    base_doc_id = "14-IiDD5SaYRmr-yQxEaHE1Q8K7mbuSe6AOs4iqdq24k"
    
    # Define replacements to align with KheloTech APM JD while strictly preserving 1-page length
    replacements = {
        # Summary adjustment
        "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
        "High-agency Associate Product Manager with 2+ years of end-to-end product lifecycle ownership across web and mobile platforms. Proven expertise translating user needs into crisp PRDs, managing sprint backlogs in Zoho Sprints & Jira, conducting user research, and optimizing funnels with Google Analytics to accelerate execution and drive 90% product adoption.",
        
        # Softwarelance role alignment (web & mobile apps, sprints, metrics)
        "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
        "Drive end-to-end product ownership and Agile sprint execution using Zoho Sprints and Jira, aligning engineering, design, and QA teams to ship web and mobile feature iterations at high velocity.",
        
        "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
        "Translate user feedback and business requirements into clear user stories, PRDs, release notes, and documentation, maintaining product backlogs and platform roadmaps.",
        
        "Tracked funnel metrics and user drop-off via Mixpanel and SQL across 12 SaaS implementations, prioritizing roadmap updates that unlocked ₹2M ARR impact.":
        "Monitored product performance, user journeys, and funnel drop-off using Google Analytics and SQL, delivering data-backed roadmap updates that accelerated user adoption.",
        
        # ConveGenius alignment (mobile/web consumer-facing research & demos)
        "Led 0-to-1 product discovery for multimodal AI search and learning models, mapping complex AI capabilities into clear PRDs, wireframes, and workflows that supported a $7M funding round.":
        "Led 0-to-1 product discovery for consumer-facing digital learning platforms, defining wireframes in Figma, API requirements, and user workflows that supported platform scale.",
        
        "Collaborated cross-functionally with AI engineers, designers, and domain experts on rapid prototyping, UAT, and model evaluations, achieving a 78% completion rate.":
        "Conducted sprint planning, UAT, usability testing, and live product demos with cross-functional stakeholders, ensuring on-time releases and 78% feature completion rates.",
        
        # Skills alignment
        "Mixpanel, Tableau, SQL, Figma, Jira, n8n, Make, Python, REST APIs, LLMs, RAG, Productboard":
        "Google Analytics, Zoho Sprints, Jira, Figma, Trello, SQL, REST APIs, Python, Product Lifecycle, UAT"
    }
    
    print("Duplicating base document and generating tailored KheloTech APM resume...")
    result = manager.duplicate_and_tailor_resume(
        base_document_id=base_doc_id,
        target_role="APM",
        company_name="KheloTech",
        replacements=replacements
    )
    
    print("\n--- RESUME GENERATION SUCCESS ---")
    print("New Google Doc ID:", result["tailored_doc_id"])
    print("New Google Doc URL:", result["tailored_doc_url"])
    print("Exported PDF Path:", result["pdf_path"])
    return result

if __name__ == "__main__":
    tailor_resume()

import sys
import os
from google_services import GoogleWorkspaceManager

def tailor_delma_resume():
    manager = GoogleWorkspaceManager()
    base_doc_id = "14-IiDD5SaYRmr-yQxEaHE1Q8K7mbuSe6AOs4iqdq24k"
    
    replacements = {
        # Summary alignment: eCommerce, OMC, shipment tracking, APIs
        "High-agency Product Manager with 2+ years of 0-to-1 startup ownership building AI-first products, LLM applications, and automated workflows. Expert in conducting deep user research, translating ambiguous user pain points into crisp PRDs, rapid prototyping, and collaborating cross-functionally with engineering and business teams to ship fast and drive 90% product adoption.":
        "Execution-focused Product Manager with 2+ years of experience across B2B/B2C eCommerce platforms, Order Management Center (OMC) workflows, and automated fulfillment systems. Adept in translating business goals into detailed PRDs, user stories, and acceptance criteria in Jira, collaborating with engineering to ship API integrations and drive 90% product adoption.",
        
        # Softwarelance: Shopify SaaS, order fulfillment, APIs, Jira backlogs
        "Drive 0-to-1 product ownership and rapid Agile sprint execution for AI-first SaaS solutions, aligning engineering, design, and business teams to ship feature iterations at high velocity.":
        "Drive product ownership and Agile sprint execution for eCommerce SaaS platforms, managing sprint backlogs in Jira and aligning engineering, QA, and business teams to ship fulfillment features on schedule.",
        
        "Translate ambiguous user feedback into actionable PRDs, functional specs, and success metrics for AI-first workflows and LLM applications, leading backlogs and core KPI tracking.":
        "Author comprehensive PRDs, user stories, and acceptance criteria for Order Management Center (OMC) modules, shipment tracking, and post-purchase customer workflows.",
        
        "Hands-on architected and prototyped 30+ AI automation workflows using Python, n8n, and Make, saving 200+ hrs/mo and boosting system efficiency by 30%.":
        "Architected and integrated 30+ automated eCommerce workflows and REST API data pipelines, cutting order fulfillment cycle times and saving 200+ operational hours/month.",
        
        # Surgelion: eCommerce conversion & checkout workflows
        "Analyzed user funnels and checkout drop-off, partnering with cross-functional teams to design and implement automated post-purchase workflows.":
        "Analyzed B2C eCommerce purchase funnels and fulfillment drop-offs, partnering with cross-functional teams to streamline order processing and shipment tracking workflows.",
        
        # Skills alignment
        "Mixpanel, Tableau, SQL, Figma, Jira, n8n, Make, Python, REST APIs, LLMs, RAG, Productboard":
        "Jira, Agile/Scrum, B2B/B2C eCommerce, Order Management (OMC), Shipment Tracking, REST APIs, SQL, Figma, Python, UAT"
    }
    
    print("Generating tailored Delma PM resume...")
    result = manager.duplicate_and_tailor_resume(
        base_document_id=base_doc_id,
        target_role="Product_Manager",
        company_name="Delma_LLC",
        replacements=replacements
    )
    
    print("New Doc ID:", result["tailored_doc_id"])
    print("New Doc URL:", result["tailored_doc_url"])
    print("PDF Path:", result["pdf_path"])
    return result

if __name__ == "__main__":
    tailor_delma_resume()

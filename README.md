# AI Job Cold DM Agent & Outreach Pipeline

An automated, end-to-end outbound job sourcing and cold outreach agent built for high-growth tech and startup roles. The agent evaluates active job postings against your default resume ground truth, scores match thresholds, identifies verified decision-maker leads (Hiring Managers, Founders, and Team Leads), generates tailored resumes via Google Docs & Drive, and dispatches hyper-personalized cold outreach emails via the Gmail API.

---

## Key Features

- **Multi-Source Sourcing Engine**:
  - Scrapes ATS job boards (Greenhouse, Lever, Ashby)
  - Scrapes Y Combinator / Hacker News startup feeds
  - Scrapes remote product boards (Jobicy, etc.)
  - Filters by recency (e.g. postings within the last 14 days) and target titles.

- **AI Job Matching & Fit Scoring**:
  - Evaluates job descriptions against a memorized default resume ground truth using Gemini models.
  - Automatically assesses core requirements, skill gaps, and match percentage (enforcing an 80–90%+ qualification threshold).

- **Authority Lead Discovery Cascade**:
  - Uses Prospeo API with multi-tier hierarchy fallback:
    $$\text{Hiring Manager / Founder} \longrightarrow \text{HR / Talent Partner} \longrightarrow \text{Peer / Referral Employee}$$
  - Enriches contacts with verified email addresses and LinkedIn URLs.

- **Automated Resume Tailoring**:
  - Automatically duplicates a master resume template in Google Docs.
  - Replaces domain summaries, highlighted bullet achievements, and bold keywords to align with the specific JD.
  - Exports cleanly formatted 1-page PDF resumes to Google Drive and local storage.

- **Personalized Email Outreach & Dual DMs**:
  - Drafts and sends personalized cold emails via the Gmail API with the tailored PDF resume attached.
  - Supports dual outreach cadences: Employee Referral DMs (DM 1) and Hiring Manager direct pitches (DM 2).

- **Dual-Layer Real-Time Tracking**:
  - Logs every role, contact, message ID, timestamp, and resume link to `job_outreach_tracker.csv`.
  - Automatically syncs all records to a live Google Sheets tracker.
  - Supports automated inbox reply detection and follow-up reminders.

---

## Architecture Overview

```
                          +------------------------+
                          |   Job Board Scraper    |
                          | (Greenhouse, Lever,    |
                          |  Ashby, YC, Jobicy)    |
                          +-----------+------------+
                                      |
                                      v
                          +------------------------+
                          |   Gemini JD Matcher    | <--- Default Resume Ground Truth
                          |  (Fit Score >= 80-90%) |
                          +-----------+------------+
                                      |
                                      v
                          +------------------------+
                          |  Lead Cascade Engine   |
                          | (Prospeo / Standby)    |
                          +-----------+------------+
                                      |
                     +----------------+----------------+
                     |                                 |
                     v                                 v
          +---------------------+            +---------------------+
          | Google Docs Engine  |            |  Gmail API Pipeline |
          | (Tailored Resumes)  |            |   (Cold DM Dispatch)|
          +----------+----------+            +----------+----------+
                     |                                  |
                     +----------------+-----------------+
                                      |
                                      v
                          +------------------------+
                          |  Sheet & CSV Tracker   |
                          | (Live Status & Replies)|
                          +------------------------+
```

---

## Project Structure

```
├── job_cold_dm_agent/
│   ├── orchestrator.py            # End-to-end multi-step workflow orchestrator
│   ├── job_scraper.py             # Multi-source job board scraper
│   ├── jd_matcher.py              # Gemini JD evaluation & fit scoring
│   ├── lead_finder.py             # Prospeo authority cascade lead discovery
│   ├── google_services.py         # Google Docs, Drive, and Gmail API integration
│   ├── resume_engine.py           # Resume customization and PDF generation
│   ├── drive_csv_tracker.py       # CSV and Google Sheet bidirectional synchronization
│   ├── outreach_pipeline.py       # Cold email formatting and validation
│   ├── default_resume.txt         # Plaintext default resume ground truth
│   └── job_preferences.json       # Role titles, locations, and thresholds
├── README.md
└── .gitignore
```

---

## Setup & Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure API Credentials
Create a `.env` file in `job_cold_dm_agent/` based on `.env.example`:
```bash
cp job_cold_dm_agent/.env.example job_cold_dm_agent/.env
```
Add your API keys:
```env
GOOGLE_API_KEY=your_gemini_api_key
PROSPEO_API_KEY=your_prospeo_api_key
```

### 4. Authenticate Google Workspace (Gmail, Drive, Docs)
1. Place your Google Cloud OAuth `credentials.json` inside `job_cold_dm_agent/`.
2. Run the authentication flow:
   ```bash
   python job_cold_dm_agent/auth_setup.py
   ```
3. Sign in to your Google Account to generate `token.json`.

---

## License
MIT License.

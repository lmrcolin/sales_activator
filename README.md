# SalesActivator – MICE (US Direct Segment)

Free, end-to-end B2B outbound system for US MICE companies. Scrapes leads from public web sources, enriches data, sends Gmail SMTP sequences, and shows a Streamlit dashboard.

## Features

- 100% free stack: Python, SQLite, duckduckgo_search, BeautifulSoup, requests, Streamlit, smtplib.
- Scrape public web results for MICE companies/venues in the US.
- Enrich from company websites (emails, phones, addresses) and guess contact emails.
- 3-step outbound email sequence via Gmail SMTP (App Password).
- Streamlit dashboard for leads, send status, and run jobs.

## Quickstart

1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

````bash
# SalesActivator – MICE (US Direct Segment)

Free, end-to-end B2B outbound system for US MICE companies. Scrapes leads from public web sources, enriches data, sends Gmail SMTP sequences, and shows a Streamlit dashboard.

## What you’ll need (free)
- Python 3.13 for CLI (recommended)
- Python 3.12 for Streamlit locally (recommended) or use Streamlit Cloud
- A Gmail account with 2FA + App Password (for real sending)

## Step-by-step setup (from clone to send)

1) Clone and enter the project
```bash
git clone .. salesactivator
cd salesactivator
````

2. Create a virtual environment (CLI)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies (CLI)

```bash
pip install -r requirements.txt
```

4. Configure environment

```bash
cp .env.example .env
# Edit .env and set SMTP_USERNAME, SMTP_APP_PASSWORD, FROM_EMAIL, FROM_NAME
# You can keep defaults for the rest and tweak later
```

5. Initialize database

```bash
python -m salesactivator.cli init-db
```

6. Get companies

- Option A: Web search (free but rate-limited)

```bash
python -m salesactivator.cli scrape --limit 30
```

- Option B (recommended to start): Seed list

```bash
python -m salesactivator.cli scrape --use-seeds
```

7. Enrich companies (website scraping for emails/phones)

```bash
python -m salesactivator.cli enrich --limit 50
```

8. Schedule the 3-step email sequence

```bash
python -m salesactivator.cli sequence --limit 50
```

9. Send emails

- Dry-run (no emails sent, marks items as “sent” for verification):

```bash
python -m salesactivator.cli send --dry-run
```

- Real send (requires valid Gmail App Password):

```bash
python -m salesactivator.cli send
```

## Dashboard (optional)

Local (use Python 3.12 for best compatibility):

```bash
python3.12 -m venv .venv-st
source .venv-st/bin/activate
pip install streamlit python-dotenv
streamlit run app.py
```

Streamlit Cloud (free):

- Push this repo to GitHub
- Create app in Streamlit Cloud from the repo
- Add Secrets (same keys as `.env`)
- Command: `streamlit run app.py`

## Loom demo flow

1. Show `.env.example` → explain free Gmail SMTP via App Password
2. Run CLI:
   - `init-db`
   - `scrape --use-seeds`
   - `enrich --limit 10`
   - `sequence --limit 10`
   - `send --dry-run`
3. Open the dashboard: leads, email queue, companies, contacts
4. Emphasize 100% free stack and public data sources

## Notes

- Respect robots.txt and site terms; throttle requests (configurable)
- Email guessing/enrichment is heuristic; validate before large sends
- Gmail SMTP requires 2FA + App Password

## Troubleshooting

- Emails sent = 0

  - Make sure you ran: `python -m salesactivator.cli sequence --limit 30`
  - Check `.env` SMTP*\* and FROM*\* variables
  - Ensure first step is due (scheduled_at <= now)

- `streamlit: command not found`
  - Use a Python 3.12 env for Streamlit locally or deploy to Streamlit Cloud

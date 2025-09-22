import argparse
from datetime import datetime
from urllib.parse import urlparse
import csv
import os

from salesactivator.utils.config import Settings
from salesactivator.db.store import DB
from salesactivator.utils.http import Http
from salesactivator.scrapers.search import search_mice_companies
from salesactivator.enrich.website import WebsiteEnricher
from salesactivator.utils.text import is_email_valid, guess_corporate_email_patterns
from salesactivator.emailer.sender import EmailSender


def cmd_init_db(args):
    s = Settings()
    db = DB(s.DB_PATH)
    db.init()
    print("DB initialized at", s.DB_PATH)


def cmd_scrape(args):
    s = Settings()
    db = DB(s.DB_PATH)
    http = Http(s.USER_AGENT, s.REQUEST_DELAY_SEC)
    enricher = WebsiteEnricher(http)

    results = [] if args.use_seeds else search_mice_companies(limit=args.limit)
    inserted = 0
    for r in results:
        href = r.get("href") or ""
        # try to keep only company domains (not linkedin profiles)
        parsed = urlparse(href)
        domain = parsed.netloc
        if not domain or any(x in domain for x in ["linkedin.com", "facebook.com", "instagram.com", "x.com", "twitter.com"]):
            continue
        cid = db.upsert_company(name=r.get("title") or domain, website=f"https://{domain}", country="United States", source="duckduckgo")
        if cid:
            inserted += 1
    # fallback to seeds if nothing found or explicit flag
    if inserted == 0 or args.use_seeds:
        seeds_path = os.path.join(os.path.dirname(__file__), "..", "data", "seeds_companies.csv")
        seeds_path = os.path.abspath(seeds_path)
        if os.path.exists(seeds_path):
            with open(seeds_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cid = db.upsert_company(
                        name=row.get("name") or "",
                        website=row.get("website") or "",
                        city=row.get("city"),
                        state=row.get("state"),
                        country=row.get("country"),
                        source="seeds",
                    )
                    if cid:
                        inserted += 1
    print(f"Scrape done. Upserted companies: {inserted}")


def cmd_enrich(args):
    s = Settings()
    db = DB(s.DB_PATH)
    http = Http(s.USER_AGENT, s.REQUEST_DELAY_SEC)
    enricher = WebsiteEnricher(http)

    companies = db.query("SELECT id, name, website FROM companies ORDER BY id DESC LIMIT ?", (args.limit,))
    created_leads = 0
    for c in companies:
        info = enricher.enrich(c["website"])
        # Save generic emails as contacts if present
        emails = info.get("emails", [])
        phones = info.get("phones", [])
        main_email = None
        for e in emails:
            if is_email_valid(e):
                main_email = e
                break
        contact_id = None
        if main_email:
            contact_id = db.add_contact(c["id"], full_name="General Contact", role="Info", email=main_email, phone=phones[0] if phones else None)
        lead_id = db.add_lead(c["id"], contact_id=contact_id, status="enriched")
        created_leads += 1
    print(f"Enrichment done. Leads created: {created_leads}")


def cmd_sequence(args):
    s = Settings()
    db = DB(s.DB_PATH)
    sender = EmailSender(s)
    leads = db.query("""
        SELECT leads.id as lead_id, companies.name as company, contacts.full_name as contact
        FROM leads
        LEFT JOIN companies ON leads.company_id = companies.id
        LEFT JOIN contacts ON leads.contact_id = contacts.id
        WHERE leads.id NOT IN (SELECT DISTINCT lead_id FROM email_queue)
        ORDER BY leads.id DESC LIMIT ?
    """, (args.limit,))
    for r in leads:
        sender.create_sequence(db, r["lead_id"], r.get("contact"), r.get("company") or "", datetime.now())
    print(f"Sequence scheduled for {len(leads)} leads")


def cmd_send(args):
    s = Settings()
    db = DB(s.DB_PATH)
    sender = EmailSender(s)
    cnt = sender.send_due(db, dry_run=args.dry_run)
    print(f"Emails sent: {cnt}")


def main():
    parser = argparse.ArgumentParser(prog="salesactivator")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("init-db")
    p1.set_defaults(func=cmd_init_db)

    p2 = sub.add_parser("scrape")
    p2.add_argument("--limit", type=int, default=30)
    p2.add_argument("--use-seeds", action="store_true", help="Load seed companies CSV instead of web search (or as fallback)")
    p2.set_defaults(func=cmd_scrape)

    p3 = sub.add_parser("enrich")
    p3.add_argument("--limit", type=int, default=50)
    p3.set_defaults(func=cmd_enrich)

    p4 = sub.add_parser("sequence")
    p4.add_argument("--limit", type=int, default=50)
    p4.set_defaults(func=cmd_sequence)

    p5 = sub.add_parser("send")
    p5.add_argument("--dry-run", action="store_true")
    p5.set_defaults(func=cmd_send)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

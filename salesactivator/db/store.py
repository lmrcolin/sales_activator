import sqlite3
from typing import Any, Iterable, Optional, Tuple, Mapping
try:
    import pandas as pd  # type: ignore
except Exception:
    pd = None  # optional
import os

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    name TEXT,
    website TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_companies_website ON companies(website);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    full_name TEXT,
    role TEXT,
    email TEXT,
    phone TEXT
);

CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'new', -- new, enriched, active, won, lost
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company_id);

CREATE TABLE IF NOT EXISTS email_queue (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    step INTEGER,
    subject TEXT,
    body TEXT,
    status TEXT DEFAULT 'scheduled', -- scheduled, sent, failed, skipped
    scheduled_at TIMESTAMP,
    last_attempt_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_queue_scheduled ON email_queue(status, scheduled_at);
"""

class DB:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path

    def connect(self):
        return sqlite3.connect(self.path)

    def init(self):
        with self.connect() as con:
            con.executescript(SCHEMA_SQL)

    def execute(self, sql: str, params: Any = ()):  # for INSERT/UPDATE/DELETE
        with self.connect() as con:
            cur = con.execute(sql, params)
            con.commit()
            return cur.lastrowid

    def query(self, sql: str, params: Any = ()):  # for SELECT
        with self.connect() as con:
            cur = con.execute(sql, params)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in rows]

    def df(self, sql: str, params: Any = ()):  # DataFrame
        with self.connect() as con:
            cur = con.execute(sql, params)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            data = [dict(zip(cols, r)) for r in rows]
            if pd is None:
                return data  # Streamlit can render list-of-dicts
            return pd.DataFrame(data)

    # Convenience methods
    def upsert_company(self, name: str, website: str, city: Optional[str] = None, state: Optional[str] = None, country: Optional[str] = None, source: Optional[str] = None):
        # normalize website
        website_n = (website or '').strip().rstrip('/')
        existing = self.query("SELECT id FROM companies WHERE website = ?", (website_n,))
        if existing:
            return existing[0]['id']
        return self.execute(
            "INSERT INTO companies(name, website, city, state, country, source) VALUES(?,?,?,?,?,?)",
            (name, website_n, city, state, country, source),
        )

    def add_contact(self, company_id: int, full_name: str, role: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None):
        # avoid duplicate exact email per company
        if email:
            found = self.query("SELECT id FROM contacts WHERE company_id=? AND email=?", (company_id, email))
            if found:
                return found[0]['id']
        return self.execute(
            "INSERT INTO contacts(company_id, full_name, role, email, phone) VALUES(?,?,?,?,?)",
            (company_id, full_name, role, email, phone),
        )

    def add_lead(self, company_id: int, contact_id: Optional[int] = None, status: str = 'new'):
        return self.execute(
            "INSERT INTO leads(company_id, contact_id, status) VALUES(?,?,?)",
            (company_id, contact_id, status),
        )

    def schedule_email(self, lead_id: int, step: int, subject: str, body: str, scheduled_at: str):
        return self.execute(
            "INSERT INTO email_queue(lead_id, step, subject, body, scheduled_at) VALUES(?,?,?,?,?)",
            (lead_id, step, subject, body, scheduled_at),
        )

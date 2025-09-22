import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime
from typing import Optional

from salesactivator.utils.config import Settings
from salesactivator.db.store import DB
from salesactivator.emailer.templates import render_subject, render_body


class EmailSender:
    def __init__(self, settings: Settings):
        self.s = settings

    def _send(self, to_email: str, subject: str, body: str) -> bool:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = formataddr((self.s.FROM_NAME, self.s.FROM_EMAIL))
        msg["To"] = to_email
        try:
            with smtplib.SMTP(self.s.SMTP_HOST, self.s.SMTP_PORT) as server:
                server.starttls()
                server.login(self.s.SMTP_USERNAME, self.s.SMTP_APP_PASSWORD)
                server.sendmail(self.s.FROM_EMAIL, [to_email], msg.as_string())
            return True
        except Exception:
            return False

    def send_due(self, db: DB, dry_run: bool = False) -> int:
        rows = db.query(
            "SELECT id, lead_id, step, subject, body FROM email_queue WHERE status='scheduled' AND scheduled_at <= CURRENT_TIMESTAMP ORDER BY scheduled_at ASC LIMIT 100"
        )
        sent = 0
        for r in rows:
            lead = db.query("SELECT contact_id FROM leads WHERE id=?", (r["lead_id"],))
            if not lead:
                continue
            contact_id = lead[0]["contact_id"]
            if not contact_id:
                continue
            contact = db.query("SELECT email, full_name FROM contacts WHERE id=?", (contact_id,))
            if not contact:
                continue
            to_email = contact[0]["email"]
            if not to_email:
                continue
            ok = True if dry_run else self._send(to_email, r["subject"], r["body"])
            db.execute(
                "UPDATE email_queue SET status=?, last_attempt_at=CURRENT_TIMESTAMP WHERE id=?",
                ("sent" if ok else "failed", r["id"]),
            )
            if ok:
                sent += 1
        return sent

    def create_sequence(self, db: DB, lead_id: int, contact_name: Optional[str], company_name: str, start: datetime):
        from salesactivator.emailer.templates import schedule_dates
        dates = schedule_dates(start)
        for step, when in dates.items():
            subj = render_subject(step, company_name)
            body = render_body(step, contact_name or "", company_name)
            db.schedule_email(lead_id, step, subj, body, when.strftime("%Y-%m-%d %H:%M:%S"))

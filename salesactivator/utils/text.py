import re
from email_validator import validate_email, EmailNotValidError

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_REGEX = re.compile(r"\+?\d[\d\s().-]{7,}\d")

COMMON_ROLES = [
    "Founder", "Co-Founder", "CEO", "President", "Partner",
    "Head of Events", "VP Events", "Director of Events", "Event Manager",
    "Sales", "Business Development", "Account Executive",
]

DOMAINS_STOPLIST = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}


def extract_emails(text: str):
    emails = set(EMAIL_REGEX.findall(text or ""))
    return [e for e in emails if not any(e.lower().endswith("@" + d) for d in DOMAINS_STOPLIST)]


def extract_phones(text: str):
    return list(set(PHONE_REGEX.findall(text or "")))


def is_email_valid(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def guess_corporate_email_patterns(domain: str, full_name: str):
    full = full_name.strip().lower()
    parts = re.split(r"\s+", full)
    if not parts:
        return []
    first = parts[0]
    last = parts[-1]
    initials = ''.join(p[0] for p in parts if p)
    candidates = [
        f"{first}.{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}{last[0]}@{domain}",
        f"{initials}@{domain}",
    ]
    return list(dict.fromkeys(candidates))

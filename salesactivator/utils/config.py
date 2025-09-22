import os
from dataclasses import dataclass

# Load .env if python-dotenv is available; otherwise continue with OS env only
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

@dataclass
class Settings:
    ENV: str = os.getenv("ENV", "dev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DB_PATH: str = os.getenv("DB_PATH", "./data/salesactivator.db")
    USER_AGENT: str = os.getenv("USER_AGENT", "SalesActivatorBot/1.0 (+https://example.com)")
    REQUEST_DELAY_SEC: float = float(os.getenv("REQUEST_DELAY_SEC", "1.0"))
    MAX_REQUESTS_PER_DOMAIN: int = int(os.getenv("MAX_REQUESTS_PER_DOMAIN", "5"))

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_APP_PASSWORD: str = os.getenv("SMTP_APP_PASSWORD", "")
    FROM_NAME: str = os.getenv("FROM_NAME", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "")

    COUNTRY: str = os.getenv("COUNTRY", "United States")
    INDUSTRY_KEYWORDS: str = os.getenv("INDUSTRY_KEYWORDS", "MICE,Incentives,Meetings,Conference,Exhibition,Event Planning,Event Agency,Corporate Events")


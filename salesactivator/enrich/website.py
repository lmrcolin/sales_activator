from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional
from salesactivator.utils.http import Http
from salesactivator.utils.text import extract_emails, extract_phones
from salesactivator.utils.text import is_email_valid


class WebsiteEnricher:
    def __init__(self, http: Http):
        self.http = http

    def normalize_website(self, url: str) -> Optional[str]:
        if not url:
            return None
        if not url.startswith("http"):
            url = "https://" + url
        return url.rstrip('/').lower()

    def find_root_domain(self, url: str) -> Optional[str]:
        try:
            p = urlparse(url)
            return p.netloc
        except Exception:
            return None

    def fetch_candidate_pages(self, base_url: str) -> List[str]:
        pages = [base_url]
        # Try common contact/about pages
        for path in ("/contact", "/contact-us", "/about", "/team"):
            pages.append(urljoin(base_url + '/', path.strip('/')))
        return pages

    def extract_company_info(self, html: str) -> Dict:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True)
        emails = extract_emails(text)
        phones = extract_phones(text)
        title = soup.title.get_text(strip=True) if soup.title else None
        return {
            "emails": emails,
            "phones": phones,
            "title": title,
        }

    def enrich(self, website: str) -> Dict:
        url = self.normalize_website(website)
        if not url:
            return {}
        pages = self.fetch_candidate_pages(url)
        data = {"emails": set(), "phones": set(), "title": None}
        for p in pages:
            resp = self.http.get(p)
            if not resp:
                continue
            info = self.extract_company_info(resp.text)
            data["emails"].update(info.get("emails", []))
            data["phones"].update(info.get("phones", []))
            if not data["title"]:
                data["title"] = info.get("title")
        # fallback generic email if none
        if not data["emails"]:
            domain = self.find_root_domain(url)
            if domain:
                generic = f"info@{domain}"
                if is_email_valid(generic):
                    data["emails"].add(generic)
        data["emails"] = list(data["emails"])  # type: ignore
        data["phones"] = list(data["phones"])  # type: ignore
        return data

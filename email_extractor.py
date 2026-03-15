import requests
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_contact_from_website(url: str) -> dict:
    """Visit a business website and extract email + phone"""
    empty = {"email": "N/A", "phone": "N/A"}

    if not url or url == "N/A":
        return empty

    try:
        if not url.startswith("http"):
            url = "https://" + url

        response = requests.get(url, headers=HEADERS, timeout=6)
        text = response.text

        # ── Extract Email ─────────────────────────────────
        emails = re.findall(
            r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
            text
        )
        email_blacklist = [
            "example.com", "sentry.io", "wix.com", "domain.com",
            "youremail", "test.com", "sentry", ".png", ".jpg",
            ".svg", ".css", ".js", "schema.org", "w3.org"
        ]
        clean_emails = [
            e for e in emails
            if not any(b in e.lower() for b in email_blacklist)
            and len(e) < 60
        ]
        email = clean_emails[0] if clean_emails else "N/A"

        # ── Extract Phone ─────────────────────────────────
        # Matches formats: +1 212-555-0100, (212) 555-0100, 212.555.0100
        phones = re.findall(
            r'(\+?1?\s?[\(\-\.]?\d{3}[\)\-\.\s]\s?\d{3}[\-\.\s]\d{4})',
            text
        )
        # Clean up whitespace
        clean_phones = [re.sub(r'\s+', ' ', p).strip() for p in phones]
        # Filter out things that look like dates/zip codes
        clean_phones = [
            p for p in clean_phones
            if len(p) >= 10
        ]
        phone = clean_phones[0] if clean_phones else "N/A"

        return {"email": email, "phone": phone}

    except Exception:
        return empty


def enrich_with_contacts(businesses: list) -> list:
    """Loop through all businesses and extract emails + phones"""
    print(f"  → Extracting contacts from {len(businesses)} websites...")

    for i, biz in enumerate(businesses):
        website = biz.get("website", "N/A")
        contacts = extract_contact_from_website(website)

        biz["email"] = contacts["email"]
        biz["phone"] = contacts["phone"]

        email_status = f"📧 {contacts['email']}" if contacts["email"] != "N/A" else "❌ No email"
        phone_status = f"📞 {contacts['phone']}" if contacts["phone"] != "N/A" else "❌ No phone"

        print(f"     [{i+1}/{len(businesses)}] {biz.get('name', '')[:28]:<28} | {email_status} | {phone_status}")
        time.sleep(0.5)

    found_emails = sum(1 for b in businesses if b.get("email") != "N/A")
    found_phones = sum(1 for b in businesses if b.get("phone") != "N/A")
    print(f"\n  → Emails found: {found_emails}/{len(businesses)}")
    print(f"  → Phones found: {found_phones}/{len(businesses)}")
    return businesses
"""Regex entity extractor and normalizer for SentryMesh Guardian.

Extracts Indicators of Compromise (IOCs):
  - URLs and FQDN domains
  - Email addresses
  - Phone numbers (+91, Indian national, international formats)
  - UPI IDs (*@okhdfcbank, *@paytm, *@invalid, etc.)
  - Financial amounts (₹, INR, Rs., USD)

Privacy Redaction:
  - Generates tokenized invariant text (<URL>, <EMAIL>, <PHONE>, <UPI_ID>, <MONEY>)
  - Masks sensitive user identifiers in public or display contexts
"""

import re
import unicodedata
from urllib.parse import urlparse
from typing import Dict, List, Any


def normalize_input_text(text: str) -> str:
    """Cleans Unicode characters, zero-width spaces, and superfluous whitespace."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u200B-\u200D\uFEFF\u00AD]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_entities(text: str) -> Dict[str, Any]:
    """Extracts IOCs from raw or normalized text."""
    clean = normalize_input_text(text)

    # 1. URLs
    url_pattern = r"(?:https?:\/\/|www\.)[^\s<>\"]+|[a-zA-Z0-9-]+\.(?:com|org|net|in|io|xyz|top|app|me|co|info|biz)(?:\/[^\s<>\"]*)?"
    raw_urls = re.findall(url_pattern, clean, flags=re.IGNORECASE)
    # Deduplicate while preserving order
    urls = list(dict.fromkeys(raw_urls))

    # Parse domains
    domains = []
    for u in urls:
        parsed = urlparse(u if "://" in u else f"http://{u}")
        host = parsed.netloc or parsed.path.split("/")[0]
        if host:
            domains.append(host.lower())
    domains = list(dict.fromkeys(domains))

    # 2. Emails
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    raw_emails = re.findall(email_pattern, clean)
    emails = list(dict.fromkeys(raw_emails))

    # 3. UPI IDs
    upi_pattern = r"\b[a-zA-Z0-9_.-]+@(?:invalid|okhdfcbank|okaxis|okicici|paytm|ybl|apl|upi|axl|ibl|barodampay|pnb|sbi)\b"
    raw_upis = re.findall(upi_pattern, clean, flags=re.IGNORECASE)
    upi_ids = list(dict.fromkeys(raw_upis))

    # Filter out emails that may have collided with UPI handles
    emails = [e for e in emails if not any(e.lower() == u.lower() for u in upi_ids)]

    # 4. Amounts / Monetary tokens
    money_pattern = r"(?:Rs\.?|INR|₹|\$)\s*[\d,]+(?:\.\d+)?|\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:rupees|INR|USD)\b"
    raw_amounts = re.findall(money_pattern, clean, flags=re.IGNORECASE)
    amounts = list(dict.fromkeys(raw_amounts))

    # 5. Phone numbers
    phone_pattern = r"(?:\+91[\-\s]?)?[6-9]\d{9}|\+91\s*00000\s*00000|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    raw_phones = re.findall(phone_pattern, clean)
    phone_numbers = list(dict.fromkeys(raw_phones))

    return {
        "urls": urls,
        "domains": domains,
        "emails": emails,
        "phone_numbers": phone_numbers,
        "upi_ids": upi_ids,
        "amounts": amounts
    }


def create_tokenized_text(text: str) -> str:
    """Replaces IOCs with standard representation tokens for semantic invariance."""
    s = normalize_input_text(text)

    # Replace URLs
    url_pattern = r"(?:https?:\/\/|www\.)[^\s<>\"]+|[a-zA-Z0-9-]+\.(?:com|org|net|in|io|xyz|top|app|me|co|info|biz)(?:\/[^\s<>\"]*)?"
    s = re.sub(url_pattern, "<URL>", s, flags=re.IGNORECASE)

    # Replace Emails
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    s = re.sub(email_pattern, "<EMAIL>", s)

    # Replace UPI
    upi_pattern = r"\b[a-zA-Z0-9_.-]+@(?:invalid|okhdfcbank|okaxis|okicici|paytm|ybl|apl|upi|axl|ibl|barodampay|pnb|sbi)\b"
    s = re.sub(upi_pattern, "<UPI_ID>", s, flags=re.IGNORECASE)

    # Replace Amounts
    money_pattern = r"(?:Rs\.?|INR|₹|\$)\s*[\d,]+(?:\.\d+)?|\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:rupees|INR|USD)\b"
    s = re.sub(money_pattern, "<MONEY>", s, flags=re.IGNORECASE)

    # Replace Phones
    phone_pattern = r"(?:\+91[\-\s]?)?[6-9]\d{9}|\+91\s*00000\s*00000|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    s = re.sub(phone_pattern, "<PHONE>", s)

    return re.sub(r"\s+", " ", s).strip()


def mask_pii(text: str) -> str:
    """Masks sensitive elements for public or community logging views."""
    s = text

    # Mask Indian phones: +91 98765 43210 -> +91 XXXXX XX210
    def mask_phone_match(m):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) >= 10:
            last3 = digits[-3:]
            return f"+91 XXXXX XX{last3}"
        return "+91 XXXXX XXXXX"

    s = re.sub(r"(?:\+91[\-\s]?)?[6-9]\d{9}", mask_phone_match, s)

    # Mask UPI: rahul.sharma@paytm -> r***@paytm
    def mask_upi_match(m):
        val = m.group(0)
        parts = val.split("@")
        if len(parts) == 2:
            handle = parts[0]
            masked_handle = handle[0] + "***" if len(handle) > 1 else "***"
            return f"{masked_handle}@{parts[1]}"
        return "***@invalid"

    s = re.sub(r"\b[a-zA-Z0-9_.-]+@(?:invalid|okhdfcbank|okaxis|okicici|paytm|ybl|apl|upi)\b", mask_upi_match, s)
    return s

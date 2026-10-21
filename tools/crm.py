"""Mock CRM. The FastAPI service in crm_service/ exposes the same data over HTTP."""
from __future__ import annotations

CUSTOMERS: dict[str, dict] = {
    "+919800000001": {"name": "Rahul Sharma", "preferred_lang": "en", "pre_approved_amount": 500000,
                      "offer_rate": 11.5, "default_tenure": 36, "dnc": False},
    "+919800000002": {"name": "Priya Verma", "preferred_lang": "hinglish", "pre_approved_amount": 300000,
                      "offer_rate": 12.0, "default_tenure": 24, "dnc": False},
    "+919800000003": {"name": "Suresh Patel", "preferred_lang": "hi", "pre_approved_amount": 800000,
                      "offer_rate": 10.75, "default_tenure": 48, "dnc": False},
    "+919800000004": {"name": "Anita Rao", "preferred_lang": "en", "pre_approved_amount": 200000,
                      "offer_rate": 13.0, "default_tenure": 24, "dnc": True},
}


def crm_lookup(phone: str) -> dict:
    record = CUSTOMERS.get(phone)
    return {"found": False, "phone": phone} if record is None else {"found": True, "phone": phone, **record}


def mark_dnc(phone: str) -> dict:
    if phone in CUSTOMERS:
        CUSTOMERS[phone]["dnc"] = True
    return {"phone": phone, "dnc": True}

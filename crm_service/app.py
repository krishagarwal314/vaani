"""Mock CRM + scheduler API. Run: uvicorn crm_service.app:app --reload"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tools.crm import crm_lookup, mark_dnc
from tools.scheduler import CALLBACKS, book_callback

app = FastAPI(title="Vaani mock CRM")


class CallbackRequest(BaseModel):
    phone: str
    time: str


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/customers/{phone}")
def get_customer(phone: str) -> dict:
    record = crm_lookup(phone)
    if not record["found"]:
        raise HTTPException(404, "customer not found")
    return record


@app.post("/customers/{phone}/dnc")
def set_dnc(phone: str) -> dict:
    return mark_dnc(phone)


@app.post("/callbacks", status_code=201)
def create_callback(req: CallbackRequest) -> dict:
    result = book_callback(req.time, phone=req.phone)
    if not result["booked"]:
        raise HTTPException(422, result["error"])
    return result


@app.get("/callbacks")
def list_callbacks() -> list[dict]:
    return CALLBACKS

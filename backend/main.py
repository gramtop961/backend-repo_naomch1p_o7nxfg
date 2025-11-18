from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from database import db, create_document, get_documents
import os

app = FastAPI(title="NOVA Automations API", version="1.0.0")

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Lead(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    budget: Optional[str] = Field(None, max_length=120)
    description: str = Field(..., min_length=10, max_length=5000)


@app.get("/", tags=["root"]) 
async def root():
    return {"status": "ok", "service": "NOVA Automations API"}


@app.get("/test", tags=["health"]) 
async def test():
    # Probe database availability
    try:
        if db is not None:
            # list collections names as a lightweight check
            _ = db.list_collection_names()
            db_ok = True
        else:
            db_ok = False
    except Exception:
        db_ok = False
    return {"ok": True, "db": db_ok}


@app.post("/leads", tags=["leads"])
async def create_lead(payload: Lead, background: BackgroundTasks):
    # Persist the lead
    try:
        lead_id = create_document("lead", payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    # Simulate email send in background (stub)
    def send_email_stub(name: str, email: str):
        # In a real app, integrate with Sendgrid/SES
        print(f"New lead: {name} <{email}>")

    background.add_task(send_email_stub, payload.name, payload.email)
    return {"ok": True, "id": lead_id}


class Testimonial(BaseModel):
    name: str
    role: str
    quote: str
    avatar: Optional[str] = None


@app.get("/testimonials", response_model=List[Testimonial], tags=["content"]) 
async def get_testimonials():
    # Static seed content; could be moved to DB later
    return [
        Testimonial(name="Maya Patel", role="COO, Horizon", quote="They automated our onboarding and support. NPS went up and costs went down.", avatar=None),
        Testimonial(name="James Turner", role="Head of Sales, Northbeam", quote="The AI SDR added pipeline from day one. We booked 4.7x more demos.", avatar=None),
        Testimonial(name="Lena Fischer", role="CX Lead, Lumos", quote="Agent-first helpdesk deflected 52% of tickets, with seamless escalation.", avatar=None),
    ]

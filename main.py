import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Contact as ContactSchema, Consultation as ConsultationSchema, BlogPost as BlogPostSchema, Resource as ResourceSchema

app = FastAPI(title="UniGrasp API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "UniGrasp Career Counseling API"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# Request models for validation
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: Optional[str] = None
    interest: Optional[str] = None


class ConsultationRequest(BaseModel):
    name: str
    email: EmailStr
    preferred_time: Optional[str] = None
    notes: Optional[str] = None
    plan: Optional[str] = None


# Create sample data on first run if collections are empty
@app.on_event("startup")
async def seed_data():
    if db is None:
        return
    # Seed blogs
    if db["blogpost"].count_documents({}) == 0:
        samples: List[dict] = [
            {
                "title": "Breaking Into Tech: A Practical Roadmap",
                "slug": "breaking-into-tech-roadmap",
                "excerpt": "Step-by-step plan to land your first role in tech without prior experience.",
                "content": "Learn how to assess your strengths, pick a path (PM, Data, SWE, Design), build a portfolio, and network effectively.",
                "author": "UniGrasp Team",
                "tags": ["career", "tech", "beginner"]
            },
            {
                "title": "Resume Framework That Passes ATS",
                "slug": "resume-framework-ats",
                "excerpt": "A battle-tested resume structure that recruiters love.",
                "content": "Use the CAR method (Challenge-Action-Result), keyword optimization, and quantified impact to stand out.",
                "author": "UniGrasp Team",
                "tags": ["resume", "ats", "hiring"]
            }
        ]
        for s in samples:
            db["blogpost"].insert_one(s)

    # Seed resources
    if db["resource"].count_documents({}) == 0:
        resources = [
            {
                "title": "Resume Template (Google Docs)",
                "category": "Resume",
                "url": "https://docs.google.com",
                "description": "Clean, ATS-friendly resume template."
            },
            {
                "title": "Behavioral Interview Question Bank",
                "category": "Interview",
                "url": "https://www.interviewbit.com/behavioral-interview-questions/",
                "description": "Comprehensive list with sample answers."
            }
        ]
        for r in resources:
            db["resource"].insert_one(r)


@app.post("/api/contact")
def submit_contact(payload: ContactRequest):
    data = ContactSchema(**payload.model_dump())
    try:
        inserted_id = create_document("contact", data)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/consultation")
def schedule_consultation(payload: ConsultationRequest):
    data = ConsultationSchema(**payload.model_dump())
    try:
        inserted_id = create_document("consultation", data)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blogs")
def list_blogs(limit: int = 20):
    try:
        docs = get_documents("blogpost", {}, limit)
        # Convert ObjectIds
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resources")
def list_resources(limit: int = 50, category: Optional[str] = None):
    try:
        flt = {"category": category} if category else {}
        docs = get_documents("resource", flt, limit)
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

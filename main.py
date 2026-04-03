import csv, io
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from models import Candidate, InterviewMessage, FeedbackInput
from scoring import save_candidate, get_ranked_candidates, update_weights_from_feedback
from interview import chat
from supabase_client import supabase
import traceback

app = FastAPI(title="GenoTek Hiring Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/candidates")
def add_candidate(candidate: Candidate):
    """Submit a candidate for scoring and ranking."""
    try:
        data = candidate.model_dump()
        saved = save_candidate(data)
        return {"message": "Candidate saved", "candidate": saved}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/candidates/bulk")
async def bulk_upload(file: UploadFile = File(...)):
    """Upload a CSV file with multiple candidates."""
    try:
        contents = await file.read()
        reader = csv.DictReader(io.StringIO(contents.decode("utf-8")))
        saved, errors = [], []
        for row in reader:
            try:
                data = {
                    "name": row["name"],
                    "email": row["email"],
                    "python_skills": int(row.get("python_skills", 5)),
                    "ai_ml_experience": int(row.get("ai_ml_experience", 5)),
                    "communication": int(row.get("communication", 5)),
                    "resume_summary": row.get("resume_summary", "")
                }
                saved.append(save_candidate(data))
            except Exception as e:
                errors.append({"row": row.get("name", "?"), "error": str(e)})
        return {"saved": len(saved), "errors": errors}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/candidates/ranked")
def ranked_candidates():
    """Get all candidates ranked by score."""
    return get_ranked_candidates()

@app.post("/interview")
def interview(msg: InterviewMessage):
    """Send a message to the interview agent for a candidate."""
    try:
        reply = chat(msg.candidate_id, msg.message)
        return {"reply": reply}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
def feedback(data: FeedbackInput):
    """Record hire/reject outcome to improve scoring weights."""
    supabase.table("candidates").update({"hired": data.hired}).eq("id", data.candidate_id).execute()
    updated_weights = update_weights_from_feedback()
    return {"message": "Feedback recorded", "updated_weights": updated_weights}

@app.get("/")
def root():
    return {"status": "GenoTek Hiring Agent running"}

from pydantic import BaseModel
from typing import Optional, List

class Candidate(BaseModel):
    name: str
    email: str
    python_skills: int        # 1-10
    ai_ml_experience: int     # 1-10
    communication: int        # 1-10
    resume_summary: Optional[str] = ""

class InterviewMessage(BaseModel):
    candidate_id: str
    message: str

class FeedbackInput(BaseModel):
    candidate_id: str
    hired: bool

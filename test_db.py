from supabase_client import supabase
from scoring import save_candidate

try:
    data = {
        "name": "Test",
        "email": "test@test.com",
        "python_skills": 7,
        "ai_ml_experience": 5,
        "communication": 6,
        "resume_summary": "test"
    }
    result = save_candidate(data)
    print("Saved:", result)
except Exception as e:
    import traceback
    traceback.print_exc()

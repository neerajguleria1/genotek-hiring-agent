from groq import Groq
from supabase_client import supabase
from dotenv import load_dotenv
import os, json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a technical interviewer at GenoTek hiring for an AI Agent Developer Intern role.
Your job is to assess candidates on Python skills, AI/ML experience, and communication.
Ask one focused question at a time. After each answer, ask a follow-up that goes deeper to detect if they truly understand or just pasted an AI response.
Be concise and professional. After 4 exchanges, output a JSON summary like:
{"verdict": "strong/weak/average", "ai_detected": true/false, "notes": "..."}"""

def get_history(candidate_id: str):
    result = supabase.table("interviews").select("history").eq("candidate_id", candidate_id).execute()
    if result.data:
        return result.data[0]["history"]
    return []

def save_history(candidate_id: str, history: list):
    existing = supabase.table("interviews").select("id").eq("candidate_id", candidate_id).execute()
    if existing.data:
        supabase.table("interviews").update({"history": history}).eq("candidate_id", candidate_id).execute()
    else:
        supabase.table("interviews").insert({"candidate_id": candidate_id, "history": history}).execute()

def chat(candidate_id: str, user_message: str) -> str:
    history = get_history(candidate_id)

    if not history:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]

    history.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history
    )

    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    save_history(candidate_id, history)

    # Check if interview is complete and save verdict
    if '"verdict"' in reply:
        try:
            verdict_json = json.loads(reply[reply.index("{"):reply.rindex("}") + 1])
            supabase.table("candidates").update({
                "interview_verdict": verdict_json.get("verdict"),
                "ai_detected": verdict_json.get("ai_detected"),
                "interview_notes": verdict_json.get("notes")
            }).eq("id", candidate_id).execute()
        except Exception:
            pass

    return reply

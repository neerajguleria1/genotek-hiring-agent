from supabase_client import supabase

# Weights — updated by learning loop
WEIGHTS = {"python_skills": 0.4, "ai_ml_experience": 0.4, "communication": 0.2}

def score_candidate(candidate: dict) -> float:
    return round(
        candidate["python_skills"] * WEIGHTS["python_skills"] +
        candidate["ai_ml_experience"] * WEIGHTS["ai_ml_experience"] +
        candidate["communication"] * WEIGHTS["communication"],
        2
    )

def save_candidate(candidate: dict) -> dict:
    score = score_candidate(candidate)
    candidate["score"] = score
    result = supabase.table("candidates").insert(candidate).execute()
    return result.data[0]

def get_ranked_candidates():
    result = supabase.table("candidates").select("*").order("score", desc=True).execute()
    return result.data

def update_weights_from_feedback():
    """Adjust weights based on hired vs rejected outcomes."""
    hired = supabase.table("candidates").select("*").eq("hired", True).execute().data
    rejected = supabase.table("candidates").select("*").eq("hired", False).execute().data

    if len(hired) < 5:
        return WEIGHTS  # not enough data yet

    def avg(data, key):
        return sum(d[key] for d in data) / len(data)

    for key in WEIGHTS:
        hired_avg = avg(hired, key)
        rejected_avg = avg(rejected, key) if rejected else 0
        diff = hired_avg - rejected_avg
        WEIGHTS[key] = round(max(0.1, WEIGHTS[key] + diff * 0.01), 2)

    # Normalize weights to sum to 1
    total = sum(WEIGHTS.values())
    for key in WEIGHTS:
        WEIGHTS[key] = round(WEIGHTS[key] / total, 2)

    return WEIGHTS

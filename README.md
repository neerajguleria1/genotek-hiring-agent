# GenoTek Hiring Agent

An autonomous hiring agent that scores, ranks, and interviews candidates using AI.

**Live Demo:** https://genotek-hiring-agent.netlify.app
**API:** https://genotek-hiring-agent.onrender.com/docs

---

## Features

- **Candidate Scoring** — Automatically scores applicants on Python skills, AI/ML experience, and communication
- **Bulk CSV Upload** — Import 1000+ candidates at once via CSV
- **Autonomous Interviews** — Multi-round AI interviews powered by Llama 3.3 (Groq)
- **AI Detection** — Follow-up questioning logic to detect copy-pasted or AI-generated answers
- **Learning Loop** — Scoring weights auto-adjust based on hire/reject feedback
- **Supabase Memory** — All candidate profiles, scores, and interview transcripts stored persistently

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| LLM | Llama 3.3 via Groq API |
| Database | Supabase (PostgreSQL) |
| Frontend | HTML/CSS/JS |
| Backend Hosting | Render |
| Frontend Hosting | Netlify |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/candidates` | Add and score a candidate |
| POST | `/candidates/bulk` | Bulk upload via CSV |
| GET | `/candidates/ranked` | Get all candidates ranked by score |
| POST | `/interview` | Send message to interview agent |
| POST | `/feedback` | Record hire/reject outcome |

---

## CSV Format

For bulk upload, use this column structure:

```csv
name,email,python_skills,ai_ml_experience,communication,resume_summary
Alice Johnson,alice@example.com,9,8,7,ML engineer with NLP experience
```

---

## Local Setup

1. Clone the repo
```bash
git clone https://github.com/neerajguleria1/genotek-hiring-agent.git
cd genotek-hiring-agent
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create `.env` file
```bash
cp .env.example .env
# Fill in your keys
```

4. Run Supabase schema
```sql
-- Run schema.sql in your Supabase SQL Editor
```

5. Start the server
```bash
uvicorn main:app --reload
```

6. Open `index.html` in your browser

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Your Supabase anon key |
| `GROQ_API_KEY` | Your Groq API key |

---

## Project Structure

```
GenoTek/
├── main.py              # FastAPI app & routes
├── scoring.py           # Candidate scoring & learning loop
├── interview.py         # Autonomous interview agent
├── supabase_client.py   # Supabase connection
├── models.py            # Pydantic data models
├── schema.sql           # Supabase table definitions
├── index.html           # Frontend UI
├── sample_candidates.csv
├── requirements.txt
└── .env.example
```

---

Built for the GenoTek AI Agent Developer challenge.

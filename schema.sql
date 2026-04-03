-- Run this in Supabase SQL Editor

create table candidates (
    id uuid default gen_random_uuid() primary key,
    name text,
    email text,
    python_skills int,
    ai_ml_experience int,
    communication int,
    resume_summary text,
    score float,
    hired boolean,
    interview_verdict text,
    ai_detected boolean,
    interview_notes text,
    created_at timestamp default now()
);

create table interviews (
    id uuid default gen_random_uuid() primary key,
    candidate_id text,
    history jsonb,
    created_at timestamp default now()
);

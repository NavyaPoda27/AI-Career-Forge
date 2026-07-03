import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
 
load_dotenv()
 
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
except Exception:
    GROQ_API_KEY = None
 
GROQ_API_KEY = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
 
 
def rewrite_resume(resume_text, job_description, missing_skills):
    prompt = f"""
You are an expert resume writer with 10+ years of experience helping candidates land jobs at top companies.
 
Your task is to rewrite the candidate's resume to be perfectly tailored for the job description below.
 
CANDIDATE'S CURRENT RESUME:
{resume_text}
 
JOB DESCRIPTION:
{job_description}
 
MISSING SKILLS TO INCORPORATE (where genuinely applicable):
{', '.join(sorted(missing_skills)) if missing_skills else 'None'}
 
STRICT RULES:
1. Never fabricate experience or skills the candidate doesn't have
2. Rewrite existing bullet points to use keywords from the job description
3. Quantify achievements wherever possible (add realistic numbers if vague)
4. Use strong action verbs: Led, Built, Optimized, Reduced, Improved, Designed
5. Mirror the exact terminology used in the job description
6. Keep the same sections but make every line more impactful
7. If a missing skill appears in their projects/experience, highlight it prominently
8. Tone: Formal and professional
9. Format with clear sections: Summary, Education, Experience, Projects, Skills
 
Return the full rewritten resume in clean markdown format.
"""
 
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()
 
 
def generate_summary(resume_text, job_description):
    prompt = f"""
Write a powerful 3-sentence professional summary for a resume.
 
Candidate background:
{resume_text[:1500]}
 
Target job:
{job_description[:1000]}
 
Rules:
- Formal and professional tone
- Mention years of experience, key skills, and career goal
- Tailor it specifically to the job description
- No first person (avoid "I", "my", "me")
- Return ONLY the summary paragraph, nothing else
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()
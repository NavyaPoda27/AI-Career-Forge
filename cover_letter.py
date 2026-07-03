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
 
 
def generate_cover_letter(resume_text, job_description, candidate_name, company_name, role_name):
    prompt = f"""
You are an expert career coach writing a formal professional cover letter.
 
CANDIDATE NAME: {candidate_name}
TARGET COMPANY: {company_name}
TARGET ROLE: {role_name}
 
CANDIDATE RESUME:
{resume_text}
 
JOB DESCRIPTION:
{job_description}
 
Write a compelling, formal cover letter that:
1. Opens with a strong hook referencing the specific role and company
2. Paragraph 1: Why this candidate is perfect for this role (match their experience to JD)
3. Paragraph 2: Highlight 2-3 specific achievements from their resume with impact
4. Paragraph 3: Why they want to work at THIS company specifically (show research)
5. Closes with a confident call to action
6. Tone: Formal and professional throughout
7. Length: 3-4 paragraphs, under 400 words
8. Do NOT use generic phrases like "I am writing to express my interest"
 
Format:
[Date]
 
Dear Hiring Manager,
 
[Body]
 
Sincerely,
{candidate_name}
"""
 
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()
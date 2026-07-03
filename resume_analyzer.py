import re
import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from job_matcher import extract_skills
 
load_dotenv()
 
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
except Exception:
    GROQ_API_KEY = None
 
GROQ_API_KEY = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
 
 
def parse_resume_with_llm(resume_text):
    prompt = f"""
You are an expert resume parser. Extract information from the resume below and return ONLY a valid JSON object — no explanation, no markdown, no code blocks.
 
Resume:
{resume_text}
 
Return exactly this JSON structure:
{{
  "name": "Full name or null",
  "email": "email or null",
  "phone": "phone number or null",
  "education": [
    {{"degree": "...", "institution": "...", "score": "...", "year": "..."}}
  ],
  "experience": [
    {{"title": "...", "company": "...", "duration": "...", "description": "..."}}
  ],
  "projects": [
    {{"name": "...", "description": "...", "technologies": "..."}}
  ],
  "certifications": ["..."],
  "skills": ["..."]
}}
 
Rules:
- Extract ALL projects, do not skip any
- If a field is missing, use null or empty list
- For education include 10th, 12th, degree, masters — everything
- Return ONLY the JSON, nothing else
"""
 
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
 
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
 
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None
 
 
def analyze_resume(resume_text):
    data = parse_resume_with_llm(resume_text)
 
    if not data:
        return "❌ Could not parse resume. Please try again."
 
    skills = extract_skills(resume_text)
 
    # Education
    edu_md = ""
    for e in data.get("education", []):
        parts = [e.get("degree"), e.get("institution"), e.get("score"), e.get("year")]
        line  = " | ".join(p for p in parts if p)
        if line:
            edu_md += f"- {line}\n"
    if not edu_md:
        edu_md = "- Not detected"
 
    # Experience
    exp_md = ""
    for e in data.get("experience", []):
        title    = e.get("title", "")
        company  = e.get("company", "")
        duration = e.get("duration", "")
        desc     = e.get("description", "")
        header   = " @ ".join(p for p in [title, company] if p)
        if duration:
            header += f" ({duration})"
        if header:
            exp_md += f"**{header}**\n"
        if desc:
            exp_md += f"{desc}\n"
        exp_md += "\n"
    if not exp_md:
        exp_md = "- Not detected"
 
    # Projects
    proj_md  = ""
    projects = data.get("projects", [])
    for i, p in enumerate(projects, 1):
        name = p.get("name", f"Project {i}")
        desc = p.get("description", "")
        tech = p.get("technologies", "")
        proj_md += f"**{i}. {name}**\n"
        if desc:
            proj_md += f"{desc}\n"
        if tech:
            proj_md += f"🛠 *{tech}*\n"
        proj_md += "\n"
    if not proj_md:
        proj_md = "- Not detected"
 
    # Certifications
    certs   = data.get("certifications", [])
    cert_md = "\n".join(f"- {c}" for c in certs) if certs else "- Not detected"
 
    # Strength score
    strength  = 0
    breakdown = []
 
    if skills:
        strength += 25
        breakdown.append(f"✅ Skills detected ({len(skills)})")
    else:
        breakdown.append("❌ No skills detected")
 
    if data.get("email"):
        strength += 10
        breakdown.append("✅ Email found")
    else:
        breakdown.append("❌ No email found")
 
    if data.get("education"):
        strength += 20
        breakdown.append("✅ Education found")
    else:
        breakdown.append("❌ No education detected")
 
    if data.get("experience"):
        strength += 20
        breakdown.append("✅ Experience found")
    else:
        breakdown.append("⚠️ No experience detected")
 
    if projects:
        strength += 15
        breakdown.append(f"✅ Projects found ({len(projects)})")
    else:
        breakdown.append("❌ No projects detected")
 
    word_count = len(resume_text.split())
    if word_count > 250:
        strength += 10
        breakdown.append("✅ Good resume length")
    else:
        breakdown.append("⚠️ Resume seems short")
 
    strength_label = (
        "🟢 Strong" if strength >= 80
        else "🟡 Average" if strength >= 50
        else "🔴 Needs Work"
    )
 
    analysis = f"""
### 👤 Candidate Info
- **Name:** {data.get('name') or 'Not detected'}
- **Email:** {data.get('email') or 'Not found'}
- **Phone:** {data.get('phone') or 'Not found'}
 
---
 
### 🎓 Education
{edu_md}
---
 
### 💼 Experience
{exp_md}
---
 
### 🗂️ Projects ({len(projects)} found)
{proj_md}
---
 
### 🏆 Certifications
{cert_md}
 
---
 
### 🛠️ Detected Skills ({len(skills)})
{', '.join(f'`{s}`' for s in sorted(skills)) if skills else 'None detected'}
 
---
 
### 📊 Resume Stats
- **Word Count:** {word_count}
- **Resume Strength:** {strength_label} ({strength}/100)
- **Breakdown:**
{chr(10).join(f'  {b}' for b in breakdown)}
"""
 
    return analysis
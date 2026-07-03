import re
import os
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
 
load_dotenv()
 
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
except Exception:
    GROQ_API_KEY = None
 
GROQ_API_KEY = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)
model = SentenceTransformer("all-MiniLM-L6-v2")
 
SKILL_ALIASES = {
    "python": ["python", "python3", "py"],
    "javascript": ["javascript", "js", "es6", "es2015"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "reactjs", "react.js", "react js"],
    "next.js": ["nextjs", "next.js", "next js"],
    "node.js": ["nodejs", "node.js", "node js"],
    "nest.js": ["nestjs", "nest.js", "nest js"],
    "vue.js": ["vuejs", "vue.js", "vue js", "vue"],
    "angular": ["angular", "angularjs", "angular.js"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c#": ["c#", "csharp", "c sharp"],
    "golang": ["golang", "go lang", "go"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "mssql"],
    "mongodb": ["mongodb", "mongo", "mongo db"],
    "aws": ["aws", "amazon web services", "amazon aws"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "azure": ["azure", "microsoft azure"],
    "docker": ["docker", "dockerfile", "docker compose"],
    "kubernetes": ["kubernetes", "k8s", "kube"],
    "git": ["git", "github", "gitlab", "bitbucket"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api"],
    "spring boot": ["spring boot", "springboot", "spring"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "scss", "sass", "tailwind", "bootstrap"],
    "rest api": ["rest", "rest api", "restful", "restful api"],
    "graphql": ["graphql", "graph ql"],
    "linux": ["linux", "ubuntu", "unix", "bash", "shell"],
    "machine learning": ["machine learning", "ml", "sklearn", "scikit-learn"],
    "deep learning": ["deep learning", "dl", "neural network", "neural networks"],
    "nlp": ["nlp", "natural language processing", "spacy", "nltk"],
    "data structures": ["data structures", "dsa", "algorithms", "data structures and algorithms"],
    "redis": ["redis", "redis cache"],
    "kafka": ["kafka", "apache kafka"],
    "langchain": ["langchain", "lang chain"],
    "openai": ["openai", "open ai", "gpt", "gpt-4", "chatgpt"],
}
 
 
def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s\+\#\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text
 
 
def extract_skills(text):
    text = normalize_text(text)
    found_canonical = set()
    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = re.escape(alias)
            if re.search(r"(?<!\w)" + pattern + r"(?!\w)", text):
                found_canonical.add(canonical)
                break
    return found_canonical
 
 
def get_smart_suggestions(matched, missing, extra, match_percent):
    if not missing:
        return "Your skills perfectly cover this job description! Focus on quantifying your achievements with numbers."
 
    prompt = f"""
You are an expert career coach reviewing a candidate's resume against a job description.
 
Match score: {match_percent}%
Matched skills: {', '.join(sorted(matched)) if matched else 'none'}
Missing skills: {', '.join(sorted(missing))}
Bonus skills the candidate has: {', '.join(sorted(extra)) if extra else 'none'}
 
Give exactly 5 specific, actionable suggestions to improve their chances of getting this job.
- Be direct and practical
- Reference the actual missing skills by name
- Suggest how to quickly learn or demonstrate each missing skill
- Mention how to leverage their bonus skills as differentiators
- No generic advice like "update your resume" without specifics
 
Format as a numbered list. Each point max 2 sentences.
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"- Could not generate suggestions: {e}"
 
 
def match_resume_to_job(resume_text, job_description):
    # Semantic similarity score (SentenceTransformer)
    resume_emb    = model.encode([resume_text])
    job_emb       = model.encode([job_description])
    score         = cosine_similarity(resume_emb, job_emb)[0][0]
    match_percent = round(float(score) * 100, 2)
 
    # Skill matching
    resume_skills = extract_skills(resume_text)
    job_skills    = extract_skills(job_description)
    matched       = resume_skills & job_skills
    missing       = job_skills - resume_skills
    extra         = resume_skills - job_skills
 
    # AI-powered suggestions (Groq)
    smart_suggestions = get_smart_suggestions(matched, missing, extra, match_percent)
 
    analysis = f"""
### ✅ Matched Skills ({len(matched)})
{', '.join(f'`{s}`' for s in sorted(matched)) if matched else "_None found_"}
 
---
 
### ❌ Missing Skills ({len(missing)})
{', '.join(f'`{s}`' for s in sorted(missing)) if missing else "_None — great coverage!_"}
 
---
 
### ➕ Bonus Skills You Have ({len(extra)})
{', '.join(f'`{s}`' for s in sorted(extra)) if extra else "_None_"}
 
---
 
### 💡 Smart Suggestions (powered by Groq AI)
{smart_suggestions}
 
---
 
### 📝 General Tips
- Quantify achievements (e.g. "Reduced load time by 40%")
- Link your GitHub repos for missing skills
- Mirror keywords from the job description exactly
- Keep resume to 1 page if under 3 years experience
"""
 
    return match_percent, analysis
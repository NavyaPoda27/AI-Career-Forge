# CareerForge – AI-Powered Career Assistant

CareerForge is an AI-powered career assistant that helps job seekers analyze resumes, match them with job descriptions, rewrite resumes for ATS optimization, and generate personalized cover letters using Large Language Models (LLMs).

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## Live Demo
🔗 https://ai-careerforge.streamlit.app/

## GitHub Repository
🔗 https://github.com/NavyaPoda27/AI-Career-Forge

---

## Features

- **Resume Analyzer**
  - Extracts skills, education, and experience from uploaded resumes
  - Provides AI-powered resume insights

- **Job Matcher**
  - Matches resumes with job descriptions
  - Calculates similarity score
  - Identifies missing skills

- **Resume Rewriter**
  - Rewrites resume content to better match job requirements
  - Improves ATS compatibility

- **Cover Letter Generator**
  - Generates personalized cover letters based on resume and job description

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Programming Language | Python |
| UI | Streamlit |
| LLM | Groq API (Llama Models) |
| Resume Parsing | pdfplumber |
| NLP | SentenceTransformers |
| Similarity Search | FAISS + Cosine Similarity |

---

## Run Locally

```bash
git clone https://github.com/NavyaPoda27/AI-Career-Forge.git
cd AI-Career-Forge

pip install -r requirements.txt

# Add your GROQ_API_KEY to .env

streamlit run app.py
```

---

## Project Structure

```
AI-Career-Forge/
│
├── app.py
├── resume_analyzer.py
├── job_matcher.py
├── resume_rewriter.py
├── cover_letter.py
├── rag_engine.py
├── utils.py
├── requirements.txt

```

---

## Screenshots

### Home Page
<img width="1913" height="1085" alt="Screenshot 2026-07-03 162638" src="https://github.com/user-attachments/assets/ed886af1-4c53-4fec-80e4-72540382490a" />

### Resume Analysis
<img width="1908" height="983" alt="Screenshot 2026-07-03 162724" src="https://github.com/user-attachments/assets/e5594d2d-13c6-42ba-aaaf-757e4053ef06" />

---

## Future Enhancements

- User authentication
- Resume history
- Interview question generator
- Skill-gap learning roadmap
- Real-time job search integration
- Resume score dashboard

---

## 👩‍💻 Author

**Navya P**

GitHub: https://github.com/NavyaPoda27

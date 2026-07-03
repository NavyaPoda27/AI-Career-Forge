import os
import faiss
import numpy as np
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Lazy globals — loaded only when first needed ──────────────
_embedder = None
_client   = None


def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


JOB_KNOWLEDGE_BASE = [
    {"id":1,"title":"Frontend Developer","company":"TechCorp","description":"React Next.js JavaScript TypeScript CSS HTML Git REST API GraphQL Redux Tailwind"},
    {"id":2,"title":"Full Stack Developer","company":"StartupXYZ","description":"React Node.js MongoDB Express SQL Git REST API Docker AWS JavaScript HTML CSS"},
    {"id":3,"title":"Backend Developer","company":"FinTech Inc","description":"Python Django Flask PostgreSQL Redis Docker Microservices REST API Kubernetes AWS Kafka"},
    {"id":4,"title":"Machine Learning Engineer","company":"AI Labs","description":"Python Machine Learning Deep Learning NLP scikit-learn LLMs LangChain FAISS PyTorch TensorFlow SQL Git"},
    {"id":5,"title":"Data Scientist","company":"Analytics Pro","description":"Python Machine Learning scikit-learn pandas numpy matplotlib seaborn SQL Jupyter regression classification clustering"},
    {"id":6,"title":"AI NLP Engineer","company":"NLP Innovations","description":"Python NLP spaCy NLTK transformers LangChain deep learning FAISS vector databases RAG pipelines text classification"},
    {"id":7,"title":"Generative AI Engineer","company":"GenAI Studios","description":"Python LangChain OpenAI Groq FAISS RAG prompt engineering vector databases Pinecone embeddings Hugging Face"},
    {"id":8,"title":"Data Engineer","company":"DataCo","description":"Python SQL PostgreSQL MongoDB Kafka ETL pipelines AWS GCP Spark Airflow Docker data warehousing"},
    {"id":9,"title":"DevOps Engineer","company":"CloudSystems","description":"Docker Kubernetes AWS GCP Linux Git CI/CD Terraform Bash Jenkins GitHub Actions monitoring"},
    {"id":10,"title":"Java Developer","company":"EnterpriseGlobal","description":"Java Spring Boot SQL REST API Git Maven microservices Docker Kafka AWS"},
    {"id":11,"title":"Web Developer","company":"CreativeAgency","description":"HTML CSS JavaScript React Vue Git responsive design Bootstrap Tailwind REST API WordPress"},
    {"id":12,"title":"Django Developer","company":"WebSolutions","description":"Python Django REST API PostgreSQL HTML CSS JavaScript React Git Docker authentication ORM AWS"},
    {"id":13,"title":"Computer Vision Engineer","company":"VisionTech","description":"Python Deep Learning OpenCV PyTorch TensorFlow image processing object detection CNNs YOLO"},
    {"id":14,"title":"Cloud Engineer","company":"CloudNative","description":"AWS GCP Azure Docker Kubernetes Terraform Linux CI/CD serverless Prometheus Grafana"},
    {"id":15,"title":"Software Development Engineer","company":"BigTechCo","description":"Data structures algorithms Python Java C++ Git system design REST API SQL microservices"},
    {"id":16,"title":"React Native Developer","company":"MobileFirst","description":"React Native React JavaScript TypeScript Git REST API mobile UI Node.js Firebase Redux"},
    {"id":17,"title":"Android Developer","company":"AppFactory","description":"Android Kotlin Java REST API Git Firebase MVVM Jetpack Compose Room Retrofit"},
    {"id":18,"title":"Database Administrator","company":"DataSystems","description":"SQL MySQL PostgreSQL MongoDB Redis Oracle database design query optimization backup Linux"},
    {"id":19,"title":"Cybersecurity Analyst","company":"SecureNet","description":"Linux networking firewalls penetration testing Python SIEM vulnerability assessment ethical hacking SQL"},
    {"id":20,"title":"Business Intelligence Developer","company":"InsightCo","description":"SQL Python Power BI Tableau data warehousing ETL Excel DAX data modeling dashboards"},
]


class RAGEngine:
    def __init__(self):
        self.index     = None
        self.job_store = []
        self._build_index()

    def _build_index(self):
        embedder     = get_embedder()
        descriptions = [job["description"] for job in JOB_KNOWLEDGE_BASE]
        embeddings   = embedder.encode(descriptions, show_progress_bar=False)
        embeddings   = np.array(embeddings).astype("float32")
        faiss.normalize_L2(embeddings)
        dimension    = embeddings.shape[1]
        self.index   = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        self.job_store = JOB_KNOWLEDGE_BASE

    def retrieve_top_jobs(self, resume_text, top_k=3):
        embedder   = get_embedder()
        resume_emb = embedder.encode([resume_text], show_progress_bar=False)
        resume_emb = np.array(resume_emb).astype("float32")
        faiss.normalize_L2(resume_emb)
        scores, indices = self.index.search(resume_emb, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            job = self.job_store[idx].copy()
            job["match_score"] = round(float(score) * 100, 1)
            results.append(job)
        return results

    def generate_rag_insights(self, resume_text, top_jobs):
        client      = get_client()
        job_context = ""
        for i, job in enumerate(top_jobs, 1):
            job_context += f"Job {i}: {job['title']} at {job['company']} (Match: {job['match_score']}%)\n{job['description']}\n---\n"

        prompt = f"""You are an expert career advisor. Do NOT use any candidate name, refer to them as the candidate only.

CANDIDATE RESUME:
{resume_text[:2000]}

TOP MATCHING JOBS:
{job_context}

Provide:
1. Career Profile Summary - what kind of developer are they?
2. Best Fit Role - which job and why?
3. Skill Gap - top 3 skills to learn for best fit role?
4. Career Path - target role in 1 year vs 3 years?
5. Immediate Action Items - 3 things to do this week?

Be specific. Professional tone. Never mention any name."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()


# ── Singleton ─────────────────────────────────────────────────
_instance = None

def get_rag_engine():
    global _instance
    if _instance is None:
        _instance = RAGEngine()
    return _instance
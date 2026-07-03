import streamlit as st
from utils import extract_resume_text
from resume_analyzer import analyze_resume
from job_matcher import match_resume_to_job, extract_skills
from resume_rewriter import rewrite_resume, generate_summary
from cover_letter import generate_cover_letter

st.set_page_config(
    page_title="CareerForge",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #0f1117; color: #ffffff; }

section[data-testid="stSidebar"] {
    background-color: #1a1d27;
    border-right: 1px solid #2e3147;
}

.card {
    background: #1a1d27;
    border: 1px solid #2e3147;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
}

.section-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #7c83ff;
    margin-bottom: 16px;
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    margin: 3px;
}
.badge-green { background: #1a3a2a; color: #4ade80; border: 1px solid #166534; }
.badge-red   { background: #3a1a1a; color: #f87171; border: 1px solid #991b1b; }
.badge-blue  { background: #1a2a3a; color: #60a5fa; border: 1px solid #1e40af; }

.metric-box {
    background: #1a1d27;
    border: 1px solid #2e3147;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.metric-value { font-size: 32px; font-weight: 700; color: #a5aaff; }
.metric-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; }

[data-testid="stFileUploader"] {
    background: #1a1d27 !important;
    border: 2px dashed #6c72ff !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] section {
    background: #1a1d27 !important;
    color: #ffffff !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #1a1d27 !important;
    color: #ffffff !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #c0c4e0 !important;
}

p, li { color: #c0c4e0; }

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: #c0c4e0 !important; }

h1, h2, h3 { color: #ffffff !important; }
strong { color: #ffffff !important; }

[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #6c72ff, #a855f7) !important;
}

textarea {
    background: #1a1d27 !important;
    border: 1px solid #2e3147 !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}
textarea::placeholder { color: #555870 !important; }

.stButton > button {
    background: linear-gradient(135deg, #6c72ff, #a855f7);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    font-weight: 600;
    width: 100%;
    font-size: 16px;
}
.stButton > button:hover { opacity: 0.9; }

hr { border-color: #2e3147; }
[data-testid="stAlert"] { background: #1a1d27 !important; border-radius: 8px !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #1a1d27;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8b8fa8;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6c72ff, #a855f7) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


def gauge_chart(score):
    if score >= 70:
        color = "#4ade80"
        label = "Strong Match"
    elif score >= 50:
        color = "#facc15"
        label = "Moderate Match"
    else:
        color = "#f87171"
        label = "Weak Match"

    angle = -90 + (score / 100) * 180
    dash  = int(score * 3.46)

    return (
        '<div style="display:flex;flex-direction:column;align-items:center;padding:10px 0">'
        '<svg width="260" height="155" viewBox="0 0 260 155">'
        '<path d="M 20 140 A 110 110 0 0 1 240 140" fill="none" stroke="#2e3147" stroke-width="22" stroke-linecap="round"/>'
        f'<path d="M 20 140 A 110 110 0 0 1 240 140" fill="none" stroke="{color}" stroke-width="22" stroke-linecap="round" stroke-dasharray="{dash} 346"/>'
        f'<g transform="translate(130,140) rotate({angle})">'
        '<line x1="0" y1="0" x2="0" y2="-88" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>'
        f'<circle cx="0" cy="0" r="6" fill="{color}"/>'
        '</g>'
        f'<text x="130" y="115" text-anchor="middle" font-size="30" font-weight="700" fill="#ffffff">{score}%</text>'
        f'<text x="130" y="136" text-anchor="middle" font-size="12" fill="{color}">{label}</text>'
        '<text x="20" y="152" text-anchor="middle" font-size="11" fill="#8b8fa8">0</text>'
        '<text x="240" y="152" text-anchor="middle" font-size="11" fill="#8b8fa8">100</text>'
        '</svg></div>'
    )


def skill_badges(skills, badge_class):
    if not skills:
        return "<span style='color:#8b8fa8;font-size:13px'>None</span>"
    return " ".join(f'<span class="badge {badge_class}">{s}</span>' for s in sorted(skills))


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Career Forge")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### ✅ Phase 1")
    st.markdown("✅ Resume Analyzer")
    st.markdown("✅ Job Matcher")
    st.markdown("✅ Gap Analysis")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### ✅ Phase 2")
    st.markdown("✅ Resume Rewriter")
    st.markdown("✅ Cover Letter Generator")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🔜 Phase 3")
    st.markdown("🔜 Interview Agent")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:12px;color:#8b8fa8'>Built with Streamlit · Groq · FAISS</div>",
        unsafe_allow_html=True
    )

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:30px 0 10px'>
  <h1 style='font-size:42px;font-weight:800;
             background:linear-gradient(135deg,#6c72ff,#a855f7);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0'>
    AI CareerForge
  </h1>
  <p style='color:#8b8fa8;font-size:16px;margin-top:8px'>
    Analyze · Match · Rewrite · Apply
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Shared Inputs ─────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="section-title">📄 Your Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF or DOCX", type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} ({round(uploaded_file.size/1024, 1)} KB)")

with col2:
    st.markdown('<div class="section-title">💼 Job Description</div>', unsafe_allow_html=True)
    job_desc = st.text_area(
        "Paste job description here", height=180,
        label_visibility="collapsed",
        placeholder="Paste the job description here..."
    )

st.markdown("<br>", unsafe_allow_html=True)
analyze_btn = st.button("🔍 Analyze & Match My Resume")

# ── Run Analysis & store in session_state ────────────────────
if analyze_btn:
    if not uploaded_file or not job_desc.strip():
        st.warning("⚠️ Please upload a resume and paste a job description.")
    else:
        with st.spinner("Analyzing your resume..."):
            st.session_state.resume_text         = extract_resume_text(uploaded_file)
            st.session_state.analysis            = analyze_resume(st.session_state.resume_text)
            st.session_state.score, st.session_state.gap = match_resume_to_job(
                st.session_state.resume_text, job_desc
            )
            st.session_state.resume_skills       = extract_skills(st.session_state.resume_text)
            st.session_state.job_skills          = extract_skills(job_desc)
            st.session_state.matched             = st.session_state.resume_skills & st.session_state.job_skills
            st.session_state.missing             = st.session_state.job_skills - st.session_state.resume_skills
            st.session_state.extra               = st.session_state.resume_skills - st.session_state.job_skills
            st.session_state.job_desc            = job_desc
            st.session_state.analyzed            = True

# ── Tabs ─────────────────────────────────────────────────────
if st.session_state.get("analyzed"):
    st.markdown("<hr>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📊 Analysis & Match",
        "✍️ Resume Rewriter",
        "💌 Cover Letter"
    ])

    # ── TAB 1: Analysis & Match ───────────────────────────────
    with tab1:
        score       = st.session_state.score
        matched     = st.session_state.matched
        missing     = st.session_state.missing
        extra       = st.session_state.extra
        resume_text = st.session_state.resume_text
        job_skills  = st.session_state.job_skills

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value">{int(score)}%</div>
                <div class="metric-label">Match Score</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value">{len(matched)}</div>
                <div class="metric-label">Skills Matched</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value">{len(missing)}</div>
                <div class="metric-label">Skills Missing</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value">{len(resume_text.split())}</div>
                <div class="metric-label">Resume Words</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        left, right = st.columns(2, gap="large")

        with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎯 Match Score</div>', unsafe_allow_html=True)
            st.markdown(gauge_chart(int(score)), unsafe_allow_html=True)
            st.markdown("**Matched Skills**")
            st.progress(len(matched) / max(len(job_skills), 1))
            st.markdown("**Resume Coverage**")
            st.progress(min(len(resume_text.split()) / 500, 1.0))
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🛠️ Skills Breakdown</div>', unsafe_allow_html=True)
            st.markdown("**✅ Matched**")
            st.markdown(skill_badges(matched, "badge-green"), unsafe_allow_html=True)
            st.markdown("<br>**❌ Missing**", unsafe_allow_html=True)
            st.markdown(skill_badges(missing, "badge-red"), unsafe_allow_html=True)
            st.markdown("<br>**➕ Bonus Skills**", unsafe_allow_html=True)
            st.markdown(skill_badges(extra, "badge-blue"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Resume Analysis</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.analysis, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧠 Gap Analysis & Suggestions</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.gap, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 2: Resume Rewriter ────────────────────────────────
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">✍️ AI Resume Rewriter</div>', unsafe_allow_html=True)
        st.markdown("Rewrites your resume bullets to match the job description — using your real experience, no fabrication.")

        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            if st.button("✨ Generate Tailored Resume"):
                with st.spinner("Rewriting your resume for this role..."):
                    st.session_state.rewritten = rewrite_resume(
                        st.session_state.resume_text,
                        st.session_state.job_desc,
                        st.session_state.missing
                    )
        with col_b:
            if st.button("📝 Generate Professional Summary"):
                with st.spinner("Crafting your professional summary..."):
                    st.session_state.summary = generate_summary(
                        st.session_state.resume_text,
                        st.session_state.job_desc
                    )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.get("summary"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📝 Professional Summary</div>', unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:#0f1117;border-left:3px solid #6c72ff;"
                f"padding:16px;border-radius:4px;color:#c0c4e0;font-style:italic'>"
                f"{st.session_state.summary}</div>",
                unsafe_allow_html=True
            )
            st.download_button(
                "⬇️ Download Summary",
                data=st.session_state.summary,
                file_name="professional_summary.txt",
                mime="text/plain"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.get("rewritten"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">✨ Tailored Resume</div>', unsafe_allow_html=True)
            st.markdown(st.session_state.rewritten)
            st.download_button(
                "⬇️ Download Rewritten Resume",
                data=st.session_state.rewritten,
                file_name="tailored_resume.md",
                mime="text/markdown"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 3: Cover Letter ───────────────────────────────────
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💌 Cover Letter Generator</div>', unsafe_allow_html=True)
        st.markdown("Generate a personalized, formal cover letter tailored to the job.")

        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            candidate_name = st.text_input("Your Full Name", placeholder="Navya Poda")
        with c2:
            company_name = st.text_input("Company Name", placeholder="Google")
        with c3:
            role_name = st.text_input("Role Applying For", placeholder="Software Engineer")

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("💌 Generate Cover Letter"):
            if not candidate_name or not company_name or not role_name:
                st.warning("⚠️ Please fill in your name, company, and role.")
            else:
                with st.spinner("Writing your cover letter..."):
                    st.session_state.cover_letter = generate_cover_letter(
                        st.session_state.resume_text,
                        st.session_state.job_desc,
                        candidate_name,
                        company_name,
                        role_name
                    )

        if st.session_state.get("cover_letter"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📄 Your Cover Letter</div>', unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:#0f1117;border:1px solid #2e3147;"
                f"border-radius:8px;padding:24px;color:#c0c4e0;line-height:1.8;white-space:pre-wrap'>"
                f"{st.session_state.cover_letter}</div>",
                unsafe_allow_html=True
            )
            st.download_button(
                "⬇️ Download Cover Letter",
                data=st.session_state.cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain"
            )
            st.markdown('</div>', unsafe_allow_html=True)
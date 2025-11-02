import os
import re
import io
import pdfplumber
import streamlit as st
from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import Counter

# Optional OpenAI import: handled gracefully if key is missing
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


st.set_page_config(page_title="AI Resume Analyzer", page_icon="🧠", layout="wide")


# ---------- Helpers ----------

STOPWORDS = set("""a an the and or of to for with without in on at from by is are was were be being been
this that these those i you he she it we they them us our your their as into about over under between
so if then than too very just can cannot could would should might may not""".split())

GENERIC_SKILLS = [
    # Core analytics / BI
    "python","sql","excel","power bi","tableau","data visualization","data analysis","statistics",
    "machine learning","forecasting","regression","classification","time series","etl","dashboards",
    # ITSM / process
    "itil","change management","incident management","service now","process improvement","kpis",
    # Cloud / dev
    "aws","azure","gcp","api","git","linux",
    # Soft skills
    "communication","stakeholder management","presentation","problem solving","leadership","collaboration"
]

def normalize_text(text: str) -> str:
    text = text.encode("utf-8","ignore").decode("utf-8","ignore")
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z\-\+\.#0-9]*", text.lower())
    return [t for t in tokens if t not in STOPWORDS]

def top_keywords(text: str, n: int = 25) -> List[Tuple[str, int]]:
    tokens = tokenize(text)
    counts = Counter(tokens)
    # down-weight extremely short tokens
    for k in list(counts.keys()):
        if len(k) < 3:
            counts[k] = int(counts[k] * 0.5)
    return counts.most_common(n)

def extract_pdf_text(file) -> str:
    try:
        full = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                full.append(page.extract_text() or "")
        return "\n".join(full)
    except Exception as e:
        return ""

def read_resume(uploaded_file, pasted_text: str) -> str:
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
            return extract_pdf_text(uploaded_file)
        elif uploaded_file.name.lower().endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore")
        else:
            return uploaded_file.read().decode("utf-8", errors="ignore")
    return pasted_text or ""

def skill_coverage(resume_text: str, skills: List[str]) -> Tuple[float, List[str], List[str]]:
    r = normalize_text(resume_text)
    present, missing = [], []
    for s in skills:
        pattern = r"\b" + re.escape(s) + r"\b"
        if re.search(pattern, r):
            present.append(s)
        else:
            missing.append(s)
    coverage = 0.0 if not skills else len(present)/len(skills)
    return coverage, present, missing

def keyword_alignment(resume_text: str, jd_text: str, n: int = 25) -> Tuple[float, List[Tuple[str,int]], List[str]]:
    jd_top = [kw for kw,_ in top_keywords(jd_text, n)]
    r_tokens = set(tokenize(resume_text))
    overlap = [kw for kw in jd_top if kw in r_tokens]
    score = 0.0 if not jd_top else len(overlap)/len(jd_top)
    return score, list(zip(jd_top, [1]*len(jd_top))), overlap

def quick_readability(text: str) -> Dict[str, float]:
    sentences = re.split(r"[\.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = tokenize(text)
    chars = sum(len(w) for w in words)
    avg_sent_len = (len(words)/len(sentences)) if sentences else 0
    avg_word_len = (chars/len(words)) if words else 0
    return {
        "word_count": float(len(words)),
        "sentence_count": float(len(sentences)),
        "avg_sentence_length_words": float(round(avg_sent_len,2)),
        "avg_word_length_chars": float(round(avg_word_len,2))
    }

def qualitative_feedback(resume_text: str, jd_text: str) -> str:
    api_key = None
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    elif "OPENAI_API_KEY" in os.environ:
        api_key = os.environ.get("OPENAI_API_KEY")

    system_prompt = (
        "You are a concise career advisor. Given a resume and a job description, "
        "provide: (1) 3-5 specific bullet-point improvements to the resume to better match the role, "
        "(2) 8-12 ATS keywords that should appear (comma separated), and (3) a 2-sentence summary of fit."
    )
    user_prompt = f"JOB DESCRIPTION:\n{jd_text}\n\nRESUME:\n{resume_text}"

    if api_key and OPENAI_AVAILABLE:
        try:
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"AI feedback unavailable ({e}). Showing rule-based tips below.\n" + rule_based_tips(resume_text, jd_text)
    else:
        return "AI feedback unavailable (no API key). Showing rule-based tips below.\n" + rule_based_tips(resume_text, jd_text)

def rule_based_tips(resume_text: str, jd_text: str) -> str:
    _, _, overlap = keyword_alignment(resume_text, jd_text, n=25)
    coverage, present, missing = skill_coverage(resume_text, GENERIC_SKILLS)
    missing_top = ", ".join(missing[:8]) if missing else "None"
    return (
        "- Tailor your summary to mirror the job title and top requirements.\n"
        "- Add 2–3 quantifiable bullets per role (impact %, time saved, $ value).\n"
        f"- Ensure these common skills appear if relevant: {missing_top}.\n"
        f"- Add role-specific keywords from the JD (you currently match {len(overlap)} of the top terms).\n"
        "- Keep lines concise (under ~2 lines per bullet) and use strong action verbs."
    )


# ---------- UI ----------
st.title("🧠 AI-Powered Resume Analyzer")
st.caption("Upload your resume and paste a job description to get alignment scoring, keyword coverage, and AI feedback.")

with st.sidebar:
    st.header("Input")
    uploaded = st.file_uploader("Upload resume (PDF/TXT preferred)", type=["pdf","txt","md","rtf","doc","docx"])
    resume_text_area = st.text_area("Or paste resume text", height=200, placeholder="Paste your resume text if not uploading a PDF/TXT...")
    jd_text = st.text_area("Paste target job description", height=240, placeholder="Paste the job posting or description here...")
    analyze = st.button("Analyze Resume", type="primary")

if analyze:
    resume_text = read_resume(uploaded, resume_text_area)
    if not resume_text.strip():
        st.error("Please upload a resume file or paste resume text.")
        st.stop()
    if not jd_text.strip():
        st.error("Please paste the job description text.")
        st.stop()

    resume_text_n = normalize_text(resume_text)
    jd_text_n = normalize_text(jd_text)

    # Scores
    kw_score, jd_kw, overlap = keyword_alignment(resume_text_n, jd_text_n, n=25)
    skill_score, present_skills, missing_skills = skill_coverage(resume_text_n, GENERIC_SKILLS)
    readability = quick_readability(resume_text_n)

    overall = round((0.6*kw_score + 0.4*skill_score)*100)

    st.subheader("Results")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Overall Alignment", f"{overall}%")
        st.progress(overall/100.0)
    with c2:
        st.metric("JD Keyword Match", f"{int(kw_score*100)}%")
        st.write(f"Matched {len(overlap)} / 25 top JD terms")
    with c3:
        st.metric("Core Skills Coverage", f"{int(skill_score*100)}%")
        st.write(f"{len(present_skills)} present, {len(missing_skills)} missing")

    st.divider()
    st.subheader("Keyword Insights")
    st.write("**Top JD keywords (target):**")
    st.write(", ".join([kw for kw,_ in jd_kw]))
    st.write("**Keywords you already hit:**")
    st.write(", ".join(overlap) if overlap else "None detected")

    st.divider()
    st.subheader("Skills Coverage")
    colA, colB = st.columns(2)
    with colA:
        st.write("✅ Present:")
        st.write(", ".join(sorted(set(present_skills))) if present_skills else "—")
    with colB:
        st.write("⚠️ Missing (consider adding if relevant):")
        st.write(", ".join(sorted(set(missing_skills))) if missing_skills else "—")

    st.divider()
    st.subheader("Readability Snapshot")
    rcols = st.columns(4)
    rcols[0].metric("Words", int(readability["word_count"]))
    rcols[1].metric("Sentences", int(readability["sentence_count"]))
    rcols[2].metric("Avg sentence length (w)", readability["avg_sentence_length_words"])
    rcols[3].metric("Avg word length (chars)", readability["avg_word_length_chars"])

    st.divider()
    st.subheader("AI Feedback & Suggestions")
    fb = qualitative_feedback(resume_text, jd_text)
    st.write(fb)

else:
    st.info("Upload your resume and paste a job description, then click **Analyze Resume** in the sidebar.")
    st.write("Tip: Add your OpenAI key to Streamlit **Secrets** for richer AI feedback.")


st.markdown("""
---
**How to use this app**  
1. Upload a PDF resume or paste your resume text.  
2. Paste the job description.  
3. Click **Analyze Resume**.  
4. Review **Alignment**, **Keyword Match**, **Skills Coverage**, and **AI Feedback**.  
""")
# AI-Powered Resume Analyzer (Streamlit)

A shareable web app that scores resume-to-job alignment, highlights job description keywords, checks skill coverage, and generates AI feedback.

I built this to help people quickly see how well their resume matches a job description and what they could improve before applying.

---

## What It Does
- Upload PDF/TXT resume or paste resume text
- Paste a target job description
- Generates alignment score and keyword overlap
- Shows skill coverage and readability snapshot
- Optional AI-powered suggestions (uses OpenAI API key)

---

## What It Looks Like
![App Screenshot](assets/demo.png)

---

## Tech Stack
- Python
- Streamlit
- NLP keyword extraction
- OpenAI API (optional)
- Pandas / basic text processing

---

## Local Run
```bash
pip install -r requirements.txt
streamlit run app.py

---
Maintainer: Kristal Makhija

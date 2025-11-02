# 🧠 AI-Powered Resume Analyzer (Streamlit)

A shareable web app that scores resume-to-job alignment, highlights JD keywords, checks core skill coverage, and generates AI feedback.

## ✨ Features
- Upload PDF/TXT resume or paste text
- Paste target Job Description
- Alignment score, keyword overlap, skills coverage
- Readability snapshot
- Optional OpenAI-powered suggestions (uses `st.secrets["OPENAI_API_KEY"]`)

## 🚀 1-Click Deploy (Streamlit Community Cloud)
1. **Create a new GitHub repo** and upload these files.
2. Go to **https://share.streamlit.io** → **Deploy an app** → point to your repo.
3. In **Advanced settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
4. Deploy — you'll get a shareable URL for your resume and applications.

## 🧪 Local Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🔐 Hugging Face Spaces (Alternative)
- Create a new Space → **Streamlit** template.
- Upload these files.
- Add a secret `OPENAI_API_KEY` in the Space settings → **Variables and Secrets**.

## 📄 Suggested Resume Bullets
> Built a Streamlit-based AI Resume Analyzer leveraging NLP keyword overlap, skills coverage, and GPT-generated recommendations; delivered interactive alignment scoring and optimization tips for targeted job applications.

---
Maintainer: Kristal Makhija
# ucs503p-202526odd-kaars

# 📌 Job Portal with ATS Resume Scoring

A **job posting and resume optimization platform** that combines web-scraped job listings with an **ATS (Applicant Tracking System) score checker**. Users can upload and edit resumes in real-time, instantly checking how well their resume matches a job description while also browsing relevant openings.

---

## 🚀 Features
- 🔎 **Job Scraping** – Aggregates job postings from multiple websites (via APIs or scraping).
- 📑 **Resume Parsing** – Extracts structured data (skills, education, experience) from PDF/DOCX.
- 📊 **ATS Score Calculator** – Evaluates resume vs. job description based on:
  - Keyword presence
  - Semantic similarity (synonyms, related terms)
  - Weighting across sections (skills, projects, education)
- ⚡ **Real-Time Resume Editing** – Users can modify resumes and see the updated ATS score instantly.
- 🎯 **Job Recommendations** – Ranks jobs by best-fit score for a given resume.
- 📬 **Automated Updates (Optional via n8n)** – Periodic job scraping and email/Slack alerts.
- 🔐 **Data Privacy** – Resumes processed securely without storing sensitive data permanently.

---

## 🛠️ Tech Stack

### Frontend (UI)
- **React.js** – Resume upload, live ATS score updates, job listings.
- **Tailwind CSS / ShadCN UI** – Modern styling and UI components.

### Backend (API)
- **FastAPI** (or Flask) – For resume parsing, ATS scoring, and job matching APIs.
- **Python NLP stack:**
  - `pdfplumber`, `docx2txt` → Resume parsing
  - `spaCy` → Named Entity Recognition (skills, companies)
  - `scikit-learn` → TF-IDF, cosine similarity
  - `sentence-transformers (MiniLM)` → Semantic embeddings

### Database
- **PostgreSQL** / **SQLite** → Job listings + user data.
- **FAISS / ChromaDB** (optional) → Vector search for semantic matching.

### Automation (Optional)
- **n8n** → Automating job scraping, notifications, and batch resume scoring.

### Deployment
- **Backend** → Render / Railway / Heroku / AWS EC2
- **Frontend** →  https://ucs503p-202526odd-kaars.vercel.app/
- **Database** → Supabase / PostgreSQL on cloud

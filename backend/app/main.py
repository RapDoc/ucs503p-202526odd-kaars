from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import docx
import pandas as pd
import json
import re
import google.generativeai as genai
import tempfile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ---------- INIT APP ----------
app = FastAPI(title="Resume Matcher API")

# Serve frontend build
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_frontend():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend build missing. Please deploy with render.yaml ⚙️"}

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- CONFIG ----------
genai.configure(api_key="YOUR_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------- UTILITIES ----------
def extract_text_from_resume(file_path: str):
    text = ""
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.strip()

def parse_resume_with_gemini(resume_text):
    prompt = f"""
    Extract only the skills from the following resume.
    Return only a valid JSON array of strings — nothing else.
    Resume:
    {resume_text}
    """
    response = model.generate_content(prompt)
    output = response.text.strip()
    match = re.search(r'\[.*\]', output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return [s.strip() for s in re.split(r',|\n|;', output) if s.strip()]

def get_job_score(resume_skills, job_skills):
    prompt = f"""
    Return ONLY JSON:
    {{
      "score": number,
      "reason": "short reason"
    }}
    Candidate Skills: {resume_skills}
    Job Skills: {job_skills}
    """
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text)
    except:
        return {"score": 0, "reason": "Parsing error"}

# ---------- LOAD JOB DATA ----------
df_jobs = pd.read_csv("cleaned_jobs_30.csv")
df_jobs['skills_list'] = df_jobs['skills_clean'].fillna('').str.lower().split(', ')

# ---------- API ROUTES ----------
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    resume_text = extract_text_from_resume(tmp_path)
    resume_skills = parse_resume_with_gemini(resume_text)

    return {"skills": resume_skills}

@app.post("/match_jobs")
async def match_jobs(resume_skills: list[str]):
    scores, reasons = [], []

    for _, row in df_jobs.iterrows():
        result = get_job_score(resume_skills, row["skills_list"])
        scores.append(result["score"])
        reasons.append(result["reason"])

    df_jobs["score"] = scores
    df_jobs["reason"] = reasons
    df_sorted = df_jobs.sort_values(by="score", ascending=False).head(10)

    return df_sorted.to_dict(orient="records")

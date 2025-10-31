from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import docx
import pandas as pd
import json
import re
import google.generativeai as genai
import tempfile
import os

# ---------- CONFIG ----------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI(title="Resume Matcher API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    You are a job matching expert. 
    Compare the candidate's skills with the job's required skills.
    Candidate Skills: {', '.join(resume_skills)}
    Job Skills: {', '.join(job_skills)}
    Score (0-100): How compatible is this candidate for this job 
    based only on the overlap and relevance of skills?
    Return ONLY a JSON in this format:
    {{
        "score": number,
        "reason": "brief reason for score"
    }}
    """
    response = model.generate_content(prompt)
    output = response.text.strip()
    output = re.sub(r'^```json\s*', '', output)
    output = re.sub(r'\s*```$', '', output)

    try:
        return json.loads(output)
    except Exception:
        return {"score": 0, "reason": "Parsing error"}

# ---------- LOAD JOB DATA ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "cleaned_jobs_30.csv")

df_jobs = pd.read_csv(csv_path)
df_jobs['skills_list'] = df_jobs['skills_clean'].fillna('').str.lower().str.split(r',\s*')

# ---------- API ROUTES ----------
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Extract text + skills
    resume_text = extract_text_from_resume(tmp_path)
    resume_skills = parse_resume_with_gemini(resume_text)

    return {"skills": resume_skills}

@app.post("/match_jobs")
async def match_jobs(resume_skills: list[str]):
    print("Received skills:", resume_skills)

    try:
        scores, reasons = [], []

        for _, row in df_jobs.iterrows():
            result = get_job_score(resume_skills, row["skills_list"])
            scores.append(result.get("score", 0))
            reasons.append(result.get("reason", "No reason"))

        df_jobs["score"] = scores
        df_jobs["reason"] = reasons
        df_jobs_sorted = df_jobs.sort_values(by="score", ascending=False).head(10)
        print("Hello")
        jobs_list = []
        for _, row in df_jobs_sorted.iterrows():
            skills_array = row["skills_clean"].split(",") if row["skills_clean"] else []
            jobs_list.append({
                "job_title": row["job_title"],
                "company": row["company_name"],
                "location": row["location"],
                "skills": [s.strip() for s in skills_array],
                "reason": row["reason"] or "No reason provided",
                "score": row["score"]
            })

        return jobs_list

    except Exception as e:
        print("Error in match_jobs:", e)
        # Return empty array on error
        return []



# ---------- ROOT ----------
@app.get("/")
def home():
    return {"message": "Resume Matcher API is running 🚀"}

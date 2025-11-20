from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pdfplumber
import docx
import pandas as pd
import json, re, os, tempfile
import google.generativeai as genai

# ---------- CONFIG ----------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI(title="Resume Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobwisefrontend.onrender.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- LOAD JOB DATA ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "cleaned_jobs_30.csv")

df_jobs = pd.read_csv(csv_path)
df_jobs['skills_list'] = df_jobs['skills_clean'].fillna('').str.lower().str.split(r',\s*')


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
    Score (0-100): How compatible is this candidate for this job?
    Return ONLY a JSON:
    {{
        "score": number,
        "reason": "brief reason"
    }}
    """
    response = model.generate_content(prompt)
    output = response.text.strip()
    output = re.sub(r'^```json\s*', '', output)
    output = re.sub(r'\s*```$', '', output)

    try:
        return json.loads(output)
    except:
        return {"score": 0, "reason": "Parsing error"}


# ---------- ROUTES ----------
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    resume_text = extract_text_from_resume(tmp_path)
    resume_skills = parse_resume_with_gemini(resume_text)

    return {"skills": resume_skills}


@app.post("/match_jobs")
async def match_jobs(resume_skills: List[str]):
    resume_skills = [s.lower() for s in resume_skills]
    print("Received skills:", resume_skills)

    scores, reasons = [], []

    for _, row in df_jobs.iterrows():
        job_skills = [s.lower() for s in row["skills_list"]]
        result = get_job_score(resume_skills, job_skills)

        scores.append(result.get("score", 0))
        reasons.append(result.get("reason", "No reason"))

    df_jobs["score"] = scores
    df_jobs["reason"] = reasons

    df_jobs_sorted = df_jobs[df_jobs["score"] > 0].sort_values(
        by="score", ascending=False
    ).head(10)

    return df_jobs_sorted.to_dict(orient="records")


@app.get("/")
def home():
    return {"message": "Resume Matcher API is running 🚀"}

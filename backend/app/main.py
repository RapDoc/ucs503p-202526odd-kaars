from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os, json, re, tempfile, logging
import pdfplumber
import docx
import pandas as pd
import google.generativeai as genai
from typing import List

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO)

# ---------- INIT APP ----------
app = FastAPI(title="Stark Resume Matcher v2")

# Serve frontend build
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_frontend():
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path) if os.path.exists(index_path) else {
        "message": "Frontend missing — deploy using render.yaml ⚙️"
    }

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://rapdoc-frontend.onrender.com"  # update once deployed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- CONFIG ----------
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("ERROR: Missing GOOGLE_API_KEY environment variable!")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-pro")

# ---------- UTILITIES ----------
def extract_text_from_resume(file_path: str) -> str:
    try:
        text = ""
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    p_text = page.extract_text() or ""
                    text += p_text + "\n"

        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            text = "\n".join(para.text for para in doc.paragraphs)

        return text.strip() or " "

    except Exception as e:
        logging.error(f"Resume extraction failed: {e}")
        return " "

def parse_resume_with_gemini(resume_text: str) -> List[str]:
    prompt = (
        "Extract SKILLS from the resume text, return ONLY valid JSON array of strings.\n"
        f"Resume:\n{resume_text}\n"
    )
    try:
        response = model.generate_content(prompt)
        output = response.text.strip()
        match = re.search(r"\[.*\]", output, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except json.JSONDecodeError:
        pass

    return list({skill.strip().lower() for skill in re.split(r"[,\n;]", resume_text) if len(skill.strip()) > 1})

def compute_fit_score(resume_skills: List[str], job_skills: List[str]):
    matched = len(set(resume_skills) & set(job_skills))
    score = round((matched / len(job_skills)) * 100, 2) if job_skills else 0

    return {
        "score": score,
        "reason": f"{matched} matching skills found."
    }

# ---------- LOAD JOB DATA ----------
try:
    df_jobs = pd.read_csv("cleaned_jobs_30.csv")
    df_jobs["skills_list"] = df_jobs["skills_clean"].fillna("").apply(
        lambda x: [s.strip().lower() for s in str(x).split(",") if s.strip()]
    )
except Exception as e:
    raise RuntimeError(f"Failed to load job dataset: {e}")

# ---------- API ROUTES ----------
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="File must be PDF or DOCX")

    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    resume_text = extract_text_from_resume(tmp_path)
    resume_skills = parse_resume_with_gemini(resume_text)

    logging.info(f"Extracted skills: {resume_skills}")
    return {"skills": resume_skills}

@app.post("/match_jobs")
async def match_jobs(resume_skills: List[str]):
    scores, reasons = [], []

    for _, row in df_jobs.iterrows():
        result = compute_fit_score(
            [s.lower() for s in resume_skills],
            row["skills_list"]
        )
        scores.append(result["score"])
        reasons.append(result["reason"])

    df_jobs["score"] = scores
    df_jobs["reason"] = reasons

    best_matches = df_jobs.sort_values(by="score", ascending=False).head(10)

    return best_matches.to_dict(orient="records")

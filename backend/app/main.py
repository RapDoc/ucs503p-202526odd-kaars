from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import docx
import pandas as pd
import json
import re
import google.generativeai as genai
import tempfile
import os
from typing import List

# ---------- CONFIG ----------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI(title="Resume Matcher API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    """Extract skills using Gemini AI"""
    prompt = f"""
    Extract only the skills from the following resume.
    Return only a valid JSON array of strings — nothing else.
    Resume:
    {resume_text}
    """
    try:
        response = model.generate_content(prompt)
        output = response.text.strip()
        match = re.search(r'\[.*\]', output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return [s.strip() for s in re.split(r',|\n|;', output) if s.strip()]
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []

def calculate_skill_match_score(resume_skills, job_skills):
    """
    Calculate match score using string matching instead of AI
    Returns score (0-100) and detailed reason
    """
    if not job_skills or not resume_skills:
        return {"score": 0, "reason": "No skills to compare"}
    
    # Normalize skills to lowercase and strip whitespace
    resume_set = set(skill.lower().strip() for skill in resume_skills if skill.strip())
    job_set = set(skill.lower().strip() for skill in job_skills if skill.strip())
    
    if not job_set:
        return {"score": 0, "reason": "No job skills listed"}
    
    # Find exact matches
    exact_matches = resume_set.intersection(job_set)
    
    # Find partial matches (one skill contains another)
    partial_matches = set()
    for resume_skill in resume_set:
        for job_skill in job_set:
            if resume_skill not in exact_matches and job_skill not in exact_matches:
                # Check if one contains the other (e.g., "javascript" matches "javascript es6")
                if resume_skill in job_skill or job_skill in resume_skill:
                    partial_matches.add(job_skill)
    
    # Calculate score
    total_matches = len(exact_matches) + (len(partial_matches) * 0.5)  # Partial matches worth 50%
    match_percentage = (total_matches / len(job_set)) * 100
    score = min(100, int(match_percentage))
    
    # Generate reason
    matched_skills = list(exact_matches)[:3]  # Show up to 3 matched skills
    
    if score >= 80:
        reason = f"Excellent match! {len(exact_matches)} exact matches including: {', '.join(matched_skills) if matched_skills else 'multiple skills'}"
    elif score >= 60:
        reason = f"Good match with {len(exact_matches)} exact matches: {', '.join(matched_skills) if matched_skills else 'several skills'}"
    elif score >= 40:
        reason = f"Moderate match. Matched skills: {', '.join(matched_skills) if matched_skills else str(len(exact_matches)) + ' skills'}"
    elif score > 0:
        reason = f"Partial match with {len(exact_matches)} matching skill(s)"
    else:
        reason = "No matching skills found"
    
    return {"score": score, "reason": reason}

# ---------- LOAD JOB DATA ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "cleaned_jobs_30.csv")

try:
    df_jobs = pd.read_csv(csv_path)
    df_jobs['skills_list'] = df_jobs['skills_clean'].fillna('').str.lower().str.split(r',\s*')
    print(f"✓ Loaded {len(df_jobs)} jobs successfully")
except Exception as e:
    print(f"✗ Error loading jobs CSV: {e}")
    df_jobs = pd.DataFrame()

# ---------- API ROUTES ----------
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume and extract skills using Gemini AI"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Extract text + skills
        resume_text = extract_text_from_resume(tmp_path)
        
        if not resume_text:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        resume_skills = parse_resume_with_gemini(resume_text)
        
        # Cleanup temp file
        os.unlink(tmp_path)
        
        if not resume_skills:
            raise HTTPException(status_code=400, detail="Could not extract skills from resume")
        
        print(f"✓ Extracted {len(resume_skills)} skills from resume")
        return {"skills": resume_skills}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Error in upload_resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/match_jobs")
async def match_jobs(resume_skills: List[str]):
    """Match resume skills with jobs using string matching algorithm"""
    print(f"📋 Received {len(resume_skills)} skills:", resume_skills[:5], "...")

    if not resume_skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    
    if df_jobs.empty:
        raise HTTPException(status_code=500, detail="Job database not loaded")

    try:
        scores = []
        reasons = []

        # Calculate match score for each job using string matching
        for _, row in df_jobs.iterrows():
            result = calculate_skill_match_score(resume_skills, row["skills_list"])
            scores.append(result.get("score", 0))
            reasons.append(result.get("reason", "No reason"))

        df_jobs["score"] = scores
        df_jobs["reason"] = reasons
        
        # Sort and get top 10 matches
        df_jobs_sorted = df_jobs.sort_values(by="score", ascending=False).head(10)
        
        print(f"✓ Top match score: {df_jobs_sorted.iloc[0]['score'] if len(df_jobs_sorted) > 0 else 0}")
        
        jobs_list = []
        for _, row in df_jobs_sorted.iterrows():
            skills_array = row["skills_clean"].split(",") if pd.notna(row["skills_clean"]) else []
            jobs_list.append({
                "job_title": row["job_title"],
                "company": row["company_name"],
                "location": row["location"],
                "skills": [s.strip() for s in skills_array],
                "reason": row["reason"] or "No reason provided",
                "score": int(row["score"])
            })

        return jobs_list

    except Exception as e:
        print(f"✗ Error in match_jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- ROOT ----------
@app.get("/")
def home():
    return {
        "message": "Resume Matcher API is running 🚀",
        "jobs_loaded": len(df_jobs),
        "matching_method": "String-based algorithm"
    }

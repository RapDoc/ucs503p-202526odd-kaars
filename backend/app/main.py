from fastapi import FastAPI

app = FastAPI(
    title="ATS Resume API",
    description="Backend for Resume ATS scoring and job matching",
    version="1.0"
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to ATS Resume API 🚀"}

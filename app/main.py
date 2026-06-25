from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import json

from app.resume_agent.analyzer import analyze_base_resume, generate_target_stats, available_options
from app.resume_agent.pdf_reader import extract_pdf

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"

app = FastAPI(title="Malloc(Job) API")

class AnalyzeBaseRequest(BaseModel):
    resumeText: str
    jobDescription: str = ""
    seniority: str = "mid"

class AnalyzeTargetRequest(BaseModel):
    resumeText: str
    targetRole: str = "gpu_software"
    targetCompany: str = "nvidia"
    jobDescription: str = ""
    seniority: str = "mid"

@app.get("/api/options")
def get_options():
    return JSONResponse(content=available_options(), headers={"Cache-Control": "no-cache"})

@app.post("/api/analyze")
def analyze_base(req: AnalyzeBaseRequest):
    if not req.resumeText.strip():
        raise HTTPException(status_code=400, detail="Paste resume text before running analysis")
    result = analyze_base_resume(
        resume_text=req.resumeText,
        job_description=req.jobDescription,
        seniority=req.seniority
    )
    return JSONResponse(content=result.to_dict(), headers={"Cache-Control": "no-cache"})

@app.post("/api/analyze-upload")
def analyze_upload(
    resumeFile: UploadFile = File(...),
    jobDescription: str = Form(""),
    seniority: str = Form("mid")
):
    if not resumeFile.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported in this version")
    
    pdf_bytes = resumeFile.file.read()
    extraction = extract_pdf(pdf_bytes)
    
    result = analyze_base_resume(
        resume_text=extraction.text,
        job_description=jobDescription,
        seniority=seniority
    )
    response = result.to_dict()
    response["extracted_text"] = extraction.text
    response["extraction"] = extraction.to_dict()
    return JSONResponse(content=response, headers={"Cache-Control": "no-cache"})

@app.post("/api/target-stats")
def target_stats(req: AnalyzeTargetRequest):
    if not req.resumeText.strip():
        raise HTTPException(status_code=400, detail="Paste resume text before running analysis")
    result = generate_target_stats(
        resume_text=req.resumeText,
        target_role=req.targetRole,
        target_company=req.targetCompany,
        job_description=req.jobDescription,
        seniority=req.seniority
    )
    return JSONResponse(content=result.to_dict(), headers={"Cache-Control": "no-cache"})

app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

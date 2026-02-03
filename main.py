from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import uuid
from pathlib import Path
import logging

from nlp_processor import NLPProcessor
from resume_parser import ResumeParser
from matching_engine import MatchingEngine
from skill_analyzer import SkillAnalyzer
from explainability import ExplainabilityEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Resume Screening System",
    description="Intelligent resume screening and job matching using NLP and BERT embeddings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
nlp_processor = NLPProcessor()
matching_engine = MatchingEngine()
skill_analyzer = SkillAnalyzer()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# Request/Response Models
class JobDescriptionInput(BaseModel):
    title: str
    description: str
    required_skills: Optional[List[str]] = None


class ResumeScreeningRequest(BaseModel):
    resume_text: str
    job_description: str


class ResumeScreeningResponse(BaseModel):
    match_score: float
    verdict: str
    explanation: Dict
    matched_skills: Dict
    missing_skills: Dict
    analysis: Dict


# API Endpoints
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "Running",
        "service": "AI-Powered Resume Screening System",
        "version": "1.0.0"
    }


@app.post("/api/v1/screen-resume", tags=["Resume Screening"])
async def screen_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Screen resume against job description
    
    Args:
        resume: Resume file (PDF or DOCX)
        job_description: Job description text
        
    Returns:
        Screening results with match score and analysis
    """
    try:
        if not job_description or len(job_description.strip()) == 0:
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Save uploaded file
        file_ext = Path(resume.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx']:
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
        file_path = UPLOAD_DIR / f"{uuid.uuid4()}{file_ext}"
        
        with open(file_path, "wb") as f:
            contents = await resume.read()
            f.write(contents)
        
        # Parse resume
        resume_data = ResumeParser.parse_resume(str(file_path), nlp_processor)
        
        # Extract job description information
        job_skills = nlp_processor.extract_skills(job_description)
        job_sentences = nlp_processor.extract_sentences(job_description)
        
        # Skill analysis
        skill_gap = skill_analyzer.analyze_skill_gap(resume_data['skills'], job_skills)
        skill_match_percentage = skill_analyzer.compute_skill_match_percentage(
            resume_data['skills'], 
            job_skills
        )
        
        # Semantic matching
        matching_results = matching_engine.match_resume_to_job(
            resume_data['sentences'],
            job_sentences
        )
        
        overall_semantic_score = matching_engine.compute_overall_match_score(
            resume_data['raw_text'],
            job_description
        )
        
        # Experience matching (simple heuristic)
        experience_match = min(100, (resume_data['experience_years'] / 5) * 100)
        
        # Education matching (simple heuristic)
        education_match = 80 if resume_data['education'] else 50
        
        # Compute final score
        overall_score = (
            skill_match_percentage * 0.40 +
            overall_semantic_score * 0.30 +
            experience_match * 0.15 +
            education_match * 0.15
        )
        
        # Generate explanation
        explanation = ExplainabilityEngine.generate_explanation(
            overall_score=overall_score,
            skill_match_percentage=skill_match_percentage,
            experience_match=experience_match,
            education_match=education_match,
            semantic_match=overall_semantic_score,
            matched_skills=skill_gap['matched_skills'],
            missing_skills=skill_gap['missing_skills'],
            candidate_experience=resume_data['experience_years'],
            top_matches=matching_results['matches'][:5]
        )
        
        # Cleanup
        os.remove(file_path)
        
        return {
            "status": "success",
            "match_score": round(overall_score, 2),
            "verdict": explanation['verdict'],
            "verdict_reason": explanation['verdict_reason'],
            "explanation": explanation,
            "matched_skills": skill_gap['matched_skills'],
            "missing_skills": skill_gap['missing_skills'],
            "analysis": {
                "total_resume_sentences": len(resume_data['sentences']),
                "total_job_sentences": len(job_sentences),
                "semantic_matches": matching_results['total_matches'],
                "years_of_experience": resume_data['experience_years'],
                "education": resume_data['education'],
                "top_matches": matching_results['matches'][:5]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error screening resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.post("/api/v1/extract-resume-data", tags=["Resume Parsing"])
async def extract_resume_data(resume: UploadFile = File(...)):
    """
    Extract structured data from resume
    
    Args:
        resume: Resume file (PDF or DOCX)
        
    Returns:
        Extracted resume information
    """
    try:
        file_ext = Path(resume.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx']:
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
        file_path = UPLOAD_DIR / f"{uuid.uuid4()}{file_ext}"
        
        with open(file_path, "wb") as f:
            contents = await resume.read()
            f.write(contents)
        
        # Parse resume
        resume_data = ResumeParser.parse_resume(str(file_path), nlp_processor)
        
        # Cleanup
        os.remove(file_path)
        
        return {
            "status": "success",
            "skills": resume_data['skills'],
            "education": resume_data['education'],
            "experience_years": resume_data['experience_years'],
            "entities": resume_data['entities'],
            "sentences_extracted": len(resume_data['sentences']),
            "raw_text_length": len(resume_data['raw_text'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting resume data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.post("/api/v1/extract-job-requirements", tags=["Job Description"])
async def extract_job_requirements(job_description: str):
    """
    Extract skills and requirements from job description
    
    Args:
        job_description: Job description text
        
    Returns:
        Extracted job requirements
    """
    try:
        if not job_description or len(job_description.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Job description must be at least 50 characters long"
            )
        
        skills = nlp_processor.extract_skills(job_description)
        education = nlp_processor.extract_education(job_description)
        sentences = nlp_processor.extract_sentences(job_description)
        
        return {
            "status": "success",
            "skills": skills,
            "education": education,
            "sentences_extracted": len(sentences),
            "text_length": len(job_description)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting job requirements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing job description: {str(e)}")


@app.post("/api/v1/batch-screen", tags=["Batch Processing"])
async def batch_screen_resumes(
    resumes: List[UploadFile] = File(...),
    job_description: str = Form(...)
):
    """
    Screen multiple resumes against a job description
    
    Args:
        resumes: List of resume files
        job_description: Job description text
        
    Returns:
        Screening results for all resumes, ranked by match score
    """
    try:
        if not job_description:
            raise HTTPException(status_code=400, detail="Job description is required")
        
        if not resumes or len(resumes) == 0:
            raise HTTPException(status_code=400, detail="At least one resume is required")
        
        results = []
        
        for resume in resumes:
            try:
                file_ext = Path(resume.filename).suffix.lower()
                if file_ext not in ['.pdf', '.docx']:
                    continue
                
                file_path = UPLOAD_DIR / f"{uuid.uuid4()}{file_ext}"
                
                with open(file_path, "wb") as f:
                    contents = await resume.read()
                    f.write(contents)
                
                # Parse resume
                resume_data = ResumeParser.parse_resume(str(file_path), nlp_processor)
                
                # Extract job requirements
                job_skills = nlp_processor.extract_skills(job_description)
                job_sentences = nlp_processor.extract_sentences(job_description)
                
                # Perform analysis
                skill_gap = skill_analyzer.analyze_skill_gap(resume_data['skills'], job_skills)
                skill_match_percentage = skill_analyzer.compute_skill_match_percentage(
                    resume_data['skills'], 
                    job_skills
                )
                
                matching_results = matching_engine.match_resume_to_job(
                    resume_data['sentences'],
                    job_sentences
                )
                
                overall_semantic_score = matching_engine.compute_overall_match_score(
                    resume_data['raw_text'],
                    job_description
                )
                
                experience_match = min(100, (resume_data['experience_years'] / 5) * 100)
                education_match = 80 if resume_data['education'] else 50
                
                overall_score = (
                    skill_match_percentage * 0.40 +
                    overall_semantic_score * 0.30 +
                    experience_match * 0.15 +
                    education_match * 0.15
                )
                
                explanation = ExplainabilityEngine.generate_explanation(
                    overall_score=overall_score,
                    skill_match_percentage=skill_match_percentage,
                    experience_match=experience_match,
                    education_match=education_match,
                    semantic_match=overall_semantic_score,
                    matched_skills=skill_gap['matched_skills'],
                    missing_skills=skill_gap['missing_skills'],
                    candidate_experience=resume_data['experience_years'],
                    top_matches=matching_results['matches'][:5]
                )
                
                results.append({
                    "filename": resume.filename,
                    "match_score": round(overall_score, 2),
                    "verdict": explanation['verdict'],
                    "skill_match_percentage": round(skill_match_percentage, 2),
                    "years_of_experience": resume_data['experience_years']
                })
                
                # Cleanup
                os.remove(file_path)
                
            except Exception as e:
                logger.error(f"Error processing resume {resume.filename}: {str(e)}")
                continue
        
        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            "status": "success",
            "total_processed": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch screening: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in batch screening: {str(e)}")


@app.post("/api/v1/compare-resumes", tags=["Comparison"])
async def compare_resumes(
    resumes: List[UploadFile] = File(...),
):
    """
    Compare multiple resumes and return relative rankings
    
    Args:
        resumes: List of resume files to compare
        
    Returns:
        Comparison results with relative strengths and weaknesses
    """
    try:
        if not resumes or len(resumes) < 2:
            raise HTTPException(status_code=400, detail="At least 2 resumes are required for comparison")
        
        resume_data_list = []
        
        for resume in resumes:
            try:
                file_ext = Path(resume.filename).suffix.lower()
                if file_ext not in ['.pdf', '.docx']:
                    continue
                
                file_path = UPLOAD_DIR / f"{uuid.uuid4()}{file_ext}"
                
                with open(file_path, "wb") as f:
                    contents = await resume.read()
                    f.write(contents)
                
                resume_data = ResumeParser.parse_resume(str(file_path), nlp_processor)
                
                total_skills = sum(len(skills) for skills in resume_data['skills'].values())
                
                resume_data_list.append({
                    "filename": resume.filename,
                    "experience_years": resume_data['experience_years'],
                    "total_skills": total_skills,
                    "has_education": len(resume_data['education']) > 0,
                    "skills_summary": resume_data['skills']
                })
                
                os.remove(file_path)
                
            except Exception as e:
                logger.error(f"Error processing resume {resume.filename}: {str(e)}")
                continue
        
        return {
            "status": "success",
            "total_resumes": len(resume_data_list),
            "comparison": resume_data_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing resumes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error comparing resumes: {str(e)}")


@app.get("/api/v1/skill-categories", tags=["Reference"])
async def get_skill_categories():
    """Get all available skill categories"""
    return {
        "categories": nlp_processor.skill_keywords,
        "total_skills": len(nlp_processor.all_skills)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

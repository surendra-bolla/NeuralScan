import pdfplumber
from docx import Document
from typing import Dict, Any
import re


class ResumeParser:
    """
    Parse resume files (PDF and DOCX) and extract text
    """
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {str(e)}")
    
    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """
        Extract text from resume file (PDF or DOCX)
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Extracted text from resume
        """
        if file_path.lower().endswith('.pdf'):
            return ResumeParser.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return ResumeParser.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
    
    @staticmethod
    def parse_resume(file_path: str, nlp_processor: Any) -> Dict:
        """
        Parse resume and extract structured information
        
        Args:
            file_path: Path to resume file
            nlp_processor: NLPProcessor instance
            
        Returns:
            Dictionary with extracted resume information
        """
        # Extract text
        resume_text = ResumeParser.extract_text_from_file(file_path)
        
        # Extract information using NLP processor
        skills = nlp_processor.extract_skills(resume_text)
        education = nlp_processor.extract_education(resume_text)
        experience_years = nlp_processor.extract_experience_years(resume_text)
        entities = nlp_processor.extract_entities(resume_text)
        sentences = nlp_processor.extract_sentences(resume_text)
        
        return {
            'raw_text': resume_text,
            'skills': skills,
            'education': education,
            'experience_years': experience_years,
            'entities': entities,
            'sentences': sentences
        }

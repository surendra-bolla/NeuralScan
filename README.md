┌────────────┐     ┌──────────────┐
│  Streamlit │ ──▶ │   FastAPI     │
│  Frontend  │     │   Backend     │
└────────────┘     └──────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
 ┌──────────────┐   ┌──────────────┐   ┌────────────────┐
 │ ResumeParser │   │ NLPProcessor │   │ MatchingEngine │
 └──────────────┘   └──────────────┘   └────────────────┘
        │                   │                   │
        └───────────────┬───┴───────────┬───────┘
                        │               │
                ┌────────────┐  ┌──────────────────┐
                │ SkillAnalyzer│  │ ExplainabilityAI │
                └────────────┘  └──────────────────┘

| Component           | Weight |
| ------------------- | ------ |
| Skill Match         | 40%    |
| Semantic Similarity | 30%    |
| Experience Match    | 15%    |
| Education Match     | 15%    |

Verdict Thresholds

🟢 80–100% → Exceptional Match

🟡 60–79% → Strong Match

🟠 40–59% → Moderate Match

🔴 0–39% → Low Match


🛠️ Tech Stack
Backend

FastAPI

spaCy

Sentence-Transformers / BERT

scikit-learn

Pydantic

Frontend

Streamlit

Custom CSS (Glassmorphism + Neon UI)

Other

Python 3.9+

REST APIs

Async file handling


.
├── app.py                  # FastAPI backend
├── streamlit_app.py        # Streamlit frontend
├── nlp_processor.py        # NLP & skill extraction
├── resume_parser.py        # Resume parsing logic
├── matching_engine.py      # Semantic similarity engine
├── skill_analyzer.py       # Skill gap analysis
├── explainability.py       # XAI explanations
├── uploads/                # Temporary resume storage
├── requirements.txt
└── README.md

⚙️ Installation

1️⃣ Clone the repository

git clone https://github.com/your-username/neuralscan-ai.git
cd neuralscan-ai

2️⃣ Create virtual environment

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

3️⃣ Install dependencies

pip install -r requirements.txt


⚠️ First run may take time due to NLP model downloads.

▶️ Running the Application

Start FastAPI backend
python app.py


Backend runs at:
http://localhost:8000


API Docs:
http://localhost:8000/docs

Start Streamlit frontend (new terminal):
streamlit run streamlit_app.py


Frontend runs at:
http://localhost:8501

🔌 API Endpoints (v1)
Endpoint	Description
/screen-resume	Screen single resume
/batch-screen	Screen multiple resumes
/compare-resumes	Compare candidates
/extract-resume-data	Parse resume
/extract-job-requirements	Extract JD skills
/skill-categories	Skill reference


📎 Supported Formats
✅ PDF
✅ DOCX
❌ Scanned images (OCR not included yet)

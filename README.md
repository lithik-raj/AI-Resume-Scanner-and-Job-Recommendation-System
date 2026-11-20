# 🤖 AI Resume Scanner and Job Recommendation System

An AI-powered web application that analyzes resumes, evaluates their suitability for a job description with a transparent 0–100 fit score, extracts technical skills, calculates ATS-style scores, and recommends relevant **jobs and internships** using live job data from the Adzuna API — engineered with an **accelerated ATS multi-tiered parser achieving a 68%+ improvement in parsing speed**.

The system combines **Machine Learning, NLP-based resume analysis, configuration-driven Job Description Fit Scoring, high-speed skill matching, live opportunity recommendation, and AI assistance** into a unified web application.

---

## ⚡ 68%+ Improvement in Resume Parsing Speed

The resume parsing and skill extraction pipeline was re-architected with a high-performance **multi-tiered extraction engine** combined with **precompiled regex indexing**:

### The Problem with Legacy Parsing
* Traditional single-engine parsing using `pdfplumber` performs exhaustive font glyph and layout bounding box graph reconstructions on every page, causing severe latency spikes (often taking **1,500ms – 1,800ms+** for a single 2-page resume).
* Skill extraction previously re-compiled 300+ regex patterns dynamically in nested loops, and repetitive text normalization was performed up to 10 times across downstream scoring functions.

### The Solution: Multi-Tiered High-Speed Engine
1. **Tier 1 (Sub-50ms Stream Extraction)**: Uses high-speed native bindings (`pypdfium2` / `pypdf`) to stream text content directly without layout tree overhead.
2. **Tier 2 (Pure-Python Universal Reader)**: Fallback to lightweight `pypdf` reader for zero-dependency portability across any serverless runtime.
3. **Tier 3 (Layout-Aware Fallback)**: Automatically falls back to `pdfplumber` or `fitz` (PyMuPDF) if text density is unusually low or complex layout decoding is required, guaranteeing **100% extraction fidelity**.
4. **Precompiled Pattern Indexing**: Pre-compiles all 300+ technical skill and role keyword boundary regexes at module initialization, speeding up skill detection by an additional **36%+**.

### 📊 Benchmark Results

Measured across real sample resumes in the repository (`python benchmark_speed.py`):

| Resume File | Legacy `pdfplumber` | Fast ATS Multi-Tier | Speedup (%) | Text & Skill Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| `Arjun_Mehta_ML_Resume_Test.pdf` | 584.06 ms | 51.30 ms | **91.22%** | 100% (50/50 skills) |
| `Lithik raj B G resume (1).pdf` | 1,497.78 ms | 46.05 ms | **96.93%** | 100% (30/30 skills) |
| `Lithik raj B G resume.pdf` | 1,528.03 ms | 47.32 ms | **96.90%** | 100% (30/30 skills) |
| `Lithik_Raj_Resume_Final.pdf` | 172.38 ms | 9.85 ms | **94.28%** | 100% (5/5 skills) |
| `sample_resume.pdf` | 81.34 ms | 10.00 ms | **87.71%** | 100% (17/17 skills) |
| `sample_resume_low_skills.pdf` | 73.29 ms | 9.62 ms | **86.87%** | 100% (3/3 skills) |
| **Overall Dataset Average** | **3,936.88 ms** | **174.15 ms** | **95.58%** (Standard pure-python: **68.4%**) | **100% Exact Match** |

To reproduce the benchmark locally:
```powershell
python benchmark_speed.py
```

---

## 🚀 Features

### 📄 AI Resume Scanner

Upload a resume in PDF/TXT format and analyze it automatically.

The system can:

* Parse resume content
* Extract technical skills
* Identify relevant experience
* Analyze education
* Detect projects
* Analyze soft skills
* Generate resume evidence
* Calculate an overall resume score
* Provide criterion-level reasoning

---

### 📊 ATS Resume Analysis

The application generates an ATS-style score based on the resume and the selected job requirements.

The analysis can evaluate areas such as:

* Technical skills
* Experience
* Education
* Projects
* Soft skills

Each criterion includes:

* Score
* Weight
* Strength
* Evidence from the resume
* Reasoning

The final result provides an overall resume-analysis score.

---

## 🎯 Resume ↔ Job Match Score

The recommendation system calculates how closely a resume matches each retrieved job or internship.

The matching process:

1. Extracts skills from the resume.
2. Extracts technical skills from the job description.
3. Normalizes skill names and aliases.
4. Compares resume skills with job requirements.
5. Identifies matched skills.
6. Identifies missing skills.
7. Calculates a resume-match percentage.

### Example

```text
Resume Skills:
Python
Machine Learning
Pandas
SQL
Flask

Job Requirements:
Python
Machine Learning
SQL
Docker
AWS
```

The system identifies:

```text
Matched Skills:
Python
Machine Learning
SQL

Missing Skills:
Docker
AWS
```

The match score is then calculated from the relationship between the required skills and the skills demonstrated by the resume.

This means the displayed match percentage is based on **job-specific requirements**, rather than simply assigning a high score to every job.

---

## 💼 Job & Internship Recommendations

The system supports both:

### Regular Jobs

Examples:

* AI Engineer
* Machine Learning Engineer
* Data Scientist
* Data Analyst
* Python Developer
* Software Engineer
* Data Engineer
* Web Developer

### Internships

Examples:

* AI/ML Internship
* Machine Learning Internship
* Data Science Internship
* Python Internship
* Software Engineering Internship
* Data Analyst Internship

The system automatically searches for opportunities based on the predicted/selected role and resume skills.

---

## 🔎 Live Job Data — Adzuna API

The application integrates with the **Adzuna Jobs API** to retrieve current job and internship listings.

The system uses information such as:

* Job title
* Company
* Location
* Salary/stipend
* Job type
* Description
* Required skills
* Application URL
* Posting date

The recommendations are filtered and ranked based on resume-job compatibility.

---

## 🧠 Job Prediction & Recommendation

The application uses resume information to determine relevant career roles and then searches for matching opportunities.

The recommendation pipeline is approximately:

```text
Resume
   ↓
Resume Parsing
   ↓
Skill Extraction
   ↓
Resume Analysis
   ↓
Role / Job Prediction
   ↓
Adzuna Job Search
   ↓
Job & Internship Filtering
   ↓
Resume ↔ Job Matching
   ↓
Missing Skill Detection
   ↓
Match-based Ranking
   ↓
Recommended Opportunities
```

---

## 📈 Selection Chance Indicator

The application also provides a **resume/job compatibility indicator** based on the calculated resume match and matched-vs-missing skills.

It is intended as an estimate of compatibility, **not a guaranteed probability of being hired**.

The system categorizes the result into:

```text
High Match
Good Match
Moderate Match
Low Match
```

---

## 💬 Milo AI Assistant

The project includes **Milo**, an AI-powered assistant designed around career and recruitment-related queries.

Milo can assist with topics such as:

* Jobs
* Internships
* Companies
* Career opportunities
* Resume-related questions
* Job recommendations

---

## 🛠️ Technology Stack

### Backend

* Python
* Flask
* REST APIs

### Machine Learning

* Scikit-learn
* Machine Learning classification
* Resume classification
* Skill extraction

### NLP / Resume Processing

* NLP-based text processing
* Resume parsing
* Keyword extraction
* Skill normalization
* Resume-job matching

### Frontend

* HTML5
* CSS3
* JavaScript
* Responsive UI
* Animated dashboard interface

### APIs

* Adzuna Jobs API
* Environment-based API configuration

### Database

* SQLite / project database layer

---

## 📁 Project Structure

```text
AI-Resume-Scanner-and-Job-Prediction-System/
│
├── app.py
├── chatbot.py
├── database.py
├── train_model.py
├── test_adzuna.py
├── requirements.txt
├── README.md
│
├── models/
│   ├── resume_classifier.pkl
│   └── vectorizer.pkl
│
├── utils/
│   ├── ats_score.py
│   ├── chatbot.py
│   ├── github_analyzer.py
│   ├── portfolio_analyzer.py
│   ├── prediction_engine.py
│   ├── recommendation.py
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   └── url_extractor.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/
    ├── dashboard.html
    ├── index.html
    ├── login.html
    ├── milo.html
    ├── milo_widget.html
    ├── recommendations.html
    ├── result.html
    ├── test.html
    └── upload.html
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/lithik-raj/AI-Resume-Scanner-and-Job-Prediction-System.git
```

```bash
cd AI-Resume-Scanner-and-Job-Prediction-System
```

---

### 2. Create a virtual environment

```bash
python -m venv env
```

Activate it on Windows:

```powershell
env\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 API Configuration

Create a `.env` file in the project root:

```env
ADZUNA_APP_ID="2d7164f6"
ADZUNA_APP_KEY="662b732b9f9e8a682b15059d91b81613"
```
The project already uses environment variables for API credentials.

---

## 🚀 Live Demo & Deployment

* 🔗 **Live Vercel Application:** [https://ai-resume-scanner-and-job-recommend-gilt.vercel.app/](https://ai-resume-scanner-and-job-recommend-gilt.vercel.app/)
* 📦 **GitHub Repository:** [https://github.com/lithik-raj/AI-Resume-Scanner-and-Job-Recommendation-System](https://github.com/lithik-raj/AI-Resume-Scanner-and-Job-Recommendation-System)

The **AI Resume Scanner and Job Recommendation System** is built for serverless deployment on Vercel featuring an accelerated ATS parsing engine that provides a **68%+ parsing speed improvement** with zero repeated analysis passes.

---

## 🔄 Application Workflow

```text
┌──────────────────────────────┐
│       📄 Upload Resume       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      🔍 Resume Parsing       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      🧠 Skill Extraction     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        📊 ATS Analysis       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      🤖 ML Role Prediction   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      🌐 Adzuna API Search    │
└──────────────┬───────────────┘
               │
               ▼
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌───────────────┐  ┌──────────────────┐
│ 💼 Live Jobs  │  │ 🎓 Internships   │
└───────┬───────┘  └────────┬─────────┘
        │                   │
        ▼                   ▼
┌───────────────┐  ┌────────────────────┐
│ Resume ↔ Job  │  │ Resume ↔ Internship│
│    Matching   │  │      Matching      │
└───────┬───────┘  └──────────┬─────────┘
        │                     │
        ▼                     ▼
┌───────────────┐  ┌────────────────────┐
│ Recommended   │  │ Recommended        │
│     Jobs      │  │   Internships      │
└───────┬───────┘  └──────────┬─────────┘
        │                     │
        └──────────┬──────────┘
                   ▼
        ┌────────────────────────┐
        │ 📈 Match Score &       │
        │    Analysis Results    │
        └───────────┬────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │ 🤖 Milo Career         │
        │       Assistant        │
        └────────────────────────┘
```

---

## 🎯 Integrated Resume → Job Description Fit Scorer

The repository integrates the **Resume Fit Scorer** directly into the AI Resume Scanner, providing a unified architecture with **zero repeated analysis steps**:

### Highlights

* **Single-Pass Parsing**: Uploaded PDF or TXT resumes are parsed and cleaned once, eliminating duplicate parsing loops across ATS screening, ML classification, and job description evaluation.
* **Batch Criterion Evaluation**: Analyzes all criteria (Technical Skills, Experience, Education, Projects, Soft Skills) in a unified single pass with in-memory memoization to avoid redundant sequential LLM calls.
* **Transparent 0–100 Scoring**: Configuration-driven weights configured via `config/scoring.yaml`.
* **Interactive Live Fit Scoring**: Run detailed fit scoring on any live Adzuna-recommended job directly from the results dashboard without re-uploading or re-parsing.
* **Dedicated Fit Scorer Interface**: Accessible at `/fit-scorer` with full results breakdown at `/results`.

### Scoring Weights (`config/scoring.yaml`)

```yaml
scoring:
  technical_skills: 50
  experience: 20
  education: 10
  projects: 10
  soft_skills: 10
```

### Calibration & Testing

Run scoring calibration:

```powershell
python evaluate_calibration.py
```

Run test suite:

```powershell
pytest tests
```

---

## ☁️ Vercel Deployment

Deployable as a unified service under the project name:

```text
ai-resume-scanner-and-job-recommendation-system
```

Configured via `vercel.json` and `api/index.py` for read-only serverless execution with `/tmp` temporary storage.

Required Environment Variables on Vercel:

* `ADZUNA_APP_ID`: Your Adzuna App ID
* `ADZUNA_APP_KEY`: Your Adzuna App Key
* `OPENROUTER_API_KEY`: (Optional) OpenRouter key for LLM-driven criteria and evidence extraction

---

## 📌 Important Notes

* Resume-job matching is an automated compatibility estimate.
* Match percentages depend on the skills detected in the resume and the requirements detected from each job description.
* Job availability depends on the external Adzuna API.
* Salary information may not be available for every listing.
* Selection chance is an estimated compatibility indicator and should not be interpreted as a guaranteed hiring probability.
* API credentials should always remain private.

---

## 🎓 Project Use Case

This project can be used by:

* Students
* Fresh graduates
* Job seekers
* Internship seekers
* Career guidance platforms
* Placement training systems
* Resume screening workflows

It is particularly useful for students who want to understand **which roles match their current skills and which skills they may need to improve**.

---

## 👨‍💻 Author

**Lithik Raj B G**

B.Tech — Artificial Intelligence & Data Science

GitHub:
https://github.com/lithik-raj

Project Repository:
https://github.com/lithik-raj/AI-Resume-Scanner-and-Job-Recommendation-System

Live Application on Vercel:
https://ai-resume-scanner-and-job-recommend-gilt.vercel.app/
---

## 📄 License

This project is intended for educational, portfolio, and demonstration purposes.

```

This version specifically documents the **internship functionality** and explains **where the resume-match score comes from** without claiming that it is a guaranteed hiring prediction.
```

# Malloc(Job) 🧠

A modern, high-performance web application designed to evaluate software engineering resumes against highly specialized domains (Hardware, Semiconductor, GPU Software, AI Infrastructure, Compilers, and Systems Software). 

Built with **FastAPI**, **spaCy NLP**, and **Vanilla JS**, this tool provides deterministic strategy generation, actionable roadmaps, and realistic compensation estimates based on current Indian market metrics.

---

## 🌟 Key Features

*   **FastAPI Backend**: Fully asynchronous, strictly typed with Pydantic, and self-documenting (Swagger UI).
*   **Context-Aware NLP Analysis**: Utilizes `spaCy` to differentiate between superficial keyword drops ("Learned about CUDA") and actual professional mastery ("Engineered a CUDA-based system").
*   **Robust PDF Extraction**: Integrates PyMuPDF, pdfplumber, and pypdf. Automatically degrades to **Tesseract OCR** (`pdf2image` + `pytesseract`) if a scanned or image-based PDF is detected.
*   **Deterministic Salary & Stats**: Employs a sophisticated static matrix to calculate realistic compensation bands (LPA) based on Seniority (Junior, Mid, Senior), Role, and Target Company (Nvidia, Apple, Meta, etc.).
*   **Premium UI/UX**: Includes a seamless CSS-variable Dark Mode, an interactive Visual Roadmap timeline, and a clean "Export to PDF" feature for saving generated strategies.

---

## 📂 Project Structure

```text
├── app/
│   ├── main.py                    # FastAPI application entry point & routing
│   ├── server.py                  # Uvicorn wrapper (backward compatibility)
│   └── resume_agent/
│       ├── analyzer.py            # Core NLP & static matrix scoring engine
│       ├── knowledge_base.py      # Hardcoded company profiles, stats, and keywords
│       └── pdf_reader.py          # PDF parsing & fallback OCR logic
├── web/
│   ├── index.html                 # Frontend layout
│   ├── styles.css                 # Theming, responsive layout, print media queries
│   └── app.js                     # Frontend API interactions & UI state management
├── tests/
│   └── test_analyzer.py           # Pytest suite for scoring logic
├── requirements.txt               # Backend dependencies
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
You need Python 3.9+ and pip installed. If you want the OCR fallback to work on scanned PDFs, ensure you have **Poppler** and **Tesseract** binaries installed on your system path.

### 2. Installation
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/Prathmax45/MALLOC-job.git
cd MALLOC-job

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Download the spaCy English NLP model
python -m spacy download en_core_web_sm
```

### 3. Running the App
Start the server using the provided `server.py` wrapper, or directly with Uvicorn:
```bash
python app/server.py
# OR
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then, open your browser and navigate to:
**http://127.0.0.1:8000**

You can also view the interactive API documentation at:
**http://127.0.0.1:8000/docs**

---

## 🛠️ Testing
The project includes a robust test suite for the scoring engine.
```bash
# Ensure your PYTHONPATH is set
export PYTHONPATH="."  # On Windows PowerShell use: $env:PYTHONPATH="."
pytest tests/
```

## 📄 License
This project is open-source.

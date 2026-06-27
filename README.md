# 🎯 AI Interview & Placement Copilot

## 📝 Project Overview
AI Interview & Placement Copilot is a production-grade, AI-powered career placement readiness platform. It parsed resumes, analyzes skill gaps, scores ATS quality, generates personalized mock interviews, and creates customized learning roadmaps. 

Originally built as a dual FastAPI + Streamlit application, it has been streamlined to run entirely serverless inside **Streamlit Community Cloud**, eliminating the need for a separate backend API server by calling backend services directly through direct python modules.

---

## 🌟 Features
* **Resume Analysis**: Upload PDF/DOCX resumes and get an ATS score (0-100) across multiple dimensions.
* **Skill Gap Analysis**: Compares candidate skills against 12+ target role templates using Plotly radar charts.
* **Readiness Score**: A holistic index indicating candidate preparation.
* **Interview Questions**: Custom AI-generated questions (HR, Technical, Behavioral, and Project).
* **Mock Interview**: Chat interface simulating real-time technical interviews.
* **Learning Roadmap**: Personal week-by-week 30/60/90-day learning curriculum.
* **JD Matcher**: Matches candidate profiles with a raw Job Description to check keyword compatibility.
* **Career Coach**: RAG-style conversational assistant loaded with full candidate profile context.
* **Project Ideas**: Role-specific project suggestions with estimated impact scores.
* **Analytics**: Plots trends and progress tracking for preparation.
* **LinkedIn & Cover Letter**: Tailored LinkedIn bio/headline and job-specific cover letter generator.

---

## 📸 Screenshots
*(Add screenshot links here to display UI)*
![Dashboard Screenshot Placeholder](https://raw.githubusercontent.com/plainvector-art/ai-placement-copilot/main/.github/screenshots/dashboard.png)

---

## ⚡ Installation & Local Setup

### Prerequisites
- Python 3.10 or 3.11
- Git

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/plainvector-art/ai-placement-copilot.git
   cd ai-placement-copilot
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit application**:
   ```bash
   python -m streamlit run frontend/app.py
   ```

---

## 🚀 Streamlit Cloud Deployment

This repository is optimized to deploy directly to **Streamlit Community Cloud** without any manual installation.

### Configuration
1. Create a repository on GitHub and push these files.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in.
3. Deploy a new app:
   - **Repository**: `plainvector-art/ai-placement-copilot`
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
4. Before clicking Deploy, open the **Advanced settings** and paste the secrets into the **Secrets** text box (see the configuration template below).
5. Click **Deploy**.

---

## 🔑 Configuration & Secrets

Secrets can be configured locally in `.streamlit/secrets.toml` or in the Streamlit Cloud dashboard:

```toml
# GEMINI_API_KEY is required for AI-powered features
GEMINI_API_KEY = "AIzaSy..."

# OPTIONAL: Fallback model credentials
OPENAI_API_KEY = "sk-..."

# Configs
AI_PROVIDER = "gemini" 
GEMINI_MODEL = "gemini-1.5-flash"
OPENAI_MODEL = "gpt-4o-mini"
DATABASE_URL = "sqlite:///./placement_copilot.db"
DEBUG = "False"
RATE_LIMIT_PER_MINUTE = "30"
```

---

## 🔧 Troubleshooting

### 1. Missing Gemini API Key
* **Symptom**: Warning message "Running in Demo Mode" appears in the sidebar, and mock responses are generated.
* **Resolution**: Ensure `GEMINI_API_KEY` is added to Streamlit secrets or configured in your local `.env` or `.streamlit/secrets.toml`.

### 2. Database Write / Permission Denied
* **Symptom**: App logs warning that database could not be created or written.
* **Resolution**: The SQLite connection automatically detects write permission restrictions. If writing to the folder fails, the app automatically switches to an in-memory database (`sqlite:///:memory:`), meaning the app remains fully functional, although database changes will not persist across app restarts.

### 3. SentenceTransformers Loading Time
* **Symptom**: First loading of "Intelligent Candidate Ranker" takes 15-20 seconds.
* **Resolution**: The model `all-MiniLM-L6-v2` is loaded lazily and cached in memory. Subsequent runs and other pages will run instantly.

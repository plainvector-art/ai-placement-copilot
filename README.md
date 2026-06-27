# 🎯 AI Interview & Placement Copilot

> A production-grade, AI-powered career placement readiness platform built with FastAPI + Streamlit + Gemini.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini-1.5%20Flash-orange?logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

---

## 🌟 Key Features

| Feature | Description |
| :--- | :--- |
| 📄 **Resume Analysis** | PDF/DOCX parsing with ATS scoring (0-100) across 6 core dimensions. |
| 🎯 **Skill Gap Analysis** | Compare skills against 12+ target roles using interactive radar charts. |
| 📊 **Readiness Score** | Composite placement readiness score with actionable breakdown. |
| ❓ **Interview Prep** | 40+ personalized, AI-generated questions (HR, Technical, Project, Behavioral). |
| 🤖 **Mock Interview** | Real-time chat-based mock interview simulator with scoring & feedback. |
| 🗺️ **Learning Roadmap** | Customized 30/60/90-day & 6-month step-by-step roadmap. |
| 📋 **JD Matcher** | Compare your resume against any Job Description for keyword alignment. |
| 💬 **Career Coach** | AI chatbot loaded with your full resume context. |
| 🚀 **Project Ideas** | Get role-specific project recommendations with estimated impact scores. |
| 📈 **Analytics** | Full interactive Plotly dashboard tracking placement metrics. |
| ✉️ **Cover Letter** | AI-generated tailored cover letters mapping to projects in your resume. |
| 🔗 **LinkedIn Profile** | Optimized headline & "About" section generator. |
| 🚀 **Career Path** | 5-year career progression and salary trajectory predictor. |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit Frontend                  │
│    10 Feature Pages + Custom CSS + Plotly Charts     │
└─────────────┬───────────────────────────────────────┘
              │ Direct Python calls (no HTTP needed)
┌─────────────▼───────────────────────────────────────┐
│              FastAPI Backend (optional HTTP API)     │
│   /api/v1/resume  /analysis  /interview  /career    │
└─────────────┬───────────────────────────────────────┘
              │
    ┌─────────┼──────────────────────┐
    │         │                      │
┌───▼───┐ ┌──▼───────┐ ┌───────────▼──┐
│SQLite │ │ AI Layer │ │ File Storage │
│  ORM  │ │  Gemini  │ │   uploads/   │
└───────┘ └──────────┘ └──────────────┘
```

---

## ⚡ Quick Start

### Step 1: Clone & Setup

```bash
# Clone the repository
git clone https://github.com/plainvector-art/ai-placement-copilot.git
cd ai-placement-copilot

# Create a virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download required spaCy NLP model
python -m spacy download en_core_web_sm
```

### Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your **Gemini API Key**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   > **How to get a key:** You can get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Step 3: Run the App

You have three options depending on your setup:

* **Option A: Run Frontend + Backend (Recommended)**
  ```bash
  python run.py
  ```
* **Option B: Run Frontend Only (Uses AI services directly)**
  ```bash
  python -m streamlit run frontend/app.py
  ```
* **Option C: Run Backend API Server Only**
  ```bash
  python -m uvicorn backend.main:app --reload
  ```

Once running, open **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```
ai-placement-copilot/
├── backend/
│   ├── api/routes/          # FastAPI route handlers
│   ├── services/            # Core business logic
│   │   ├── ai_client.py     # Gemini & OpenAI client wrapper
│   │   ├── resume_parser.py # PDF/DOCX profile extractor
│   │   ├── ats_scorer.py    # ATS scoring engine
│   │   └── ...
│   ├── database/            # SQLAlchemy database model & ORM
│   ├── data/                # Static data (roles.json, projects.json)
│   └── utils/
├── frontend/
│   ├── app.py               # Streamlit application entry point
│   ├── pages/               # Multi-page feature implementations
│   └── components/          # CSS styling, charts, and reused UI components
├── tests/                   # Pytest suite
├── uploads/                 # Local directory for temporary resume uploads
├── run.py                   # Unified developer launcher script
├── requirements.txt
└── .env.example
```

---

## 🎨 Premium Design System

The application features a custom **dark-mode first design system** inspired by modern platforms like Vercel and Linear:
- **Palette**: Slate backgrounds (`#0a0a0f`), glassmorphism cards (`#16161f`), and gold accents (`#d4af37`).
- **Typography**: Inter & JetBrains Mono fonts.
- **Micro-Animations**: Smooth fade-ins, hover state scale translations, and glowing button frames.
- **UI Customizations**: Streamlit's sidebar layout uses premium custom chevron controls (`»` / `«`) matching the overall style.

---

## 🧪 Running Tests

Ensure your environment is set up, then run:
```bash
pip install pytest
pytest tests/ -v
```

---

## 🚀 Production Deployment

### Streamlit Community Cloud (Easiest)
1. Fork this repository to your GitHub account.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in.
3. Select your repository, branch, and set the entry file to `frontend/app.py`.
4. In **Settings > Secrets**, add `GEMINI_API_KEY = "your_key"`.
5. Deploy!

### Docker Containerization
```bash
# Build the container
docker build -t placement-copilot .

# Run the container
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key placement-copilot
```

---

## 🔧 Configuration Options

The following variables can be configured in your `.env` file:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `—` | **Required** for AI-based features |
| `AI_PROVIDER` | `gemini` | Choose between `gemini` and `openai` |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Selected Gemini model |
| `DATABASE_URL` | `sqlite:///./placement_copilot.db` | Database URL |
| `MAX_UPLOAD_SIZE_MB` | `10` | Max file upload limit |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

# 🧠 AI Data Analyst Pro — Production SaaS Platform

A full-stack, production-level AI Data Analyst platform with user authentication,
PostgreSQL database, 10 specialized AI agents, streaming chat, voice input/output,
and professional report generation.

---

## 🏗️ Architecture

```
User Browser (React + Vite + Tailwind)
         │
    HTTPS REST API
         │
FastAPI Backend (Python)
    ├── JWT Auth
    ├── PostgreSQL (Neon/Supabase - Free)
    ├── File Storage (local/Supabase)
    └── 10 AI Agents
         ├── Groq API (LLM)
         ├── scikit-learn (ML)
         ├── pandas/numpy
         ├── matplotlib/seaborn/plotly
         └── ChromaDB (RAG)
```

---

## 🤖 10 AI Agents

| # | Agent | Technology | Skill |
|---|-------|-----------|-------|
| 1 | Data Cleaning | pandas, numpy | Missing values, duplicates, outliers |
| 2 | EDA | pandas, numpy | Statistics, correlations, distributions |
| 3 | Visualization | matplotlib, seaborn, plotly | 8 chart types (static + interactive) |
| 4 | Business Insights | Groq LLM | Prompt Engineering, Gen AI |
| 5 | Recommendations | Groq LLM | Prompt Engineering, Agentic AI |
| 6 | Forecasting | scikit-learn | Linear/Polynomial Regression, ML |
| 7 | Report Generator | reportlab, python-docx, python-pptx | PDF, DOCX, PPTX |
| 8 | SQL Agent | SQLite, Groq LLM | Natural Language → SQL |
| 9 | Pandas Agent | pandas exec, Groq LLM | Natural Language → Python |
| 10 | Dashboard Agent | pandas, Groq LLM | Auto KPI Dashboard |

---

## 📁 Project Structure

```
ai-analyst-pro/
├── backend/
│   ├── app/
│   │   ├── agents/          ← 10 AI Agents
│   │   ├── api/             ← FastAPI routes (auth, projects, analysis, chat)
│   │   ├── core/            ← Config, Auth, LLM client, File loader, Logging
│   │   ├── db/              ← SQLAlchemy models + async engine
│   │   └── schemas/         ← Pydantic request/response models
│   ├── storage/             ← uploads, charts, reports (auto-created)
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── pages/           ← Landing, Login, Signup, Dashboard, ProjectPage
    │   ├── components/      ← Navbar, UploadZone, PlotlyChart, UI components
    │   ├── context/         ← AuthContext (global login state)
    │   ├── hooks/           ← useSpeechRecognition (mic + TTS)
    │   └── lib/             ← Axios API client
    └── .env
```

---

## ⚙️ Setup & Run

### Step 1: Database Setup (Free)

**Option A: Neon PostgreSQL (Recommended)**
1. Go to https://neon.tech → Create account → New project
2. Copy the connection string

**Option B: Local PostgreSQL**
```bash
createdb ai_analyst_db
```

### Step 2: Backend Setup

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

Edit `.env`:
```
SECRET_KEY=your-random-secret-key-at-least-32-chars
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
GROQ_API_KEY=your_groq_key_here
```

Start backend:
```bash
uvicorn app.main:app --reload --port 8001
```

Visit: http://localhost:8001/docs (Interactive API docs)

### Step 3: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

---

## 🌟 Features

### Authentication
- ✅ Signup / Login / Logout
- ✅ Email verification (token-based)
- ✅ Forgot / Reset password
- ✅ JWT (Access + Refresh tokens)
- ✅ Change password
- ✅ Delete account

### Dashboard
- ✅ Total projects, reports, chat messages stats
- ✅ Recent projects list
- ✅ Activity log
- ✅ Quick upload

### Analysis (ProjectPage — 10 Tabs)
- ✅ Overview (row count, columns, quality score, data preview)
- ✅ Data Quality (missing values, cleaning suggestions, one-click clean)
- ✅ EDA (mean, median, mode, variance, skewness, correlations)
- ✅ Charts (8 interactive Plotly charts)
- ✅ Dashboard (Auto KPI cards, top performers, executive summary)
- ✅ Insights (8-10 detailed LLM-generated insights)
- ✅ Recommendations (6-8 actionable LLM recommendations)
- ✅ Forecast (ML model, R² score, accuracy, forecast chart)
- ✅ Chat (streaming, voice input, TTS, memory, agent routing)
- ✅ Reports (PDF + DOCX + PPTX download)

### Smart Chat
- ✅ Auto-detects which agent to use (SQL/Pandas/Chart/Forecast/General)
- ✅ Column auto-mapping ("price" → "revenue" if price doesn't exist)
- ✅ Conversation memory (last 10 messages)
- ✅ Language auto-detect (English/Urdu/Hindi/Hinglish)
- ✅ Voice input (mic button) — Chrome/Edge only
- ✅ Text-to-speech output
- ✅ Streaming responses (Server-Sent Events)
- ✅ Suggested follow-up questions
- ✅ Chat history saved in PostgreSQL

---

## 🛠️ Skills Used

| Skill | Where |
|-------|-------|
| Python | Entire backend |
| pandas / numpy | Agents 1, 2, 3, 6, 9 |
| Matplotlib / Seaborn | Static charts (Agent 3) |
| Plotly | Interactive charts (Agent 3) |
| scikit-learn | Forecasting Agent (Agent 6) |
| FastAPI | All API routes |
| SQLAlchemy (async) | Database ORM |
| PostgreSQL | Production database |
| JWT Authentication | User auth system |
| Groq LLM | Agents 4, 5, 8, 9, 10, Chat |
| Prompt Engineering | All LLM agents |
| RAG (ChromaDB) | Document chat |
| Agentic AI | 10-agent orchestration pipeline |
| MLOps concepts | Logging, retry, error handling |
| React.js | Frontend UI |
| Tailwind CSS | Styling |
| React Router | Page navigation |
| Axios | HTTP client |
| Web Speech API | Voice input + TTS |
| Streaming (SSE) | Real-time chat responses |

---

## ☁️ Free Deployment

| Service | Platform | Free Tier |
|---------|----------|-----------|
| Frontend | Vercel | ✅ Free |
| Backend | Render | ✅ Free |
| Database | Neon PostgreSQL | ✅ Free |
| File Storage | Supabase Storage | ✅ Free |
| AI | Groq API | ✅ Free |

---

## ⚠️ Important Notes

1. **Never commit .env** — it contains your API keys
2. **Groq free tier** has rate limits — if you see 503 errors, wait 60 seconds
3. **Voice input** works in Chrome and Edge only (Web Speech API)
4. **PostgreSQL required** — the app will fail to start without a valid DATABASE_URL
5. **Email verification** — in development, the token is returned in the API response
   (in production, configure SMTP to send actual emails)

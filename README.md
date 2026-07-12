<div align="center">

# 🚀 InsightFlow

### AI-Powered Data Analytics SaaS Platform

Transform raw datasets into meaningful insights with Artificial Intelligence, Machine Learning, and Interactive Dashboards.

<p align="center">

<a href="https://insight-flow-chi-smoky.vercel.app">
<img src="https://img.shields.io/badge/🌐_Live_Demo-Vercel-000000?style=for-the-badge"/>
</a>

<a href="https://insightflow-production-6395.up.railway.app/docs">
<img src="https://img.shields.io/badge/API-Swagger-success?style=for-the-badge"/>
</a>

<a href="https://insightflow-production-6395.up.railway.app">
<img src="https://img.shields.io/badge/Backend-Railway-purple?style=for-the-badge"/>
</a>

</p>

<p align="center">

<img src="https://img.shields.io/badge/Python-3.11-blue"/>
<img src="https://img.shields.io/badge/FastAPI-Production-green"/>
<img src="https://img.shields.io/badge/React-18-61DAFB"/>
<img src="https://img.shields.io/badge/PostgreSQL-Neon-336791"/>
<img src="https://img.shields.io/badge/AI-Groq-orange"/>
<img src="https://img.shields.io/badge/Deployment-Vercel%20%7C%20Railway-black"/>

</p>

</div>

---

# 🌍 Live Demo

| Service | URL |
|----------|-----|
| **Frontend** | https://insight-flow-chi-smoky.vercel.app |
| **Backend API** | https://insightflow-production-6395.up.railway.app |
| **Swagger Docs** | https://insightflow-production-6395.up.railway.app/docs |

---

# 📖 About InsightFlow

InsightFlow is a **Production-Level AI SaaS Platform** designed to help users analyze datasets without writing code.

Instead of manually cleaning data, creating charts, calculating statistics, or writing SQL queries, users simply upload a dataset and InsightFlow performs the complete analysis automatically using multiple AI Agents.

The platform combines **Artificial Intelligence**, **Machine Learning**, **Business Intelligence**, and **Modern Web Technologies** into a single application.

---

# ✨ Core Features

## 👤 Authentication

- JWT Authentication
- User Registration
- Secure Login
- Password Hashing
- Protected API Routes

---

## 📂 Dataset Upload

Supports

- CSV
- Excel
- JSON
- Parquet
- PDF
- TXT

---

## 📊 Automatic Data Analysis

- Data Quality Detection
- Missing Values Detection
- Duplicate Detection
- Outlier Detection
- Statistical Analysis
- Interactive Charts
- Dashboard Generation

---

## 🤖 AI Powered Features

- AI Business Insights
- AI Recommendations
- Smart Dataset Chat
- Forecasting
- Automated Reports

---

# 🏗 System Architecture

```text
                              USER
                                │
                                ▼
                     React Frontend (Vercel)
                                │
                     REST API Requests (Axios)
                                │
                                ▼
                    FastAPI Backend (Railway)
                                │
        ┌──────────────┬───────────────┬──────────────┐
        │              │               │              │
        ▼              ▼               ▼              ▼

   AI Agents      Authentication    PostgreSQL     File Storage
                                   (Neon Cloud)   (Local Storage)

        │
        ▼

Business Insights
Charts
Forecast
Reports
Dashboard
Chat
```

---

# 🔄 Complete Request Flow

```text
User

↓

Login

↓

Upload Dataset

↓

Backend validates file

↓

Dataset stored

↓

AI Agents execute

↓

Data Cleaning

↓

EDA

↓

Visualization

↓

Insights

↓

Recommendations

↓

Forecasting

↓

Reports

↓

Results returned to Frontend
```

---

# 📂 Project Structure

```text
InsightFlow
│
├── backend/
│
│   ├── app/
│   │
│   ├── agents/
│   │      ├── Data Cleaning Agent
│   │      ├── EDA Agent
│   │      ├── Visualization Agent
│   │      ├── Dashboard Agent
│   │      ├── Insight Agent
│   │      ├── Recommendation Agent
│   │      ├── Forecast Agent
│   │      ├── SQL Agent
│   │      ├── Pandas Agent
│   │      ├── Smart Chat Agent
│   │      └── Report Agent
│   │
│   ├── api/
│   │      ├── auth.py
│   │      ├── projects.py
│   │      ├── analysis.py
│   │      └── chat.py
│   │
│   ├── core/
│   │      ├── config.py
│   │      ├── auth.py
│   │      ├── llm_client.py
│   │      ├── logging_config.py
│   │      ├── exceptions.py
│   │      └── file_loader.py
│   │
│   ├── db/
│   │      └── database.py
│   │
│   ├── schemas/
│   │
│   ├── storage/
│   │      ├── uploads/
│   │      ├── charts/
│   │      └── reports/
│   │
│   ├── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│
│   ├── src/
│   │
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── context/
│   ├── lib/
│   ├── App.jsx
│   └── main.jsx
│
├── README.md
│
└── .gitignore
```

---

# 📦 Backend Folder Explanation

| Folder | Purpose |
|----------|----------|
| **agents/** | AI agents responsible for data cleaning, visualization, forecasting, reporting, recommendations and chat |
| **api/** | FastAPI endpoints used by the frontend |
| **core/** | Authentication, configuration, logging, exceptions and LLM integration |
| **db/** | SQLAlchemy models and PostgreSQL database connection |
| **schemas/** | Request and response validation models |
| **storage/** | Stores uploaded datasets, generated charts and reports |
| **main.py** | Entry point of the FastAPI application |

---

# 🎨 Frontend Folder Explanation

| Folder | Purpose |
|----------|----------|
| **pages/** | Application screens |
| **components/** | Reusable UI components |
| **context/** | Authentication state management |
| **hooks/** | Custom React hooks |
| **lib/** | Axios API client |
| **App.jsx** | Application routing |
| **main.jsx** | React entry point |


# 🗄 Database Architecture

InsightFlow uses **PostgreSQL (Neon Cloud Database)** as its primary database.

```
                PostgreSQL (Neon)
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼

     Users         Projects      Chat Messages
        │               │                │
        └───────────────┼────────────────┘
                        ▼

                  Reports

                        │

                        ▼

                 Activity Logs
```

---

## Database Tables

### 👤 users

Stores user authentication and profile information.

| Column | Description |
|---------|-------------|
| id | User ID |
| email | User Email |
| password_hash | Encrypted Password |
| created_at | Registration Date |
| last_login | Last Login |

---

### 📂 projects

Stores uploaded datasets.

| Column | Description |
|---------|-------------|
| id | Project ID |
| user_id | Owner |
| filename | Dataset Name |
| file_path | Dataset Location |
| quality_score | Data Quality |
| rows | Total Rows |
| columns | Total Columns |

---

### 💬 chat_messages

Stores complete AI conversation history.

| Column | Description |
|---------|-------------|
| id | Chat ID |
| project_id | Dataset |
| role | User / Assistant |
| message | Conversation |
| created_at | Timestamp |

---

### 📄 reports

Stores generated reports.

| Column | Description |
|---------|-------------|
| id | Report ID |
| project_id | Dataset |
| report_type | PDF / DOCX / PPTX |
| report_path | File Location |

---

### 📊 activity_logs

Tracks every user activity.

Examples

- Login
- Upload
- Chat
- Report Generation
- Forecast

---

# 🤖 AI Agent Architecture

InsightFlow uses multiple specialized AI Agents.

Each agent performs one dedicated task.

```
Dataset

      │

      ▼

Data Cleaning Agent

      │

      ▼

EDA Agent

      │

      ▼

Visualization Agent

      │

      ▼

Insight Agent

      │

      ▼

Recommendation Agent

      │

      ▼

Forecast Agent

      │

      ▼

Dashboard Agent

      │

      ▼

Smart Chat Agent

      │

      ▼

Report Agent

      │

      ▼

User
```

---

# 🤖 AI Agents

## 🧹 Data Cleaning Agent

Responsible for

- Missing Values
- Duplicate Detection
- Outlier Detection
- Quality Score

---

## 📈 EDA Agent

Calculates

- Mean
- Median
- Mode
- Variance
- Standard Deviation
- Correlation
- Distribution

---

## 📊 Visualization Agent

Creates

- Bar Charts
- Line Charts
- Pie Charts
- Scatter Charts
- Histograms
- Heatmaps
- Plotly Interactive Charts

---

## 💡 Insight Agent

Uses LLM to generate

- Business Insights
- Trend Detection
- Hidden Patterns

---

## 🎯 Recommendation Agent

Generates

- Business Recommendations
- Improvement Suggestions
- Action Plans

---

## 🔮 Forecast Agent

Uses Machine Learning

- Linear Regression
- Polynomial Regression
- R² Score
- MAE

---

## 🗄 Dashboard Agent

Automatically generates

- KPI Cards
- Executive Summary
- Dataset Overview

---

## 💬 Smart Chat Agent

Allows users to

- Ask questions
- Chat with Dataset
- Generate AI Responses

---

## 📄 Report Agent

Exports

- PDF
- DOCX
- PPTX

---

# 🌐 API Endpoints

## Authentication

```
POST   /auth/signup

POST   /auth/login

GET    /auth/me

POST   /auth/forgot-password

POST   /auth/reset-password
```

---

## Projects

```
POST   /projects/upload

GET    /projects/

GET    /projects/{id}

DELETE /projects/{id}

GET    /projects/dashboard/stats
```

---

## Analysis

```
GET  /analyze/quality

GET  /analyze/eda

GET  /analyze/charts

GET  /analyze/dashboard

GET  /analyze/insights

GET  /analyze/recommendations

POST /analyze/forecast

POST /analyze/report
```

---

## Chat

```
POST /chat/{project_id}

GET /chat/{project_id}/history

DELETE /chat/{project_id}/history
```

---

# ⚙ Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- AsyncIO
- JWT Authentication
- Pydantic

---

## Frontend

- React
- Vite
- Axios
- React Router
- Tailwind CSS

---

## Artificial Intelligence

- Groq API
- Llama 3.3
- Prompt Engineering

---

## Machine Learning

- Pandas
- NumPy
- Scikit-learn

---

## Visualization

- Plotly
- Matplotlib
- Seaborn

---

## Database

- PostgreSQL
- Neon Database

---

## Deployment

- Railway
- Vercel
- GitHub

---

# 🚀 Deployment Architecture

```
Developer

      │

      ▼

GitHub Repository

      │

      ├───────────────┐

      ▼               ▼

 Railway         Vercel

      │               │

      ▼               ▼

 Backend       Frontend

      │

      ▼

 Neon PostgreSQL
```

---

# 📸 Application Screenshots

> Screenshots will be added here.

- Landing Page

- Dashboard

- Upload Dataset

- Charts

- AI Chat

- Reports

- Forecast

---

# 🛣 Roadmap

## Completed

- User Authentication

- JWT Security

- PostgreSQL

- AI Agents

- Dashboard

- Reports

- Forecasting

- AI Chat

- Railway Deployment

- Vercel Deployment

---

## Coming Soon

- Docker

- Docker Compose

- GitHub Actions (CI/CD)

- Redis Cache

- Supabase Storage

- Email Verification

- Team Collaboration

- Mobile App

- Stripe Subscription

---

# 👨‍💻 Developer

## Sami Chohan

AI Engineer | Full Stack AI Developer

GitHub

https://github.com/samichohan

---

# ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

It helps the project reach more developers and motivates future improvements.

---

## 📄 License

This project is licensed under the MIT License.


# 📈 Project Statistics

| Metric | Value |
|---------|------:|
| AI Agents | 10+ |
| REST API Endpoints | 37+ |
| Database Tables | 5 |
| Supported File Formats | 7 |
| Report Formats | 3 |
| Interactive Charts | 8+ |
| Deployment Platforms | 3 |
| Authentication | JWT |
| Database | PostgreSQL |
| Frontend | React + Vite |
| Backend | FastAPI |
| AI Model | Llama 3.3 (Groq) |

---

# 📊 Supported File Formats

| Format | Status |
|---------|--------|
| CSV | ✅ |
| Excel (.xlsx) | ✅ |
| Excel (.xls) | ✅ |
| JSON | ✅ |
| Parquet | ✅ |
| PDF | ✅ |
| TXT | ✅ |

---

# 📊 Generated Analytics

InsightFlow automatically performs:

- ✅ Dataset Overview
- ✅ Missing Value Detection
- ✅ Duplicate Detection
- ✅ Outlier Detection
- ✅ Column Type Detection
- ✅ Data Quality Score
- ✅ Statistical Summary
- ✅ Correlation Analysis
- ✅ Interactive Charts
- ✅ Executive Dashboard
- ✅ Business Insights
- ✅ AI Recommendations
- ✅ Machine Learning Forecast
- ✅ Smart Dataset Chat
- ✅ Professional Reports

---

# 🔐 Security Features

- JWT Authentication
- Password Hashing
- Protected API Routes
- Environment Variables (.env)
- PostgreSQL Authentication
- Input Validation
- File Type Validation
- Upload Size Validation
- Global Exception Handling
- Structured Logging

---

# ⚡ Performance Features

- Async FastAPI
- Async SQLAlchemy
- Axios API Client
- React Context API
- Modular Architecture
- AI Agent Pipeline
- Cloud PostgreSQL
- Interactive Plotly Charts

---

# 🎯 Skills Demonstrated

This project demonstrates practical experience with:

### Backend

- Python
- FastAPI
- REST APIs
- SQLAlchemy
- Async Programming
- Authentication
- API Design

### Frontend

- React
- Vite
- React Router
- Axios
- Tailwind CSS
- Context API

### Data Science

- Pandas
- NumPy
- Statistics
- Data Cleaning
- EDA
- Data Visualization

### Machine Learning

- Scikit-learn
- Linear Regression
- Polynomial Regression
- Forecasting

### Artificial Intelligence

- Large Language Models
- Prompt Engineering
- AI Agents
- Dataset Chat
- AI Insights

### Database

- PostgreSQL
- Neon Database
- ORM Relationships

### Deployment

- GitHub
- Railway
- Vercel

---

# 💼 Why InsightFlow?

Unlike traditional analytics tools, InsightFlow combines:

- Artificial Intelligence
- Business Intelligence
- Machine Learning
- Interactive Visualization
- Conversational Analytics

into one modern SaaS platform.

Users don't need SQL or Python knowledge.

Simply upload a dataset and receive intelligent insights in seconds.

---

# 🆚 Comparison

| Feature | InsightFlow | Traditional BI Tools |
|----------|-------------|----------------------|
| AI Insights | ✅ | ❌ |
| Dataset Chat | ✅ | ❌ |
| Automated Recommendations | ✅ | ❌ |
| Interactive Charts | ✅ | ✅ |
| Dashboard | ✅ | ✅ |
| Forecasting | ✅ | Limited |
| Report Export | ✅ | ✅ |
| Cloud Database | ✅ | ✅ |

---

# 🚀 Future Enhancements

- Docker
- Docker Compose
- GitHub Actions (CI/CD)
- Redis Caching
- Supabase Storage
- Email Verification
- Multi-file Analysis
- Team Collaboration
- Mobile Application
- Stripe Subscription
- Kubernetes
- Monitoring & Logging
- WebSockets
- API Marketplace

---

# 🌟 Highlights

✔ Production-Level Architecture

✔ Cloud PostgreSQL Database

✔ AI-Powered Analytics

✔ Interactive Dashboard

✔ Machine Learning Forecasting

✔ JWT Authentication

✔ Railway Deployment

✔ Vercel Deployment

✔ REST API

✔ Modular Codebase

✔ Scalable Architecture

---

# 🤝 Contributing

Contributions are welcome!

If you'd like to improve InsightFlow:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

# 📬 Contact

**Developer:** Sami Chohan

- GitHub: https://github.com/samichohan
- Project Repository: https://github.com/samichohan/InsightFlow

---

<div align="center">

## ⭐ If you like this project, please consider giving it a Star.

Your support motivates future improvements and helps more developers discover InsightFlow.

Made with ❤️ by **Sami Chohan**

</div>

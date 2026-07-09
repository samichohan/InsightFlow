"""api/analysis.py — All data analysis endpoints (quality, EDA, charts, forecast, insights)."""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db, User, Project, Report, ActivityLog
from app.core.auth import get_current_user
from app.core.file_loader import load_file, is_structured
from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.schemas import ForecastRequest, ReportRequest, CleanRequest
from app.agents.base import PipelineContext, AgentPipeline
from app.agents.data_cleaning_agent import DataCleaningAgent, clean_dataset, save_cleaned_csv
from app.agents.eda_agent import EDAAgent, run_full_eda
from app.agents.visualization_agent import VisualizationAgent, generate_interactive_charts, generate_static_charts
from app.agents.insight_agent import InsightAgent, generate_insights
from app.agents.recommendation_agent import RecommendationAgent, generate_recommendations
from app.agents.forecasting_agent import ForecastingAgent, forecast
from app.agents.dashboard_agent import DashboardAgent, build_dashboard
from app.agents.report_agent import ReportAgent, generate_pdf, generate_docx, generate_pptx
from app.api.projects import PROJECT_SESSIONS

router = APIRouter(prefix="/analyze", tags=["Analysis"])


def _get_session(project_id: str):
    session = PROJECT_SESSIONS.get(project_id)
    if not session:
        raise HTTPException(404, "Project not loaded. Please re-open the project.")
    if session.get("type") != "structured":
        raise HTTPException(400, "This operation requires a structured dataset (CSV/Excel/JSON/Parquet)")
    return session


async def _get_project(project_id: str, user_id: str, db: AsyncSession):
    result = await db.execute(select(Project).where(
        Project.id == project_id, Project.user_id == user_id
    ))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    return project


# ── Data Quality ──────────────────────────────────────────────────────────────
@router.get("/quality/{project_id}")
async def get_quality(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    await _get_project(project_id, current_user.id, db)

    context = PipelineContext()
    context.set("dataframe", session["dataframe"])
    context.set("dataset_name", session["dataset_name"])
    result = DataCleaningAgent().execute(context)

    if result.status.value == "failed":
        raise HTTPException(500, result.error)

    # Cache in session
    PROJECT_SESSIONS[project_id]["quality_report"] = result.output
    return result.output


# ── Clean Dataset ─────────────────────────────────────────────────────────────
@router.post("/clean/{project_id}")
async def clean_data(
    project_id: str,
    request: CleanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    await _get_project(project_id, current_user.id, db)

    df = session["dataframe"]
    cleaned_df = clean_dataset(df, strategy=request.strategy)
    cleaned_path = save_cleaned_csv(cleaned_df, project_id)

    PROJECT_SESSIONS[project_id]["dataframe"] = cleaned_df
    PROJECT_SESSIONS[project_id]["cleaned_csv_path"] = cleaned_path

    return {
        "message": "Dataset cleaned successfully",
        "rows_before": len(df),
        "rows_after": len(cleaned_df),
        "cleaned_filename": os.path.basename(cleaned_path),
    }


# ── EDA ───────────────────────────────────────────────────────────────────────
@router.get("/eda/{project_id}")
async def get_eda(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    await _get_project(project_id, current_user.id, db)

    result = run_full_eda(session["dataframe"])
    PROJECT_SESSIONS[project_id]["eda_report"] = result
    return result


# ── Charts ────────────────────────────────────────────────────────────────────
@router.get("/charts/{project_id}")
async def get_charts(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    await _get_project(project_id, current_user.id, db)

    df = session["dataframe"]
    interactive = generate_interactive_charts(df)
    static = generate_static_charts(df)

    PROJECT_SESSIONS[project_id]["charts"] = interactive
    PROJECT_SESSIONS[project_id]["static_charts"] = static

    return {"interactive": interactive, "static_paths": static}


# ── Forecast ──────────────────────────────────────────────────────────────────
@router.post("/forecast/{project_id}")
async def get_forecast(
    project_id: str,
    request: ForecastRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    await _get_project(project_id, current_user.id, db)

    result = forecast(
        session["dataframe"],
        request.date_column,
        request.value_column,
        request.periods_ahead,
        request.use_polynomial,
    )
    PROJECT_SESSIONS[project_id]["forecast"] = result
    return result


# ── AI Insights ───────────────────────────────────────────────────────────────
@router.get("/insights/{project_id}")
async def get_insights(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    await _get_project(project_id, current_user.id, db)

    quality = session.get("quality_report") or DataCleaningAgent().execute(
        _build_context(session)
    ).output or {}
    eda = session.get("eda_report") or run_full_eda(session["dataframe"])

    insights = generate_insights(quality, eda, session["dataset_name"])
    PROJECT_SESSIONS[project_id]["insights"] = insights
    return {"insights": insights}


# ── Recommendations ───────────────────────────────────────────────────────────
@router.get("/recommendations/{project_id}")
async def get_recommendations(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    await _get_project(project_id, current_user.id, db)

    insights = session.get("insights")
    if not insights:
        quality = session.get("quality_report") or {}
        eda = session.get("eda_report") or run_full_eda(session["dataframe"])
        insights = generate_insights(quality, eda, session["dataset_name"])
        PROJECT_SESSIONS[project_id]["insights"] = insights

    recs = generate_recommendations(insights, session["dataset_name"])
    PROJECT_SESSIONS[project_id]["recommendations"] = recs
    return {"recommendations": recs}


# ── Dashboard ─────────────────────────────────────────────────────────────────
@router.get("/dashboard/{project_id}")
async def get_dashboard(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    await _get_project(project_id, current_user.id, db)

    df = session["dataframe"]
    insights = session.get("insights", [])
    charts = session.get("charts", {})

    return build_dashboard(df, session["dataset_name"], insights, charts)


# ── Report Generation ─────────────────────────────────────────────────────────
@router.post("/report/{project_id}")
async def generate_report(
    project_id: str,
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = _get_session(project_id)
    project = await _get_project(project_id, current_user.id, db)

    df = session["dataframe"]
    name = session["dataset_name"]

    # Run any missing pipeline steps
    quality = session.get("quality_report") or DataCleaningAgent().execute(_build_context(session)).output or {}
    eda = session.get("eda_report") or run_full_eda(df)
    insights = session.get("insights") or generate_insights(quality, eda, name)
    recs = session.get("recommendations") or generate_recommendations(insights, name)
    static_charts = session.get("static_charts") or generate_static_charts(df)
    fc = session.get("forecast")

    # Generate
    if request.format == "docx":
        path = generate_docx(name, quality, eda, insights, recs, static_charts, fc)
    elif request.format == "pptx":
        path = generate_pptx(name, insights, recs)
    else:
        path = generate_pdf(name, quality, eda, insights, recs, static_charts, fc)

    # Save to DB
    report = Report(
        id=str(uuid.uuid4()),
        project_id=project_id,
        format=request.format,
        file_path=path,
    )
    db.add(report)
    await db.commit()

    return {
        "report_path": path,
        "filename": os.path.basename(path),
        "format": request.format,
    }


# ── Download ─────────────────────────────────────────────────────────
@router.get("/download/report/{filename}")
async def download_report(filename: str):  
    path = os.path.join(settings.REPORT_DIR, os.path.basename(filename))
    if not os.path.exists(path):
        raise HTTPException(404, "Report file not found")
    return FileResponse(path, filename=filename)

@router.get("/download/dataset/{project_id}")
async def download_cleaned(project_id: str):
    session = PROJECT_SESSIONS.get(project_id, {})
    path = session.get("cleaned_csv_path")
    if not path or not os.path.exists(path):
        raise HTTPException(404, "Please run 'Clean Dataset' first from the Data Quality tab.")
    return FileResponse(path, filename=f"cleaned_dataset.csv", media_type="text/csv")

@router.get("/download/chart/{filename}")
async def download_report(filename: str):
    path = os.path.join(settings.CHART_DIR, os.path.basename(filename))
    if not os.path.exists(path):
        raise HTTPException(404, "Chart not found")
    return FileResponse(path, filename=filename)


def _build_context(session: dict) -> PipelineContext:
    ctx = PipelineContext()
    ctx.set("dataframe", session["dataframe"])
    ctx.set("dataset_name", session.get("dataset_name", "dataset"))
    return ctx

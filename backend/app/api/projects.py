"""api/projects.py — Project/file upload management routes."""

import os
import uuid
import shutil
from datetime import datetime
from app.core.supabase_client import supabase, BUCKET_NAME
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.db.database import get_db, User, Project, ChatMessage, Report, ActivityLog
from app.core.auth import get_current_user, get_verified_user
from app.core.config import settings
from app.core.file_loader import load_file, extract_pdf_text, extract_txt_text, is_structured
from app.core.exceptions import FileError
from app.core.logging_config import logger
from app.agents.data_cleaning_agent import analyze_quality
from app.schemas.schemas import ProjectResponse, DashboardStatsResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

# In-memory session store (holds loaded DataFrames)
PROJECT_SESSIONS: dict = {}


async def _log_activity(db: AsyncSession, user_id: str, action: str, detail: str = ""):
    log = ActivityLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        detail=detail,
    )
    db.add(log)


# ── Upload File / Create Project ──────────────────────────────────────────────
@router.post("/upload", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(413, f"File too large. Max: {settings.MAX_UPLOAD_SIZE_MB}MB")

    project_id = str(uuid.uuid4())
    save_path = os.path.join(settings.UPLOAD_DIR, f"{project_id}{ext}")

    storage_path = f"{project_id}/{file.filename}"

    with open(save_path, "wb") as f:
        f.write(contents)

    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=contents,
            file_options={
                "content-type": file.content_type
            }
        )
    except Exception as e:
        raise HTTPException(500, f"Supabase upload failed: {e}")

      


    # Load and analyze
    total_rows = total_cols = quality_score = None
    col_metadata = {}
    session_type = "document"

    if is_structured(save_path):
        try:
            df = load_file(save_path)
            total_rows = len(df)
            total_cols = len(df.columns)
            col_metadata = {
                "columns": list(df.columns),
                "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
                "column_types": {
                    col: ("numeric" if str(dt) in ["int64","float64","int32","float32"] else "categorical")
                    for col, dt in df.dtypes.items()
                }
            }
            quality = analyze_quality(df)
            quality_score = quality["data_quality_score"]
            session_type = "structured"

            # Store in session
            PROJECT_SESSIONS[project_id] = {
                "dataframe": df,
                "type": "structured",
                "dataset_name": file.filename,
                "column_metadata": col_metadata,
            }

        except Exception as e:
            logger.error(f"Could not load file: {e}")

    elif ext == ".pdf":
        text = extract_pdf_text(save_path)
        PROJECT_SESSIONS[project_id] = {"type": "document", "text": text, "dataset_name": file.filename}
    elif ext == ".txt":
        text = extract_txt_text(save_path)
        PROJECT_SESSIONS[project_id] = {"type": "document", "text": text, "dataset_name": file.filename}

    # Save to DB
    project = Project(
        id=project_id,
        user_id=current_user.id,
        name=file.filename.rsplit(".", 1)[0],
        filename=file.filename,
        file_path=storage_path,
        file_type=ext.lstrip("."),
        file_size_mb=round(size_mb, 2),
        total_rows=total_rows,
        total_columns=total_cols,
        quality_score=quality_score,
        column_metadata=col_metadata,
    )
    db.add(project)
    await _log_activity(db, current_user.id, "upload", f"Uploaded {file.filename}")
    await db.commit()
    await db.refresh(project)

    logger.info(f"File uploaded: {file.filename} → project {project_id}")

    df = PROJECT_SESSIONS.get(project_id, {}).get("dataframe")


    preview = (
    df.head(10).fillna("").to_dict(orient="records")
    if df is not None
    else []
    )


    return {
        "project_id": project_id,
        "filename": file.filename,
        "type": session_type,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "quality_score": quality_score,
        "columns": col_metadata.get("columns", []),
        "column_types": col_metadata.get("column_types", {}),
         "preview": preview,
    }


# ── List Projects ─────────────────────────────────────────────────────────────
@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(desc(Project.created_at))
    )
    return result.scalars().all()


# ── Get Single Project ────────────────────────────────────────────────────────
@router.get("/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(
        Project.id == project_id, Project.user_id == current_user.id
    ))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    # # Reload into session if not loaded
    # if project_id not in PROJECT_SESSIONS:
    #     if is_structured(project.file_path):
    #         try:
    #             df = load_file(project.file_path)
    #             PROJECT_SESSIONS[project_id] = {
    #                 "dataframe": df, "type": "structured",
    #                 "dataset_name": project.filename,
    #                 "column_metadata": project.column_metadata or {},
    #             }
    #         except:
    #             pass

    session = PROJECT_SESSIONS.get(project_id, {})

    return {
        "id": project.id,
        "name": project.name,
        "filename": project.filename,
        "type": project.file_type,
        "total_rows": project.total_rows,
        "total_columns": project.total_columns,
        "quality_score": project.quality_score,
        "columns": (project.column_metadata or {}).get("columns", []),
        "column_types": (project.column_metadata or {}).get("column_types", {}),
        "created_at": project.created_at,
        "is_loaded": project_id in PROJECT_SESSIONS,
    }


# ── Delete Project ────────────────────────────────────────────────────────────
@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(
        Project.id == project_id, Project.user_id == current_user.id
    ))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")


    # TODO: Delete file from Supabase Storage
    # Local delete disabled because files are now stored in Supabase.
    # # Remove file from disk
    # if os.path.exists(project.file_path):
    #     os.remove(project.file_path)

    # Remove from session
    PROJECT_SESSIONS.pop(project_id, None)

    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted successfully"}


# ── Dashboard Stats ───────────────────────────────────────────────────────────
@router.get("/dashboard/stats")
async def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Count projects
    p_count = await db.execute(
        select(func.count()).where(Project.user_id == current_user.id)
    )
    total_projects = p_count.scalar()

    # Count reports
    r_count = await db.execute(
        select(func.count(Report.id))
        .join(Project, Report.project_id == Project.id)
        .where(Project.user_id == current_user.id)
    )
    total_reports = r_count.scalar()

    # Count chat messages
    c_count = await db.execute(
        select(func.count(ChatMessage.id))
        .join(Project, ChatMessage.project_id == Project.id)
        .where(Project.user_id == current_user.id)
    )
    total_chats = c_count.scalar()

    # Recent projects
    recent = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(desc(Project.created_at))
        .limit(5)
    )
    recent_projects = recent.scalars().all()

    # Activity logs
    logs = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.user_id == current_user.id)
        .order_by(desc(ActivityLog.created_at))
        .limit(10)
    )
    activity = logs.scalars().all()

    return {
        "total_projects": total_projects,
        "total_reports": total_reports,
        "total_chats": total_chats,
        "last_login": current_user.last_login,
        "recent_projects": [
            {"id": p.id, "name": p.name, "filename": p.filename,
             "total_rows": p.total_rows, "created_at": p.created_at}
            for p in recent_projects
        ],
        "recent_activity": [
            {"action": l.action, "detail": l.detail, "time": l.created_at}
            for l in activity
        ],
    }

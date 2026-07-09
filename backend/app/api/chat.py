"""
api/chat.py — Smart Chat routes with streaming, memory, agent routing.
"""

import uuid
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.database import get_db, User, Project, ChatMessage
from app.core.auth import get_current_user
from app.schemas.schemas import ChatRequest, ChatMessageResponse
from app.agents.smart_chat_agent import process_chat_message, stream_chat_message
from app.api.projects import PROJECT_SESSIONS
from app.core.logging_config import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


async def _get_project_and_session(project_id: str, user_id: str, db: AsyncSession):
    result = await db.execute(select(Project).where(
        Project.id == project_id, Project.user_id == user_id
    ))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    session = PROJECT_SESSIONS.get(project_id)
    if not session:
        raise HTTPException(404, "Project not loaded. Please re-open the project.")

    return project, session


async def _get_conversation_history(project_id: str, db: AsyncSession, limit: int = 10) -> list:
    """Get last N chat messages for conversation memory."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.project_id == project_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()
    # Return in chronological order for LLM
    return [{"role": m.role, "content": m.content} for m in reversed(messages)]


async def _save_message(db: AsyncSession, project_id: str, role: str,
                         content: str, agent_used: str = None, chart_data: dict = None):
    msg = ChatMessage(
        id=str(uuid.uuid4()),
        project_id=project_id,
        role=role,
        content=content,
        agent_used=agent_used,
        chart_data=chart_data,
    )
    db.add(msg)
    await db.commit()
    return msg


# ── Regular Chat (full response at once) ─────────────────────────────────────
@router.post("/{project_id}")
async def chat(
    project_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project, session = await _get_project_and_session(project_id, current_user.id, db)

    # Get conversation history for memory
    history = await _get_conversation_history(project_id, db)

    # Process message
    if session["type"] == "structured":
        result = process_chat_message(
            df=session["dataframe"],
            question=request.message,
            dataset_name=session["dataset_name"],
            conversation_history=history,
            pre_computed={
                "insights": session.get("insights"),
                "charts": session.get("charts"),
            }
        )
    else:
        # Document RAG mode
        from app.agents.smart_chat_agent import build_data_context
        result = {
            "answer": "Document chat coming soon. Please upload a structured dataset (CSV/Excel) for full chat support.",
            "agent_used": "general",
            "chart_data": None,
            "follow_ups": [],
        }

    # Save user message + assistant response to DB
    await _save_message(db, project_id, "user", request.message)
    assistant_msg = await _save_message(
        db, project_id, "assistant",
        result["answer"],
        agent_used=result.get("agent_used"),
        chart_data=result.get("chart_data"),
    )

    return {
        "id": assistant_msg.id,
        "answer": result["answer"],
        "agent_used": result.get("agent_used"),
        "chart_data": result.get("chart_data"),
        "additional_data": result.get("additional_data"),
        "follow_ups": result.get("follow_ups", []),
        "language": result.get("language", "english"),
        "created_at": assistant_msg.created_at,
    }


# ── Streaming Chat (Server-Sent Events) ───────────────────────────────────────
@router.post("/{project_id}/stream")
async def chat_stream(
    project_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Streaming chat — returns words one by one (ChatGPT style).
    Frontend uses EventSource or fetch with ReadableStream to consume.
    """
    project, session = await _get_project_and_session(project_id, current_user.id, db)

    if session["type"] != "structured":
        raise HTTPException(400, "Streaming chat requires structured dataset")

    history = await _get_conversation_history(project_id, db)

    # Save user message first
    await _save_message(db, project_id, "user", request.message)

    async def event_generator():
        full_response = []
        try:
            async for chunk in stream_chat_message(
                df=session["dataframe"],
                question=request.message,
                dataset_name=session["dataset_name"],
                conversation_history=history,
            ):
                full_response.append(chunk)
                # SSE format: "data: chunk\n\n"
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Save complete response to DB
            complete = "".join(full_response)
            msg_id = str(uuid.uuid4())
            msg = ChatMessage(
                id=msg_id,
                project_id=project_id,
                role="assistant",
                content=complete,
                agent_used="streaming",
            )
            db.add(msg)
            await db.commit()

            # Send completion signal
            yield f"data: {json.dumps({'done': True, 'id': msg_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


# ── Chat History ──────────────────────────────────────────────────────────────
@router.get("/{project_id}/history")
async def get_chat_history(
    project_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify project belongs to user
    result = await db.execute(select(Project).where(
        Project.id == project_id, Project.user_id == current_user.id
    ))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Project not found")

    msgs = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.project_id == project_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    )
    messages = msgs.scalars().all()

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "agent_used": m.agent_used,
            "chart_data": m.chart_data,
            "created_at": m.created_at,
        }
        for m in messages
    ]


# ── Clear Chat History ────────────────────────────────────────────────────────
@router.delete("/{project_id}/history")
async def clear_history(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(
        Project.id == project_id, Project.user_id == current_user.id
    ))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Project not found")

    msgs = await db.execute(
        select(ChatMessage).where(ChatMessage.project_id == project_id)
    )
    for msg in msgs.scalars().all():
        await db.delete(msg)
    await db.commit()

    return {"message": "Chat history cleared"}

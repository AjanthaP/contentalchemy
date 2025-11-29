"""FastAPI application exposing content workflows."""
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi import FastAPI
from src.integrations.linkedin_oauth import router as linkedin_router
from fastapi.middleware.cors import CORSMiddleware

from src.api import schemas
from src.api.dependencies import get_conversation_manager, get_profile_manager
from src.core.config import settings
from src.optimization.content_validator import ContentValidator
from src.workflow.langgraph_flow import generate_content as run_workflow
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="ContentAlchemAI", version=settings.app_version)
app.include_router(linkedin_router, prefix="/api")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://contentalchemy.vercel.app")
allowed_origins_list = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=schemas.HealthResponse)
async def health() -> schemas.HealthResponse:
    return schemas.HealthResponse()


@app.get("/api/profile/{user_email}", response_model=schemas.ProfileResponse)
async def fetch_profile(user_email: str, profile_manager=Depends(get_profile_manager)):
    profile = profile_manager.get_profile(user_email)
    return schemas.ProfileResponse(user_email=user_email, profile=profile)


@app.put("/api/profile/{user_email}", response_model=schemas.ProfileResponse)
async def update_profile(
    user_email: str,
    payload: schemas.ProfileUpdateRequest,
    profile_manager=Depends(get_profile_manager),
):
    updates = payload.model_dump(exclude_unset=True)
    profile_manager.update_profile(user_email, updates)
    profile = profile_manager.get_profile(user_email)
    return schemas.ProfileResponse(user_email=user_email, profile=profile)


@app.post("/api/generate", response_model=schemas.GenerateResponse)
async def generate_content(payload: schemas.GenerateRequest):
    session_id, conversation_manager = get_conversation_manager(payload.session_id)

    metadata = {
        "content_type": payload.content_type,
        "tone": payload.tone,
        "enable_seo": payload.enable_seo,
        "include_sources": payload.include_sources,
        "target_words": payload.target_words,
        "target_audience": payload.target_audience,
        "keywords": payload.keywords,
        "additional_notes": payload.additional_notes,
        "override": payload.override,
    }
    conversation_manager.add_message("user", payload.user_query, metadata)

    enriched_query = payload.user_query
    if payload.target_audience:
        enriched_query += f"\n\nTarget Audience: {payload.target_audience}"
    if payload.keywords:
        enriched_query += f"\n\nKeywords: {payload.keywords}"
    if payload.additional_notes:
        enriched_query += f"\n\nAdditional Notes: {payload.additional_notes}"

    result = run_workflow(
        query=enriched_query,
        content_type=payload.content_type,
        user_profile=getattr(payload, "user_profile", None),
        session_id=payload.session_id
    )
    # Patch: handle Stable Diffusion base64 output
    image_url = result.get("image_url")
    if not image_url and result.get("image_base64"):
        image_url = f"data:image/png;base64,{result['image_base64']}"
        result["image_url"] = image_url
    if not image_url and not result.get("image_base64") and result.get("image_object"):
        image_url = f"data:image/png;base64,{result['image_object']}"
        result["image_url"] = image_url
    final_content = result.get("final_content", "")
    conversation_manager.add_message("assistant", final_content, {"result": result})

    validator = None
    if payload.content_type in {"blog", "research"} and final_content:
        validator = ContentValidator().validate_content(final_content, payload.content_type)

    conversation_manager.save_session(session_id)
    conversation = schemas.ConversationResponse(
        session_id=session_id,
        messages=list(conversation_manager.current_session),
    )

    # Ensure content_type is valid for GenerateResponse
    valid_types = {"research", "blog", "linkedin", "image", "strategy"}
    response_content_type = result.get("content_type", payload.content_type)
    if response_content_type == "research_report":
        response_content_type = "research"
    if response_content_type not in valid_types:
        response_content_type = payload.content_type if payload.content_type in valid_types else "research"

    return schemas.GenerateResponse(
        session_id=session_id,
        user_email=getattr(payload, "user_email", "default"),
        content_type=response_content_type,
        final_content=final_content,
        metadata=result.get("metadata", {}),
        analysis=validator,
        image_url=result.get("image_url"),
        image_base64=result.get("image_base64"),
        image_prompt=result.get("image_prompt"),
        sources=result.get("research_report", {}).get("sources", []),
        raw_result=result,
        conversation=conversation,
    )


@app.get("/api/history/{session_id}", response_model=schemas.ConversationHistoryResponse)
async def conversation_history(session_id: str):
    session_id, manager = get_conversation_manager(session_id)
    if not manager.current_session:
        loaded = manager.load_session(session_id)
        manager.current_session = loaded
    if not manager.current_session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return schemas.ConversationHistoryResponse(session_id=session_id, history=manager.current_session)

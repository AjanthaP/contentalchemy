"""Pydantic schemas for the FastAPI layer."""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from src.optimization.content_validator import ValidationResult

ContentTypeLiteral = Literal["research", "blog", "linkedin", "image", "strategy"]


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerateRequest(BaseModel):
    session_id: Optional[str] = None
    user_email: str = "default"
    user_query: str
    content_type: ContentTypeLiteral
    tone: str = "professional"
    enable_seo: bool = True
    include_sources: bool = True
    target_words: Optional[int] = None
    target_audience: Optional[str] = None
    keywords: Optional[str] = None
    additional_notes: Optional[str] = None
    image_size: Optional[str] = None
    image_quality: Optional[str] = None
    image_provider: Optional[str] = None
    
    # ✅ ADD THESE TWO FIELDS
    override: bool = False
    user_profile: Optional[Dict[str, Any]] = None


class ProfileResponse(BaseModel):
    user_email: str
    profile: Dict[str, Any]


class ProfileUpdateRequest(BaseModel):
    preferences: Dict[str, Any] = Field(default_factory=dict)
    brand_voice: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    session_id: str
    messages: List[Message]


class ConversationHistoryResponse(BaseModel):
    session_id: str
    history: List[Message]


class HealthResponse(BaseModel):
    status: str = "ok"


class GenerateResponse(BaseModel):
    session_id: str
    user_email: str
    content_type: ContentTypeLiteral
    final_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    analysis: Optional[ValidationResult] = None
    image_url: Optional[str] = None
    image_prompt: Optional[str] = None
    image_base64: Optional[str] = None
    image_object: Optional[str] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    raw_result: Dict[str, Any] = Field(default_factory=dict)
    conversation: Optional[ConversationResponse] = None
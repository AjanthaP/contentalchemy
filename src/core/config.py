from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum

class ContentType(str, Enum):
    RESEARCH = "research"
    BLOG = "blog"
    LINKEDIN = "linkedin"
    IMAGE = "image"

class Settings(BaseSettings):
    # API Configuration
    openai_api_key: Optional[str] = None
    serp_api_key: Optional[str] = None
    langchain_project: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    #Hugging Face API Key
    hf_api_key: Optional[str] = None
    # Optional API Keys
    perplexity_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Application Settings
    app_name: str = "ContentAlchemy"
    debug: bool = False
    log_level: str = "INFO"
    allowed_origins: Optional[str] = None  # comma-separated; parsed in src/api/app.py
    
    # LLM Settings
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # Image Generation
    dalle_model: str = "gpt-image-2.5-flare"
    dalle_size: str = "1024x1024"
    dalle_quality: str = "standard"
    
    # Content Settings
    max_research_results: int = 10
    blog_min_words: int = 1000
    blog_max_words: int = 2000
    linkedin_max_chars: int = 3000
    
    # Memory Settings
    enable_conversation_memory: bool = True
    max_conversation_history: int = 10
    
    # Redis (Optional)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    use_redis: bool = False
    
    # Extra Settings
    openai_temperature: float = 0.7
    app_version: str = "1.0.0"

    # LinkedIn OAuth
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    linkedin_redirect_uri: Optional[str] = None
    
    # Frontend Base URL
    frontend_base_url: Optional[str] = "http://localhost:5173"

    # Rate limiting (slowapi / "limits" syntax, e.g. "5/minute;50/day")
    rate_limit_enabled: bool = True
    rate_limit_default: str = "120/minute"          # every endpoint, per client IP
    rate_limit_generate: str = "5/minute;50/day"    # /api/generate, per client IP
    rate_limit_generate_global: str = "500/day"     # /api/generate, all callers combined
    # "memory://" is per instance; use e.g. "redis://host:6379/1" to share counts across instances
    rate_limit_storage_uri: str = "memory://"
    # Number of proxies that append to X-Forwarded-For (1 = Cloud Run directly)
    trusted_proxy_hops: int = 1
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env

settings = Settings()

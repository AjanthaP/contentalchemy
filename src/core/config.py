from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum

class ContentType(str, Enum):
    RESEARCH = "research"
    BLOG = "blog"
    LINKEDIN = "linkedin"
    IMAGE = "image"

class Settings(BaseSettings):
    # API Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    serp_api_key: str = ""
    
    # Optional API Keys
    perplexity_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Application Settings
    app_name: str = "ContentAlchemy"
    debug: bool = False
    log_level: str = "INFO"
    
    # LLM Settings
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # Image Generation
    dalle_model: str = "dall-e-3"
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
    
    # Extra Settings
    openai_temperature: float = 0.7
    app_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env

settings = Settings()

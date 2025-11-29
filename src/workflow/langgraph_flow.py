from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import operator
import os

from src.agents.query_handler import QueryHandlerAgent
from src.agents.research_agent import DeepResearchAgent
from src.agents.blog_writer import SEOBlogWriterAgent
from src.agents.linkedin_writer import LinkedInPostAgent
from src.agents.image_generator import ImageGeneratorAgent
from src.agents.content_strategist import ContentStrategistAgent
from src.core.config import settings

# Enable LangSmith tracing
from langsmith import Client

class ContentState(TypedDict, total=False):
    """State for content generation workflow"""
    # Core Input
    user_query: str
    override: bool
    requested_content_type: str
    session_id: Optional[str]
    
    # User Profile Data
    user_profile: dict
    
    # Content Settings
    tone: str
    target_words: int
    keywords: str
    target_audience: str
    enable_seo: bool
    
    # Topic & Research
    topic: str
    key_findings: list
    research_summary: str
    sources: list
    max_results: int
    key_points: list
    
    # Image Settings
    image_provider: str
    image_size: str
    image_quality: str
    
    # UI Override Fields (prefixed with ui_)
    ui_tone: str
    ui_keywords: str
    ui_target_words: int
    ui_target_audience: str
    ui_topic: str
    ui_key_findings: list
    ui_research_summary: str
    ui_sources: list
    ui_user_query: str
    ui_image_size: str
    ui_image_quality: str
    ui_image_provider: str
    ui_max_results: int
    ui_key_points: list
    ui_enable_seo: bool
    
    # Query Analysis
    query_analysis: dict
    intent: str
    requires_research: bool
    
    # Research Results
    research_report: dict
    
    # Content Generation Results
    blog_content: str
    linkedin_content: str
    image_url: str
    image_prompt: str
    formatted_content: str
    image_base64: str
    image_object: str
    
    # Final Output
    final_content: str
    content_type: str
    metadata: dict
    
    # State Management
    messages: Annotated[list, operator.add]
    error: str


def prepare_initial_state(query: str, content_type: str, user_profile: dict = None, session_id: str = None) -> dict:
    """Prepare initial state with proper field mapping"""
    
    # Default values
    fallback_tone = os.getenv("DEFAULT_TONE", "professional")
    fallback_target_words = int(os.getenv("DEFAULT_TARGET_WORDS", "1200"))
    
    # Initialize base state
    state = {
        "user_query": query,
        "messages": [],
        "requested_content_type": content_type,
        "session_id": session_id,
        "override": False,  # Default to False
        "tone": fallback_tone,
        "target_words": fallback_target_words,
        "keywords": "",
        "target_audience": "general",
        "enable_seo": True,
        "image_provider": "stable-diffusion",
        "image_size": "1024x1024",
        "image_quality": "standard",
        "max_results": 10,
        "user_profile": user_profile or {}
    }
    
    # If user_profile exists, extract and map fields
    if user_profile:
        # Extract override flag FIRST
        state["override"] = bool(user_profile.get("override", False))
        
        print(f"[DEBUG] Override extracted from user_profile: {state['override']}")
        
        # Map ALL UI fields to both ui_* and main keys
        ui_field_mapping = {
            "ui_tone": ("tone", str),
            "ui_keywords": ("keywords", str),
            "ui_target_words": ("target_words", int),
            "ui_target_audience": ("target_audience", str),
            "ui_topic": ("topic", str),
            "ui_key_findings": ("key_findings", list),
            "ui_research_summary": ("research_summary", str),
            "ui_sources": ("sources", list),
            "ui_user_query": ("user_query", str),
            "ui_image_size": ("image_size", str),
            "ui_image_quality": ("image_quality", str),
            "ui_image_provider": ("image_provider", str),
            "ui_max_results": ("max_results", int),
            "ui_key_points": ("key_points", list),
            "ui_enable_seo": ("enable_seo", bool)
        }
        
        for ui_key, (main_key, expected_type) in ui_field_mapping.items():
            if ui_key in user_profile:
                value = user_profile[ui_key]
                # Type validation
                try:
                    if expected_type == int and not isinstance(value, int):
                        value = int(value) if value else 0
                    elif expected_type == bool:
                        value = bool(value)
                    elif expected_type == list and not isinstance(value, list):
                        value = [value] if value else []
                    elif expected_type == str and not isinstance(value, str):
                        value = str(value) if value else ""
                    
                    # Set both ui_* and main key
                    state[ui_key] = value
                    state[main_key] = value
                    print(f"[DEBUG] Mapped {ui_key} -> {main_key}: {value}")
                except (ValueError, TypeError) as e:
                    print(f"[WARNING] Failed to map {ui_key}: {e}")
    
    print(f"[DEBUG] Final prepared state keys: {list(state.keys())}")
    print(f"[DEBUG] Override in final state: {state.get('override')}")
    print(f"[DEBUG] Image provider in final state: {state.get('image_provider')}")
    
    return state


def create_content_workflow():
    """Create LangGraph workflow for content generation with LangSmith tracing enabled"""

    # Verify LangSmith environment variable usage
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY", getattr(settings, "langsmith_api_key", None))
    if not langsmith_api_key:
        print("[WARNING] LANGSMITH_API_KEY is not set. Tracing may not work.")

    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens
    )

    # Initialize agents
    query_handler = QueryHandlerAgent(llm)
    research_agent = DeepResearchAgent(llm, settings.serp_api_key)
    blog_writer = SEOBlogWriterAgent(llm)
    linkedin_writer = LinkedInPostAgent(llm)
    content_strategist = ContentStrategistAgent(llm)

    def image_node(state):
        """Image generation node with proper provider handling"""
        print(f"[DEBUG] [Image Node] Full state keys: {list(state.keys())}")
        print(f"[DEBUG] [Image Node] Override: {state.get('override', None)}")
        print(f"[DEBUG] [Image Node] Image provider from state: {state.get('image_provider')}")
        print(f"[DEBUG] [Image Node] UI Image provider from state: {state.get('ui_image_provider')}")
        
        # Get provider with proper fallback chain
        provider = (
            state.get("image_provider") or 
            state.get("ui_image_provider") or 
            "stable-diffusion"
        )
        
        print(f"[DEBUG] [Image Node] Using provider: {provider}")
        
        # Create agent and call it
        agent = ImageGeneratorAgent(
            provider=provider,
            llm=llm,
            openai_api_key=settings.openai_api_key,
            hf_api_key=settings.hf_api_key
        )
        
        result = agent(state)
        print(f"[DEBUG] [Image Node] Result: {result}")
        return result

    # Router function with improved logging
    def route_content(state: ContentState) -> str:
        """Route to appropriate content generation node"""
        print(f"[DEBUG] [Router] Full state keys: {list(state.keys())}")
        print(f"[DEBUG] [Router] Override: {state.get('override', False)}")
        
        override = state.get("override", False)
        requested_type = state.get("requested_content_type")
        
        print(f"[DEBUG] [Router] Requested type: {requested_type}")
        
        # If override is enabled, use requested_content_type directly
        if override and requested_type:
            print(f"[DEBUG] [Router] Override enabled, routing to: {requested_type}")
            return requested_type
        
        # If explicit content type is requested
        if requested_type:
            print(f"[DEBUG] [Router] Routing to requested type: {requested_type}")
            return requested_type
        
        # Fallback to query analysis
        intent = state.get("query_analysis", {}).get("intent", "research")
        print(f"[DEBUG] [Router] Routing based on intent: {intent}")
        return intent

    # Create workflow
    workflow = StateGraph(ContentState)

    # Add nodes with logging wrapper
    def log_wrapper(agent, name):
        def wrapped(state):
            print(f"[DEBUG] [{name}] Input state keys: {list(state.keys())}")
            result = agent(state)
            print(f"[DEBUG] [{name}] Output: {result}")
            return result
        return wrapped

    workflow.add_node("analyze_query", log_wrapper(query_handler, "analyze_query"))
    workflow.add_node("research", log_wrapper(research_agent, "research"))
    workflow.add_node("blog", log_wrapper(blog_writer, "blog"))
    workflow.add_node("linkedin", log_wrapper(linkedin_writer, "linkedin"))
    workflow.add_node("image", log_wrapper(image_node, "image"))
    workflow.add_node("strategy", log_wrapper(content_strategist, "strategy"))

    # Set entry point
    workflow.set_entry_point("analyze_query")

    # Add conditional routing after query analysis
    workflow.add_conditional_edges(
        "analyze_query",
        route_content,
        {
            "research": "research",
            "blog": "blog",
            "linkedin": "linkedin",
            "image": "image",
            "strategy": "strategy"
        }
    )

    # Research can lead to other content types
    workflow.add_conditional_edges(
        "research",
        lambda state: state.get("requested_content_type", "strategy"),
        {
            "blog": "blog",
            "linkedin": "linkedin",
            "strategy": "strategy",
            "image": "image",
            "research": END
        }
    )

    # All content types lead to END
    workflow.add_edge("blog", END)
    workflow.add_edge("linkedin", END)
    workflow.add_edge("image", END)
    workflow.add_edge("strategy", END)

    return workflow.compile()


def generate_content(query: str, content_type: str, user_profile: dict = None, session_id: str = None):
    """Generate content from user query"""
    
    # Prepare initial state with proper mapping
    initial_state = prepare_initial_state(query, content_type, user_profile, session_id)
    
    print("[DEBUG] ========== Starting Content Generation ==========")
    print(f"[DEBUG] Query: {query}")
    print(f"[DEBUG] Content Type: {content_type}")
    print(f"[DEBUG] Override: {initial_state.get('override')}")
    print(f"[DEBUG] Image Provider: {initial_state.get('image_provider')}")
    
    # Create and run workflow
    workflow = create_content_workflow()
    
    try:
        print("[DEBUG] Invoking workflow...")
        result = workflow.invoke(initial_state)
        
        # Extract final content based on content type
        content_type_result = result.get("content_type", content_type)
        
        if content_type_result == "blog":
            final_content = result.get("blog_content", "")
        elif content_type_result == "linkedin":
            final_content = result.get("linkedin_content", "")
        elif content_type_result == "image":
            final_content = result.get("image_url", "")
        elif content_type_result == "research":
            final_content = result.get("research_summary", "")
        else:
            final_content = result.get("formatted_content", "")
        
        result["final_content"] = final_content
        
        # Calculate word count
        if isinstance(final_content, str):
            result["word_count"] = len(final_content.split())
        else:
            result["word_count"] = 0
        
        print("[DEBUG] ========== Content Generation Complete ==========")
        return result
        
    except Exception as e:
        print(f"[ERROR] Content generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "error": str(e),
            "final_content": "Error generating content. Please try again.",
            "content_type": "error",
            "word_count": 0
        }
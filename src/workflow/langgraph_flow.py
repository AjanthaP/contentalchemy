from typing import TypedDict, Annotated, Literal
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

class ContentState(TypedDict):
    """State for content generation workflow"""
    # Input
    user_query: str
    override: bool  # Ensure override is always present
    requested_content_type: str
    user_profile: dict
    session_id: str
    tone: str
    target_words: int
    keywords: str
    target_audience: str
    topic: str
    key_findings: list[str]
    research_summary: str
    sources: list[str]
    enable_seo: bool
    max_results: int
    key_points: list[str]
    image_provider: str
    image_size: str
    image_quality: str

    # Query Analysis
    query_analysis: dict
    intent: str
    topic: str
    keywords: list[str]
    requires_research: bool
    
    # Research
    research_report: dict
    research_summary: str
    key_findings: list[str]
    
    # Content Generation
    blog_content: str
    linkedin_content: str
    image_url: str
    image_prompt: str
    formatted_content: str
    
    # Output
    final_content: str
    content_type: str
    metadata: dict
    
    # State management
    messages: Annotated[list, operator.add]
    error: str

def create_content_workflow():
    """Create LangGraph workflow for content generation with LangSmith tracing enabled"""

    # Verify LangSmith environment variable usage
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY", getattr(settings, "langsmith_api_key", None))
    langsmith_project = os.getenv("LANGSMITH_PROJECT", "ContentBlitz")
    if not langsmith_api_key:
        raise EnvironmentError("LANGSMITH_API_KEY is not set. Please add your LangSmith PAT to the environment.")

    # Initialize LLM with LangSmith tracing (remove unsupported 'project' argument)
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
        print(f"[DEBUG] [Image Node] State override: {state.get('override', None)}")
        provider = state.get("image_provider") or state.get("ui_image_provider") or "stable-diffusion"
        print(f"[Image Node] Using provider: {provider}")
        agent = ImageGeneratorAgent(provider, llm, settings.openai_api_key, settings.hf_api_key)
        return agent(state)

    # Router function
    def route_content(state: ContentState) -> str:
        print("[DEBUG] [Router] State:", state)
        override = state.get("override", False)
        print(f"[DEBUG] [Router] override: {override}")
        if override:
            requested_type = state.get("requested_content_type")
            print(f"[DEBUG] [Router] Override enabled, requested_content_type: {requested_type}")
            return requested_type if requested_type else "analyze_query"

        requested_type = state.get("requested_content_type")
        if requested_type:
            print(f"[DEBUG] [Router] requested_content_type: {requested_type}")
            return requested_type

        user_query = state.get("user_query", "").lower()
        for keyword in ["research", "blog", "linkedin", "image", "strategy"]:
            if keyword in user_query:
                print(f"[DEBUG] [Router] keyword match: {keyword}")
                return keyword

        print("[DEBUG] [Router] fallback to requested_content_type or 'research'")
        return state.get("requested_content_type", "research")

    # Create workflow
    workflow = StateGraph(ContentState)

    # Add nodes with logging after execution
    def log_wrapper(agent, name):
        def wrapped(state):
            result = agent(state)
            print(f"[Agent Output] {name}:", result)
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
            "analyze_query": "analyze_query",  # If override, stay in query_handler
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
        lambda state: state.get("query_analysis", {}).get("intent", "strategy"),
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
    workflow = create_content_workflow()
    
    # Fallbacks for tone and target_words
    fallback_tone = os.getenv("DEFAULT_TONE", "professional")
    fallback_target_words = int(os.getenv("DEFAULT_TARGET_WORDS", "1200"))

    # Always set user_profile as a dict
    if user_profile is None:
        user_profile = {}
    initial_state = {
        "user_query": query,
        "messages": [],
        "requested_content_type": content_type,
        "user_profile": user_profile,
        "session_id": session_id,
        "tone": fallback_tone,
        "target_words": fallback_target_words
    }
    print("[DEBUG] Initial state before UI mapping:", initial_state)
    # Always set override from user_profile or directly from payload
    initial_state["override"] = bool(user_profile.get("override", False))
    print(f"[DEBUG] After setting override: {initial_state['override']}")
    # Map UI fields to both ui_* and main keys for workflow compatibility
    ui_to_main = {
        "ui_tone": "tone",
        "ui_keywords": "keywords",
        "ui_target_words": "target_words",
        "ui_target_audience": "target_audience",
        "ui_topic": "topic",
        "ui_key_findings": "key_findings",
        "ui_research_summary": "research_summary",
        "ui_sources": "sources",
        "ui_user_query": "user_query",
        "ui_image_size": "image_size",
        "ui_image_quality": "image_quality",
        "ui_image_provider": "image_provider",
        "ui_max_results": "max_results",
        "ui_key_points": "key_points",
        "ui_enable_seo": "enable_seo"
    }
    for ui_key, main_key in ui_to_main.items():
        if ui_key in user_profile:
            initial_state[ui_key] = user_profile[ui_key]
            initial_state[main_key] = user_profile[ui_key]
    print("[DEBUG] Initial state after UI mapping:", initial_state)
    try:
        print("[DEBUG] State before workflow.invoke:", initial_state)
        result = workflow.invoke(initial_state)
        content_type = result.get("content_type", "research")
        if content_type == "blog":
            final_content = result.get("blog_content", "")
        elif content_type == "linkedin":
            final_content = result.get("linkedin_content", "")
        elif content_type == "image":
            final_content = result.get("image_url", "")
        elif content_type == "research":
            final_content = result.get("research_summary", "")
        else:
            final_content = result.get("formatted_content", "")
        result["final_content"] = final_content
        # Restore word count meter
        if isinstance(final_content, str):
            result["word_count"] = len(final_content.split())
        else:
            result["word_count"] = 0
        return result
    except Exception as e:
        return {
            "error": str(e),
            "final_content": "Error generating content. Please try again.",
            "content_type": "error"
        }

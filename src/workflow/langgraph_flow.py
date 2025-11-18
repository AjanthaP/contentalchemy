from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import operator

from src.agents.query_handler import QueryHandlerAgent
from src.agents.research_agent import DeepResearchAgent
from src.agents.blog_writer import SEOBlogWriterAgent
from src.agents.linkedin_writer import LinkedInPostAgent
from src.agents.image_generator import ImageGeneratorAgent
from src.agents.content_strategist import ContentStrategistAgent
from src.core.config import settings

class ContentState(TypedDict):
    """State for content generation workflow"""
    # Input
    user_query: str
    
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
    """Create LangGraph workflow for content generation"""
    
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
    image_generator = ImageGeneratorAgent(llm, settings.openai_api_key)
    content_strategist = ContentStrategistAgent(llm)
    
    # Router function
    def route_content(state: ContentState) -> str:
        """Route to appropriate content generation agent"""
        intent = state.get("intent", "research")
        requires_research = state.get("requires_research", False)
        
        # If research needed and not done yet, do research first
        if requires_research and not state.get("research_summary"):
            return "research"
        
        # Route based on intent
        if intent == "blog":
            return "blog"
        elif intent == "linkedin":
            return "linkedin"
        elif intent == "image":
            return "image"
        elif intent == "strategy":
            return "strategy"
        else:
            return "research"
    
    # Create workflow
    workflow = StateGraph(ContentState)
    
    # Add nodes
    workflow.add_node("analyze_query", query_handler)
    workflow.add_node("research", research_agent)
    workflow.add_node("blog", blog_writer)
    workflow.add_node("linkedin", linkedin_writer)
    workflow.add_node("image", image_generator)
    workflow.add_node("strategy", content_strategist)
    
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
        lambda state: state.get("query_analysis", {}).get("intent", "strategy"),
        {
            "blog": "blog",
            "linkedin": "linkedin",
            "strategy": "strategy",
            "research": END
        }
    )
    
    # All content types lead to END
    workflow.add_edge("blog", END)
    workflow.add_edge("linkedin", END)
    workflow.add_edge("image", END)
    workflow.add_edge("strategy", END)
    
    return workflow.compile()

def generate_content(user_query: str, **kwargs) -> dict:
    """Generate content from user query"""
    workflow = create_content_workflow()
    
    initial_state = {
        "user_query": user_query,
        "messages": [],
        **kwargs
    }
    
    try:
        result = workflow.invoke(initial_state)
        
        # Extract final content based on type
        content_type = result.get("content_type", "research")
        if content_type == "blog":
            final_content = result.get("blog_content", "")
        elif content_type == "linkedin":
            final_content = result.get("linkedin_content", "")
        elif content_type == "image":
            final_content = result.get("image_url", "")
        else:
            final_content = result.get("formatted_content", "")
        
        result["final_content"] = final_content
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "final_content": "Error generating content. Please try again.",
            "content_type": "error"
        }

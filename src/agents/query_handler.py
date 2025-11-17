from typing import Dict, Any, Literal
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json

ContentIntent = Literal["research", "blog", "linkedin", "image", "strategy"]

class QueryAnalysis(BaseModel):
    """Structured output from query handler"""
    intent: ContentIntent = Field(description="Primary content intent")
    topic: str = Field(description="Main topic or subject")
    keywords: list[str] = Field(description="Key search terms or keywords")
    target_audience: str = Field(default="general", description="Target audience")
    tone: str = Field(default="professional", description="Desired tone")
    additional_requirements: Dict[str, Any] = Field(default_factory=dict)
    requires_research: bool = Field(default=False, description="Whether research is needed first")

class QueryHandlerAgent:
    """Routes user queries to appropriate specialized agents"""
    
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
        You are an expert content marketing strategist analyzing user requests.
        
        User Query: {query}
        
        Analyze this request and determine:
        1. Primary Intent (choose ONE):
           - "research": User wants web research on a topic
           - "blog": User wants an SEO-optimized blog post
           - "linkedin": User wants a LinkedIn post
           - "image": User wants an AI-generated image
           - "strategy": User wants content organized from research
        
        2. Extract:
           - Main topic/subject
           - Key keywords (3-5 relevant terms)
           - Target audience (who will read this)
           - Desired tone (professional, casual, technical, etc.)
           - Any special requirements
        
        3. Determine if research is needed BEFORE creating content
        
        Return your analysis as a JSON object with these fields:
        {{
          "intent": "blog|research|linkedin|image|strategy",
          "topic": "clear topic statement",
          "keywords": ["keyword1", "keyword2", ...],
          "target_audience": "audience description",
          "tone": "tone description",
          "additional_requirements": {{}},
          "requires_research": true|false
        }}
        
        Be precise. Return ONLY valid JSON.
        """)
    
    def analyze(self, query: str) -> QueryAnalysis:
        """Analyze user query and route to appropriate agent"""
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"query": query})
            
            # Extract JSON from response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            parsed_data = json.loads(content.strip())
            return QueryAnalysis(**parsed_data)
            
        except Exception as e:
            print(f"Error analyzing query: {e}")
            # Fallback: simple keyword detection
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str) -> QueryAnalysis:
        """Fallback analysis using simple keyword matching"""
        query_lower = query.lower()
        
        # Detect intent
        if any(word in query_lower for word in ["research", "find", "search", "investigate"]):
            intent = "research"
        elif any(word in query_lower for word in ["blog", "article", "post", "write"]):
            intent = "blog"
        elif any(word in query_lower for word in ["linkedin", "social", "professional network"]):
            intent = "linkedin"
        elif any(word in query_lower for word in ["image", "picture", "visual", "graphic"]):
            intent = "image"
        else:
            intent = "research"  # Default
        
        return QueryAnalysis(
            intent=intent,
            topic=query[:100],
            keywords=[word for word in query_lower.split() if len(word) > 4][:5],
            target_audience="general",
            tone="professional",
            requires_research=intent != "image"
        )
    
    def __call__(self, state: Dict) -> Dict:
        """LangGraph node function"""
        analysis = self.analyze(state["user_query"])
        return {
            "query_analysis": analysis.model_dump(),
            "intent": analysis.intent,
            "topic": analysis.topic,
            "keywords": analysis.keywords,
            "requires_research": analysis.requires_research
        }

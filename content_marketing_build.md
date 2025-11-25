# AI Content Marketing Assistant - Complete Build Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Day 1: Core Multi-Agent System](#day-1-core-multi-agent-system)
5. [Day 2: Content Enhancement](#day-2-content-enhancement)
6. [Day 3: UI & Integration](#day-3-ui--integration)
7. [Testing & Deployment](#testing--deployment)
8. [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

**Goal:** Build a production-ready multi-agent content marketing assistant that generates research reports, SEO blogs, LinkedIn posts, and images.

**Key Features:**
- 6 specialized AI agents with distinct roles
- LangGraph workflow orchestration
- Multi-format content generation
- SEO optimization engine
- Image generation with DALL-E 3
- Web research capabilities
- Streamlit web interface
- Conversation memory system

**Tech Stack:**
- **LLM:** OpenAI GPT-4 (alternatives: Claude Sonnet, Google Gemini)
- **Framework:** LangChain + LangGraph
- **Research:** SERP API (alternatives: Perplexity Sonar, Tavily)
- **Images:** DALL-E 3 (alternatives: Stability AI, Midjourney)
- **UI:** Streamlit
- **Memory:** JSON files / Redis (optional)
- **Python:** 3.10+

---

## 🏗️ System Architecture

### Agent Roles:

1. **Query Handler Agent**: Routes user requests to appropriate specialized agents
2. **Deep Research Agent**: Conducts comprehensive web research using SERP API
3. **SEO Blog Writer Agent**: Creates search-optimized long-form content (1000-2000 words)
4. **LinkedIn Post Writer Agent**: Generates engaging professional social content
5. **Image Generation Agent**: Produces custom visuals with prompt optimization
6. **Content Strategist Agent**: Formats and organizes research into readable content

### Data Flow:
```
User Input → Query Handler → [Route to Agent] → Content Generation → Quality Enhancement → Output
                                    ↓
                          Research/Image/Blog/LinkedIn
                                    ↓
                            Content Optimization
                                    ↓
                            Quality Validation
```

---

## 📁 Project Structure

```
contentalchemy/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── query_handler.py      # Routes requests to specialized agents
│   │   ├── research_agent.py     # Deep web research with SERP API
│   │   ├── blog_writer.py        # SEO-optimized blog content
│   │   ├── linkedin_writer.py    # Social media content
│   │   ├── image_generator.py    # DALL-E 3 image creation
│   │   └── content_strategist.py # Research formatting
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration management
│   │   ├── router.py             # Agent routing logic
│   │   └── workflow.py           # Workflow orchestration
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── openai_client.py      # OpenAI API wrapper
│   │   ├── serp_client.py        # SERP API wrapper
│   │   ├── perplexity_client.py  # Perplexity alternative
│   │   └── image_clients.py      # Image generation clients
│   ├── optimization/
│   │   ├── __init__.py
│   │   ├── seo_optimizer.py      # SEO enhancement
│   │   ├── content_validator.py  # Quality validation
│   │   └── brand_voice.py        # Brand consistency
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── conversation_manager.py
│   │   └── user_profiles.json
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── prompts.py            # Prompt templates
│   │   ├── validators.py         # Input validation
│   │   └── export_tools.py       # Export functionality
│   ├── workflow/
│   │   ├── __init__.py
│   │   └── langgraph_flow.py     # LangGraph orchestration
│   └── web_app/
│       ├── streamlit_app.py      # Main UI
│       ├── components/
│       │   ├── chat_interface.py
│       │   ├── content_editor.py
│       │   └── dashboard.py
│       └── static/
│           └── styles.css
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_agents.py
│   │   └── test_optimization.py
│   ├── integration/
│   │   └── test_workflow.py
│   └── e2e/
│       └── test_full_pipeline.py
├── config/
│   ├── development.yaml
│   ├── production.yaml
│   └── services.yaml
├── docs/
│   ├── architecture.md
│   ├── api_documentation.md
│   └── deployment_guide.md
├── data/
│   └── templates/
│       ├── blog_templates.json
│       └── linkedin_templates.json
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── README.md
└── setup.py
```

---

## 🚀 Day 1: Core Multi-Agent System (8-10 hours)

### Hour 1-2: Project Setup

#### Step 1: Create Project Structure
```bash
# Create project directory
mkdir contentalchemy
cd contentalchemy

# Create all subdirectories
mkdir -p src/{agents,core,integrations,optimization,memory,utils,workflow,web_app/components/static}
mkdir -p tests/{unit,integration,e2e}
mkdir -p config data/templates docs

# Create __init__.py files
find src tests -type d -exec touch {}/__init__.py \;
```

#### Step 2: Set Up Virtual Environment
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

#### Step 3: Create requirements.txt
```txt
# Core AI/ML
langchain==0.1.20
langchain-openai==0.0.8
langgraph==0.0.30
openai==1.12.0

# Research & Web
requests==2.31.0
beautifulsoup4==4.12.3
serpapi==0.1.5
python-dotenv==1.0.0

# UI
streamlit==1.31.0
plotly==5.18.0

# Data Processing
pydantic==2.5.0
pydantic-settings==2.1.0
pandas==2.2.0
numpy==1.26.3

# Utilities
python-dateutil==2.8.2
pillow==10.2.0
markdown==3.5.2

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0

# Optional Performance
redis==5.0.1
aiohttp==3.9.1

# Code Quality
black==24.1.1
flake8==7.0.0
mypy==1.8.0
```

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Set Up Environment Variables
Create `.env` file:
```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# SERP API (for research)
SERP_API_KEY=your_serp_api_key_here

# Optional: Alternative Services
PERPLEXITY_API_KEY=your_perplexity_key
ANTHROPIC_API_KEY=your_claude_key

# Application Settings
APP_NAME=ContentAlchemy
DEBUG=True
LOG_LEVEL=INFO
MAX_TOKENS=4000
TEMPERATURE=0.7

# Image Generation
DALLE_MODEL=dall-e-3
DALLE_SIZE=1024x1024
DALLE_QUALITY=standard

# Content Settings
MAX_RESEARCH_RESULTS=10
BLOG_MIN_WORDS=1000
BLOG_MAX_WORDS=2000
```

Create `.env.example`:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERP_API_KEY=your_serp_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
APP_NAME=ContentAlchemy
DEBUG=True
```

#### Step 6: Create Configuration File
Create `src/core/config.py`:
```python
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

### Hour 2-4: Core Agent Implementation

#### Agent 1: Query Handler (`src/agents/query_handler.py`)
```python
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
```

#### Agent 2: Deep Research Agent (`src/agents/research_agent.py`)
```python
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import requests
import os

class ResearchResult(BaseModel):
    """Single research result"""
    title: str
    url: str
    snippet: str
    relevance_score: float = 0.0

class ResearchReport(BaseModel):
    """Comprehensive research report"""
    topic: str
    summary: str
    key_findings: List[str]
    sources: List[ResearchResult]
    insights: List[str]
    recommended_angles: List[str]

class DeepResearchAgent:
    """Conducts comprehensive web research using SERP API"""
    
    def __init__(self, llm, serp_api_key: str = None):
        self.llm = llm
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        
        self.analysis_prompt = ChatPromptTemplate.from_template("""
        You are a professional research analyst. Analyze these search results.
        
        Topic: {topic}
        Keywords: {keywords}
        
        Search Results:
        {search_results}
        
        Create a comprehensive research report with:
        1. Executive Summary (2-3 sentences)
        2. Key Findings (5-7 bullet points of the most important discoveries)
        3. Insights (3-5 analytical observations or trends)
        4. Recommended Content Angles (3-5 unique perspectives for content creation)
        
        Format as JSON:
        {{
          "summary": "executive summary",
          "key_findings": ["finding 1", "finding 2", ...],
          "insights": ["insight 1", "insight 2", ...],
          "recommended_angles": ["angle 1", "angle 2", ...]
        }}
        
        Be thorough, analytical, and actionable.
        """)
    
    def search_web(self, query: str, num_results: int = 10) -> List[ResearchResult]:
        """Perform web search using SERP API"""
        if not self.serp_api_key:
            print("Warning: No SERP API key found. Using mock data.")
            return self._mock_search_results(query)
        
        try:
            params = {
                "q": query,
                "api_key": self.serp_api_key,
                "num": num_results,
                "engine": "google"
            }
            
            response = requests.get(
                "https://serpapi.com/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic_results", [])[:num_results]:
                results.append(ResearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    relevance_score=1.0
                ))
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return self._mock_search_results(query)
    
    def _mock_search_results(self, query: str) -> List[ResearchResult]:
        """Mock search results for testing"""
        return [
            ResearchResult(
                title=f"Research on {query} - Source {i+1}",
                url=f"https://example.com/research/{i+1}",
                snippet=f"Comprehensive information about {query}. This source provides valuable insights...",
                relevance_score=0.9 - (i * 0.1)
            )
            for i in range(5)
        ]
    
    def analyze_results(self, topic: str, keywords: List[str], 
                       results: List[ResearchResult]) -> ResearchReport:
        """Analyze search results and create report"""
        try:
            # Format search results
            results_text = "\n\n".join([
                f"Title: {r.title}\nURL: {r.url}\nSnippet: {r.snippet}"
                for r in results
            ])
            
            chain = self.analysis_prompt | self.llm
            response = chain.invoke({
                "topic": topic,
                "keywords": ", ".join(keywords),
                "search_results": results_text
            })
            
            # Parse JSON response
            import json
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            analysis = json.loads(content.strip())
            
            return ResearchReport(
                topic=topic,
                summary=analysis["summary"],
                key_findings=analysis["key_findings"],
                sources=results,
                insights=analysis["insights"],
                recommended_angles=analysis["recommended_angles"]
            )
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return self._fallback_report(topic, results)
    
    def _fallback_report(self, topic: str, results: List[ResearchResult]) -> ResearchReport:
        """Fallback report if analysis fails"""
        return ResearchReport(
            topic=topic,
            summary=f"Research compiled on {topic} from {len(results)} sources.",
            key_findings=[r.snippet[:100] for r in results[:5]],
            sources=results,
            insights=[f"Insight about {topic} from research"],
            recommended_angles=[
                f"Beginner's guide to {topic}",
                f"Advanced strategies for {topic}",
                f"Common mistakes in {topic}"
            ]
        )
    
    def research(self, topic: str, keywords: List[str], 
                 num_results: int = 10) -> ResearchReport:
        """Main research method"""
        # Combine topic and keywords for search
        search_query = f"{topic} {' '.join(keywords)}"
        
        # Perform search
        results = self.search_web(search_query, num_results)
        
        # Analyze results
        report = self.analyze_results(topic, keywords, results)
        
        return report
    
    def __call__(self, state: Dict) -> Dict:
        """LangGraph node function"""
        report = self.research(
            topic=state["topic"],
            keywords=state["keywords"],
            num_results=state.get("max_results", 10)
        )
        
        return {
            "research_report": report.model_dump(),
            "research_summary": report.summary,
            "key_findings": report.key_findings
        }
```

#### Agent 3: SEO Blog Writer (`src/agents/blog_writer.py`)
```python
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel

class BlogPost(BaseModel):
    """SEO-optimized blog post"""
    title: str
    meta_description: str
    introduction: str
    body_sections: List[Dict[str, str]]  # [{heading: content}]
    conclusion: str
    seo_keywords: List[str]
    word_count: int
    internal_links_suggestions: List[str]
    cta: str

class SEOBlogWriterAgent:
    """Creates SEO-optimized blog posts"""
    
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
        You are an expert SEO content writer. Create a comprehensive, engaging blog post.
        
        Topic: {topic}
        Target Keywords: {keywords}
        Target Audience: {audience}
        Tone: {tone}
        
        Research Context:
        {research_summary}
        
        Key Points to Cover:
        {key_findings}
        
        Create a blog post (1000-2000 words) with:
        
        1. **Compelling Title** (60-70 characters, includes primary keyword)
        2. **Meta Description** (150-160 characters, compelling, includes keyword)
        3. **Introduction** (150-200 words)
           - Hook the reader
           - State the problem/topic
           - Preview what they'll learn
        
        4. **Body Sections** (5-7 sections with H2 headings)
           - Each section 200-300 words
           - Use H2 and H3 subheadings
           - Include examples, data, or case studies
           - Incorporate keywords naturally
        
        5. **Conclusion** (100-150 words)
           - Summarize key takeaways
           - Reinforce value
        
        6. **Call-to-Action (CTA)**
           - Clear next step for reader
        
        7. **SEO Elements**:
           - Primary and secondary keywords integrated naturally
           - Internal link suggestions (3-5 related topics)
           - Proper heading hierarchy
        
        Format your response as a complete blog post in markdown.
        Use proper headings (## for H2, ### for H3).
        Make it engaging, informative, and optimized for both readers and search engines.
        
        START BLOG POST:
        """)
    
    def write_blog(self, topic: str, keywords: List[str], 
                   research_summary: str, key_findings: List[str],
                   audience: str = "general", tone: str = "professional") -> str:
        """Generate SEO blog post"""
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "topic": topic,
                "keywords": ", ".join(keywords),
                "audience": audience,
                "tone": tone,
                "research_summary": research_summary,
                "key_findings": "\n- ".join(key_findings)
            })
            
            blog_content = response.content.strip()
            
            # Ensure minimum word count
            word_count = len(blog_content.split())
            if word_count < 1000:
                blog_content = self._expand_content(blog_content, topic, keywords)
            
            return blog_content
            
        except Exception as e:
            print(f"Error writing blog: {e}")
            return self._fallback_blog(topic, keywords, key_findings)
    
    def _expand_content(self, content: str, topic: str, keywords: List[str]) -> str:
        """Expand short content to meet minimum word count"""
        expansion_prompt = f"""
        This blog post about {topic} is too short. Expand it by:
        1. Adding more detailed examples
        2. Including additional subsections
        3. Providing deeper explanations
        4. Adding relevant statistics or data points
        
        Keywords to incorporate: {', '.join(keywords)}
        
        Current content:
        {content}
        
        Provide the expanded version:
        """
        
        try:
            response = self.llm.invoke(expansion_prompt)
            return response.content
        except:
            return content
    
    def _fallback_blog(self, topic: str, keywords: List[str], 
                      key_findings: List[str]) -> str:
        """Fallback blog template"""
        return f"""# The Complete Guide to {topic}

## Introduction

Understanding {topic} is essential in today's digital landscape. This comprehensive guide will walk you through everything you need to know about {', '.join(keywords[:3])}.

## What is {topic}?

{topic} represents an important concept that affects many aspects of modern business and technology.

## Key Insights

{chr(10).join([f"- {finding}" for finding in key_findings[:5]])}

## Best Practices for {topic}

When working with {topic}, it's important to follow industry best practices and stay updated with the latest trends.

### Strategy 1: Research-Driven Approach
Start with comprehensive research to understand your audience and market.

### Strategy 2: Data-Informed Decisions
Use analytics and data to guide your strategy.

### Strategy 3: Continuous Optimization
Regularly review and optimize your approach based on results.

## Common Challenges and Solutions

Many professionals face challenges when dealing with {topic}. Here are proven solutions:

1. **Challenge**: Understanding the fundamentals
   **Solution**: Start with comprehensive research and education

2. **Challenge**: Implementing effectively
   **Solution**: Follow best practices and learn from case studies

## Conclusion

Mastering {topic} requires dedication, continuous learning, and practical application. By following the strategies outlined in this guide, you'll be well-equipped to succeed.

## Next Steps

Ready to get started? Begin by implementing one strategy from this guide today.

**Keywords**: {', '.join(keywords)}
"""
    
    def __call__(self, state: Dict) -> Dict:
        """LangGraph node function"""
        blog_content = self.write_blog(
            topic=state["topic"],
            keywords=state["keywords"],
            research_summary=state.get("research_summary", ""),
            key_findings=state.get("key_findings", []),
            audience=state.get("query_analysis", {}).get("target_audience", "general"),
            tone=state.get("query_analysis", {}).get("tone", "professional")
        )
        
        return {
            "blog_content": blog_content,
            "content_type": "blog",
            "word_count": len(blog_content.split())
        }
```

---

### Hour 4-6: Image & LinkedIn Agents

#### Agent 4: LinkedIn Post Writer (`src/agents/linkedin_writer.py`)
```python
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class LinkedInPostAgent:
    """Creates engaging LinkedIn posts"""
    
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
        You are a LinkedIn content strategist creating engaging professional posts.
        
        Topic: {topic}
        Key Points: {key_points}
        Tone: {tone}
        Target Audience: {audience}
        
        Create a LinkedIn post that:
        
        1. **Hook** (First 1-2 lines): Grab attention immediately
           - Use a question, stat, or bold statement
           - Must work as a preview (first 2 lines visible)
        
        2. **Body** (Main content):
           - Tell a story or share insight
           - Use short paragraphs (1-2 sentences each)
           - Include 3-5 key points
           - Add white space for readability
           - Use emojis strategically (2-4 total)
        
        3. **Value** (What readers gain):
           - Clear takeaway or lesson
           - Actionable advice
        
        4. **Engagement** (Call-to-action):
           - Question for comments
           - Invitation to discuss
        
        5. **Hashtags** (3-5 relevant):
           - Mix of popular and niche
           - Placed at end
        
        Length: 1300-2000 characters (optimal for LinkedIn)
        
        Style Guidelines:
        - Professional but conversational
        - Use "you" to address reader
        - Short sentences (10-15 words)
        - One idea per paragraph
        - Strategic line breaks
        
        Format with proper line breaks and spacing for LinkedIn readability.
        """)
    
    def write_post(self, topic: str, key_points: List[str],
                   audience: str = "professionals", 
                   tone: str = "professional") -> str:
        """Generate LinkedIn post"""
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "topic": topic,
                "key_points": "\n- ".join(key_points),
                "tone": tone,
                "audience": audience
            })
            
            post_content = response.content.strip()
            
            # Ensure proper length (LinkedIn optimal: 1300-2000 chars)
            if len(post_content) > 3000:
                post_content = self._trim_post(post_content)
            elif len(post_content) < 500:
                post_content = self._expand_post(post_content, topic)
            
            return post_content
            
        except Exception as e:
            print(f"Error writing LinkedIn post: {e}")
            return self._fallback_post(topic, key_points)
    
    def _trim_post(self, content: str) -> str:
        """Trim post to optimal length"""
        # Keep first 2000 characters and add ellipsis if needed
        if len(content) > 2000:
            return content[:1997] + "..."
        return content
    
    def _expand_post(self, content: str, topic: str) -> str:
        """Expand short post"""
        expansion = f"\n\nWant to learn more about {topic}?\n\nShare your thoughts in the comments below! 👇"
        return content + expansion
    
    def _fallback_post(self, topic: str, key_points: List[str]) -> str:
        """Fallback post template"""
        return f"""🚀 Let's talk about {topic}

I've been exploring {topic} recently, and here's what I've discovered:

{chr(10).join([f"✓ {point}" for point in key_points[:4]])}

The key insight? Success in {topic} requires a strategic approach combined with continuous learning.

What's your experience with {topic}? 

Drop your thoughts in the comments! 💬

#ContentMarketing #DigitalStrategy #ProfessionalGrowth #{topic.replace(' ', '')}
"""
    
    def __call__(self, state: Dict) -> Dict:
        """LangGraph node function"""
        post_content = self.write_post(
            topic=state["topic"],
            key_points=state.get("key_findings", [])[:5],
            audience=state.get("query_analysis", {}).get("target_audience", "professionals"),
            tone=state.get("query_analysis", {}).get("tone", "professional")
        )
        
        return {
            "linkedin_content": post_content,
            "content_type": "linkedin",
            "char_count": len(post_content)
        }
```

#### Agent 5: Image Generator (`src/agents/image_generator.py`)
```python
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
import os

class ImageGeneratorAgent:
    """Generates images using DALL-E 3 with prompt optimization"""
    
    def __init__(self, llm, openai_api_key: str = None):
        self.llm = llm
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)
        
        self.prompt_optimizer = ChatPromptTemplate.from_template("""
        You are a DALL-E 3 prompt engineering expert.
        
        User Request: {user_request}
        Context: {context}
        
        Create an optimized DALL-E 3 prompt that:
        
        1. **Style & Medium**: Specify artistic style (e.g., "digital art", "photorealistic", "minimalist illustration")
        2. **Subject**: Clear description of main subject
        3. **Details**: Important visual elements, colors, composition
        4. **Mood/Atmosphere**: Tone and feeling
        5. **Technical**: Lighting, perspective, quality markers
        
        Best Practices:
        - Be specific but not overly restrictive
        - Use descriptive adjectives
        - Specify composition (e.g., "centered", "wide angle")
        - Include lighting details (e.g., "soft natural lighting")
        - Avoid text/words in images (DALL-E struggles with text)
        - Keep under 400 characters
        
        Example good prompt:
        "A modern minimalist office workspace, clean white desk with laptop, green plants, natural sunlight streaming through large windows, professional and inspiring atmosphere, digital illustration style, high quality"
        
        Return ONLY the optimized prompt, nothing else.
        """)
    
    def optimize_prompt(self, user_request: str, context: str = "") -> str:
        """Optimize user prompt for DALL-E 3"""
        try:
            chain = self.prompt_optimizer | self.llm
            response = chain.invoke({
                "user_request": user_request,
                "context": context
            })
            
            optimized = response.content.strip()
            
            # Ensure reasonable length
            if len(optimized) > 400:
                optimized = optimized[:397] + "..."
            
            return optimized
            
        except Exception as e:
            print(f"Error optimizing prompt: {e}")
            return user_request[:400]
    
    def generate_image(self, prompt: str, size: str = "1024x1024", 
                      quality: str = "standard") -> Dict[str, str]:
        """Generate image using DALL-E 3"""
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            return {
                "url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt,
                "status": "success"
            }
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return {
                "url": "",
                "revised_prompt": prompt,
                "status": "error",
                "error": str(e)
            }
    
    def create_image(self, user_request: str, context: str = "",
                    size: str = "1024x1024", quality: str = "standard") -> Dict:
        """Main method: optimize prompt and generate image"""
        # Optimize prompt
        optimized_prompt = self.optimize_prompt(user_request, context)
        
        # Generate image
        result = self.generate_image(optimized_prompt, size, quality)
        result["original_request"] = user_request
        result["optimized_prompt"] = optimized_prompt
        
        return result
    
    def __call__(self, state: Dict) -> Dict:
        """LangGraph node function"""
        user_request = state.get("user_query", "")
        context = state.get("topic", "")
        
        result = self.create_image(
            user_request=user_request,
            context=context,
            size=state.get("image_size", "1024x1024"),
            quality=state.get("image_quality", "standard")
        )
        
        return {
            "image_url": result.get("url", ""),
            "image_prompt": result.get("optimized_prompt", ""),
            "image_status": result.get("status", "error"),
            "content_type": "image"
        }
```

#### Agent 6: Content Strategist (`src/agents/content_strategist.py`)
```python
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class ContentStrategistAgent:
    """Formats and organizes research into readable content"""
    
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
        You are a content strategist organizing research into a clear, actionable report.
        
        Topic: {topic}
        
        Research Summary:
        {research_summary}
        
        Key Findings:
        {key_findings}
        
        Sources:
        {sources}
        
        Create a well-structured research report with:
        
        1. **Executive Summary** (2-3 paragraphs)
           - Overview of topic
           - Why it matters
           - Key takeaways
        
        2. **Main Findings** (organized by theme)
           - Group related findings
           - Use clear subheadings
           - Support with source citations
        
        3. **Analysis & Insights**
           - Patterns or trends
           - Implications
           - Opportunities
        
        4. **Recommendations**
           - Actionable next steps
           - Content opportunities
           - Strategic angles
        
        5. **Sources**
           - List all sources with links
           - Organized by relevance
        
        Format in markdown with proper headings, bullet points, and emphasis.
        Make it professional, scannable, and actionable.
        """)
    
    def format_research(self, topic: str, research_summary: str,
                       key_findings: List[str], sources: List[Dict]) -> str:
        """Format research into structured report"""
        try:
            # Format sources
            sources_text = "\n".join([
                f"- {s.get('title', 'Unknown')}: {s.get('url', 'N/A')}"
                for s in sources[:10]
            ])
            
            chain = self.prompt | self.llm
            response = chain.invoke({
                "topic": topic,
                "research_summary": research_summary,
                "key_findings": "\n- ".join(key_findings),
                "sources": sources_text
            })
            
            return response.content.strip()
            
        except Exception as e:
            print(f"Error formatting research: {e}")
            return self._fallback_report(topic, research_summary, key_findings, sources)
    
    def _fallback_report(self, topic: str, summary: str, 
                        findings: List[str], sources: List[Dict]) -> str:
        """Fallback report template"""
        sources_list = "\n".join([
            f"- [{s.get('title', 'Source')}]({s.get('url', '#')})"
            for s in sources[:10]
        ])
        
        return f"""# Research Report: {topic}

## Executive Summary

{summary}

## Key Findings

{chr(10).join([f"- {finding}" for finding in findings])}

## Recommendations

Based on this research, consider the following content opportunities:

1. Create educational content addressing the main findings
2. Develop case studies demonstrating practical applications
3. Share insights with your target audience through multiple channels

## Sources

{sources_list}

---
*Report generated on {self._get_timestamp()}*
"""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __call__(self, state: Dict) -> Dict:
        """LangGraph node function"""
        formatted_report = self.format_research(
            topic=state["topic"],
            research_summary=state.get("research_summary", ""),
            key_findings=state.get("key_findings", []),
            sources=state.get("research_report", {}).get("sources", [])
        )
        
        return {
            "formatted_content": formatted_report,
            "content_type": "research_report"
        }
```

---

### Hour 6-8: LangGraph Workflow

Create `src/workflow/langgraph_flow.py`:
```python
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
```

---

## 🎨 Day 2: Content Enhancement (8-10 hours)

### Hour 1-3: SEO Optimization System

Create `src/optimization/seo_optimizer.py`:
```python
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import re

class SEOOptimizer:
    """Optimizes content for search engines"""
    
    def __init__(self, llm):
        self.llm = llm
        self.analysis_prompt = ChatPromptTemplate.from_template("""
        You are an SEO expert analyzing content.
        
        Content: {content}
        Target Keywords: {keywords}
        
        Analyze and provide:
        
        1. **Keyword Usage**:
           - Primary keyword frequency
           - Secondary keyword usage
           - Keyword placement (title, headings, first paragraph)
        
        2. **Content Structure**:
           - Heading hierarchy (H1, H2, H3)
           - Paragraph length
           - Readability score estimate
        
        3. **SEO Score** (0-100):
           - Overall optimization score
        
        4. **Improvements** (specific, actionable):
           - 3-5 concrete recommendations
        
        Format as JSON:
        {{
          "keyword_density": {{"primary": 0.02, "secondary": 0.01}},
          "structure_score": 85,
          "readability_score": 70,
          "seo_score": 78,
          "improvements": ["improvement 1", "improvement 2", ...]
        }}
        """)
    
    def analyze_content(self, content: str, keywords: List[str]) -> Dict:
        """Analyze content for SEO"""
        try:
            chain = self.analysis_prompt | self.llm
            response = chain.invoke({
                "content": content[:3000],  # Limit for analysis
                "keywords": ", ".join(keywords)
            })
            
            import json
            content_text = response.content
            if "```json" in content_text:
                content_text = content_text.split("```json")[1].split("```")[0]
            
            return json.loads(content_text.strip())
            
        except Exception as e:
            print(f"Error analyzing SEO: {e}")
            return self._basic_analysis(content, keywords)
    
    def _basic_analysis(self, content: str, keywords: List[str]) -> Dict:
        """Basic SEO analysis without LLM"""
        word_count = len(content.split())
        primary_keyword = keywords[0] if keywords else ""
        
        # Count keyword occurrences
        keyword_count = content.lower().count(primary_keyword.lower())
        keyword_density = keyword_count / word_count if word_count > 0 else 0
        
        # Count headings
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
        
        # Basic scoring
        structure_score = min(100, (h2_count * 15) + (h3_count * 5))
        seo_score = 50 if keyword_density > 0.01 else 30
        
        return {
            "keyword_density": {"primary": keyword_density},
            "structure_score": structure_score,
            "readability_score": 60,
            "seo_score": seo_score,
            "improvements": [
                f"Add more instances of '{primary_keyword}' if density is low",
                "Include keyword in first paragraph",
                "Use keyword in at least one H2 heading"
            ]
        }
    
    def optimize_content(self, content: str, keywords: List[str]) -> str:
        """Optimize content based on analysis"""
        analysis = self.analyze_content(content, keywords)
        
        if analysis.get("seo_score", 0) >= 75:
            return content  # Already well-optimized
        
        # Create optimization prompt
        optimization_prompt = f"""
        Optimize this content for SEO without changing the core message:
        
        Content: {content}
        
        Target Keywords: {', '.join(keywords)}
        
        Current Issues:
        {chr(10).join([f"- {imp}" for imp in analysis.get("improvements", [])])}
        
        Improve by:
        1. Adding target keywords naturally (aim for 1-2% density)
        2. Including keywords in headings where appropriate
        3. Ensuring keyword appears in first 100 words
        4. Maintaining readability and natural flow
        
        Return the optimized content:
        """
        
        try:
            response = self.llm.invoke(optimization_prompt)
            return response.content
        except:
            return content
    
    def generate_meta_tags(self, content: str, keywords: List[str]) -> Dict[str, str]:
        """Generate meta title and description"""
        prompt = f"""
        Create SEO meta tags for this content:
        
        Content Summary: {content[:500]}
        Keywords: {', '.join(keywords)}
        
        Generate:
        1. Meta Title (50-60 characters, includes primary keyword)
        2. Meta Description (150-160 characters, compelling, includes keyword)
        
        Format as JSON:
        {{
          "title": "Your meta title here",
          "description": "Your meta description here"
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            import json
            content_text = response.content
            if "```json" in content_text:
                content_text = content_text.split("```json")[1].split("```")[0]
            return json.loads(content_text.strip())
        except:
            return {
                "title": keywords[0] if keywords else "Article",
                "description": content[:160]
            }
```

Create `src/optimization/content_validator.py`:
```python
from typing import Dict, List
from pydantic import BaseModel

class ValidationResult(BaseModel):
    """Content validation result"""
    is_valid: bool
    score: int  # 0-100
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]

class ContentValidator:
    """Validates content quality"""
    
    def __init__(self):
        self.min_word_count = {
            "blog": 800,
            "linkedin": 100,
            "research": 500
        }
        
        self.max_word_count = {
            "blog": 3000,
            "linkedin": 600,
            "research": 5000
        }
    
    def validate_content(self, content: str, content_type: str = "blog") -> ValidationResult:
        """Validate content quality"""
        issues = []
        warnings = []
        suggestions = []
        score = 100
        
        # Word count validation
        word_count = len(content.split())
        min_words = self.min_word_count.get(content_type, 500)
        max_words = self.max_word_count.get(content_type, 3000)
        
        if word_count < min_words:
            issues.append(f"Content too short: {word_count} words (minimum: {min_words})")
            score -= 20
        elif word_count > max_words:
            warnings.append(f"Content quite long: {word_count} words (recommended max: {max_words})")
            score -= 5
        
        # Structure validation
        if content_type == "blog":
            if not self._has_headings(content):
                issues.append("Missing heading structure (H2/H3)")
                score -= 15
            
            if not self._has_introduction(content):
                warnings.append("Consider adding a clear introduction")
                score -= 5
        
        # Readability checks
        avg_sentence_length = self._avg_sentence_length(content)
        if avg_sentence_length > 25:
            suggestions.append("Consider shorter sentences for better readability")
            score -= 5
        
        # Paragraph length
        if self._has_long_paragraphs(content):
            suggestions.append("Break up long paragraphs for better scannability")
            score -= 5
        
        is_valid = len(issues) == 0 and score >= 60
        
        return ValidationResult(
            is_valid=is_valid,
            score=max(0, score),
            issues=issues,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _has_headings(self, content: str) -> bool:
        """Check if content has proper headings"""
        import re
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        return h2_count >= 2
    
    def _has_introduction(self, content: str) -> bool:
        """Check if content has introduction"""
        lines = content.split('\n')
        first_paragraph = '\n'.join(lines[:5])
        return len(first_paragraph.split()) >= 50
    
    def _avg_sentence_length(self, content: str) -> float:
        """Calculate average sentence length"""
        sentences = content.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 0
        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)
    
    def _has_long_paragraphs(self, content: str) -> bool:
        """Check for paragraphs longer than 150 words"""
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para.split()) > 150:
                return True
        return False
```

---

### Hour 3-5: Memory & Brand Voice System

Create `src/memory/conversation_manager.py`:
```python
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from pathlib import Path

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, storage_path: str = "data/conversations"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_session = []
        
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to current session"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.current_session.append(message)
    
    def get_context(self, max_messages: int = 10) -> List[Dict]:
        """Get recent conversation context"""
        return self.current_session[-max_messages:]
    
    def save_session(self, session_id: str):
        """Save conversation session"""
        filepath = self.storage_path / f"{session_id}.json"
        with open(filepath, 'w') as f:
            json.dump({
                "session_id": session_id,
                "messages": self.current_session,
                "created_at": datetime.now().isoformat()
            }, f, indent=2)
    
    def load_session(self, session_id: str) -> List[Dict]:
        """Load conversation session"""
        filepath = self.storage_path / f"{session_id}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get("messages", [])
        return []
    
    def clear_session(self):
        """Clear current session"""
        self.current_session = []

class UserProfileManager:
    """Manages user profiles and preferences"""
    
    def __init__(self, profile_path: str = "src/memory/user_profiles.json"):
        self.profile_path = profile_path
        self.profiles = self._load_profiles()
    
    def _load_profiles(self) -> Dict:
        """Load user profiles"""
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_profiles(self):
        """Save user profiles"""
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    def get_profile(self, user_id: str = "default") -> Dict:
        """Get user profile"""
        return self.profiles.get(user_id, self._create_default_profile())
    
    def _create_default_profile(self) -> Dict:
        """Create default profile"""
        return {
            "user_id": "default",
            "preferences": {
                "tone": "professional",
                "content_length": "medium",
                "include_sources": True,
                "seo_optimization": True
            },
            "brand_voice": {
                "style": "professional and informative",
                "vocabulary": "industry-standard",
                "avoid": []
            },
            "content_history": [],
            "learned_preferences": {}
        }
    
    def update_profile(self, user_id: str, updates: Dict):
        """Update user profile"""
        if user_id not in self.profiles:
            self.profiles[user_id] = self._create_default_profile()
        
        profile = self.profiles[user_id]
        for key, value in updates.items():
            if key in profile:
                if isinstance(profile[key], dict) and isinstance(value, dict):
                    profile[key].update(value)
                else:
                    profile[key] = value
        
        self._save_profiles()
    
    def learn_from_edits(self, user_id: str, original: str, edited: str):
        """Learn from user edits"""
        profile = self.get_profile(user_id)
        
        # Analyze differences
        changes = self._analyze_changes(original, edited)
        
        # Update learned preferences
        if "learned_preferences" not in profile:
            profile["learned_preferences"] = {}
        
        for change_type, change_data in changes.items():
            if change_type not in profile["learned_preferences"]:
                profile["learned_preferences"][change_type] = []
            profile["learned_preferences"][change_type].append(change_data)
        
        self.profiles[user_id] = profile
        self._save_profiles()
    
    def _analyze_changes(self, original: str, edited: str) -> Dict:
        """Analyze what changed between original and edited"""
        changes = {}
        
        # Simple analysis: word count, tone indicators
        orig_words = len(original.split())
        edit_words = len(edited.split())
        
        if abs(orig_words - edit_words) > 50:
            changes["length_preference"] = {
                "original_words": orig_words,
                "edited_words": edit_words,
                "change": "shorter" if edit_words < orig_words else "longer"
            }
        
        # Check for tone changes (simple heuristic)
        formal_words = ["furthermore", "however", "therefore", "consequently"]
        casual_words = ["anyway", "basically", "pretty much", "kind of"]
        
        orig_formal = sum(1 for word in formal_words if word in original.lower())
        edit_formal = sum(1 for word in formal_words if word in edited.lower())
        
        if edit_formal < orig_formal:
            changes["tone_preference"] = "more casual"
        elif edit_formal > orig_formal:
            changes["tone_preference"] = "more formal"
        
        return changes
```

Create `src/optimization/brand_voice.py`:
```python
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class BrandVoiceManager:
    """Maintains brand voice consistency"""
    
    def __init__(self, llm):
        self.llm = llm
        self.consistency_prompt = ChatPromptTemplate.from_template("""
        You are a brand voice specialist ensuring content consistency.
        
        Brand Voice Guidelines:
        - Style: {style}
        - Tone: {tone}
        - Vocabulary: {vocabulary}
        - Words to Avoid: {avoid_words}
        - Example Phrases: {example_phrases}
        
        Original Content:
        {content}
        
        Rewrite the content to match the brand voice exactly while:
        1. Preserving all key information and facts
        2. Maintaining the same structure and length
        3. Applying the specified tone and style
        4. Using appropriate vocabulary
        5. Avoiding prohibited words/phrases
        
        Return only the rewritten content.
        """)
    
    def apply_brand_voice(self, content: str, brand_profile: Dict) -> str:
        """Apply brand voice to content"""
        try:
            chain = self.consistency_prompt | self.llm
            response = chain.invoke({
                "style": brand_profile.get("style", "professional"),
                "tone": brand_profile.get("tone", "informative"),
                "vocabulary": brand_profile.get("vocabulary", "standard"),
                "avoid_words": ", ".join(brand_profile.get("avoid", [])),
                "example_phrases": ", ".join(brand_profile.get("examples", [])),
                "content": content
            })
            
            return response.content.strip()
            
        except Exception as e:
            print(f"Error applying brand voice: {e}")
            return content
    
    def extract_voice_from_samples(self, samples: List[str]) -> Dict:
        """Extract brand voice characteristics from sample content"""
        combined_samples = "\n\n---\n\n".join(samples[:3])
        
        analysis_prompt = f"""
        Analyze these content samples to extract brand voice characteristics:
        
        {combined_samples}
        
        Identify:
        1. Writing Style (formal/casual/technical/conversational)
        2. Tone (professional/friendly/authoritative/empathetic)
        3. Vocabulary Level (simple/standard/advanced/technical)
        4. Common Patterns (sentence structure, phrases, formatting)
        5. Unique Characteristics
        
        Format as JSON:
        {{
          "style": "description",
          "tone": "description",
          "vocabulary": "level",
          "patterns": ["pattern1", "pattern2"],
          "characteristics": ["char1", "char2"],
          "example_phrases": ["phrase1", "phrase2"]
        }}
        """
        
        try:
            response = self.llm.invoke(analysis_prompt)
            import json
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            return json.loads(content.strip())
        except:
            return {
                "style": "professional",
                "tone": "informative",
                "vocabulary": "standard",
                "patterns": [],
                "characteristics": []
            }
```

---

## 🖥️ Day 3: UI & Integration (8-10 hours)

### Hour 1-4: Streamlit Web Application

Create `src/web_app/streamlit_app.py`:
```python
import streamlit as st
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.workflow.langgraph_flow import generate_content
from src.memory.conversation_manager import ConversationManager, UserProfileManager
from src.optimization.seo_optimizer import SEOOptimizer
from src.optimization.content_validator import ContentValidator
from langchain_openai import ChatOpenAI
from src.core.config import settings

# Page config
st.set_page_config(
    page_title="ContentAlchemy - AI Content Marketing",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation_manager' not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()
    st.session_state.profile_manager = UserProfileManager()
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">✨ ContentAlchemy</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Content Marketing Assistant</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Content type selector
    content_type_display = st.selectbox(
        "What do you want to create?",
        [
            "🔍 Research Report",
            "📝 SEO Blog Post",
            "💼 LinkedIn Post",
            "🎨 AI-Generated Image",
            "📊 Content Strategy"
        ]
    )
    
    # Map display names to intents
    content_type_map = {
        "🔍 Research Report": "research",
        "📝 SEO Blog Post": "blog",
        "💼 LinkedIn Post": "linkedin",
        "🎨 AI-Generated Image": "image",
        "📊 Content Strategy": "strategy"
    }
    
    st.divider()
    
    # Advanced settings
    with st.expander("🎯 Advanced Settings"):
        user_tone = st.select_slider(
            "Content Tone",
            options=["Casual", "Conversational", "Professional", "Formal", "Technical"],
            value="Professional"
        )
        
        enable_seo = st.checkbox("Enable SEO Optimization", value=True)
        include_sources = st.checkbox("Include Source Citations", value=True)
        
        if content_type_display == "📝 SEO Blog Post":
            target_words = st.slider(
                "Target Word Count",
                min_value=800,
                max_value=2500,
                value=1500,
                step=100
            )
        
        if content_type_display == "🎨 AI-Generated Image":
            image_size = st.select_slider(
                "Image Size",
                options=["1024x1024", "1024x1792", "1792x1024"],
                value="1024x1024"
            )
            image_quality = st.radio("Image Quality", ["standard", "hd"], index=0)
    
    st.divider()
    
    # Profile management
    st.subheader("👤 Profile")
    user_id = st.text_input("User ID", value="default")
    
    if st.button("💾 Save Current Settings"):
        profile_updates = {
            "preferences": {
                "tone": user_tone.lower(),
                "seo_optimization": enable_seo,
                "include_sources": include_sources
            }
        }
        st.session_state.profile_manager.update_profile(user_id, profile_updates)
        st.success("Settings saved!")

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📝 Content Request")
    
    # Main input
    user_query = st.text_area(
        "Describe what you want to create:",
        placeholder="""Examples:
        
• Research the latest trends in AI marketing for 2024
• Write an SEO blog post about sustainable fashion
• Create a LinkedIn post about my company's new product launch
• Generate an image of a futuristic workspace with AI elements
• Develop a content strategy for promoting a SaaS product""",
        height=150,
        key="main_query"
    )
    
    # Additional context
    with st.expander("➕ Additional Context (Optional)"):
        target_audience = st.text_input(
            "Target Audience",
            placeholder="e.g., Marketing professionals, Tech startups, B2B companies"
        )
        
        keywords = st.text_input(
            "Target Keywords (comma-separated)",
            placeholder="e.g., AI marketing, automation, ROI"
        )
        
        additional_notes = st.text_area(
            "Additional Requirements",
            placeholder="Any specific requirements, constraints, or preferences...",
            height=80
        )
    
    # Generate button
    generate_clicked = st.button(
        "✨ Generate Content",
        type="primary",
        use_container_width=True
    )

with col2:
    st.header("💡 Tips & Examples")
    
    tips_tab, examples_tab = st.tabs(["Tips", "Examples"])
    
    with tips_tab:
        st.markdown("""
        **For Best Results:**
        
        📌 **Be Specific**
        - Include your topic, target audience, and purpose
        - Mention any key points you want covered
        
        🎯 **Set Context**
        - Describe your industry or niche
        - Specify content goals (educate, promote, inspire)
        
        🔍 **Research-Based Content**
        - Let the AI research first for factual accuracy
        - Review sources and adjust as needed
        
        ✏️ **Iterate & Refine**
        - Edit the generated content
        - The system learns from your edits
        """)
    
    with examples_tab:
        st.markdown("""
        **Research Report:**
        "Research emerging AI tools for content marketing in 2024"
        
        **Blog Post:**
        "Write an SEO blog about email marketing automation for small businesses"
        
        **LinkedIn Post:**
        "Create a LinkedIn post announcing our company's sustainability initiative"
        
        **Image:**
        "Generate a professional header image for a tech blog about cloud computing"
        """)

# Content Generation
if generate_clicked:
    if not user_query.strip():
        st.error("⚠️ Please enter a content request")
    else:
        with st.spinner("🤖 Creating your content..."):
            try:
                # Enhance query with additional context
                enhanced_query = user_query
                if target_audience:
                    enhanced_query += f"\n\nTarget Audience: {target_audience}"
                if keywords:
                    enhanced_query += f"\n\nKeywords: {keywords}"
                if additional_notes:
                    enhanced_query += f"\n\nAdditional Notes: {additional_notes}"
                
                # Add to conversation
                st.session_state.conversation_manager.add_message(
                    "user",
                    enhanced_query,
                    {"content_type": content_type_map[content_type_display]}
                )
                
                # Generate content
                result = generate_content(
                    user_query=enhanced_query,
                    image_size=image_size if content_type_display == "🎨 AI-Generated Image" else "1024x1024",
                    image_quality=image_quality if content_type_display == "🎨 AI-Generated Image" else "standard"
                )
                
                # Store result
                st.session_state.last_result = result
                st.session_state.last_query = user_query
                
                # Add to conversation
                st.session_state.conversation_manager.add_message(
                    "assistant",
                    result.get("final_content", ""),
                    {"result": result}
                )
                
                st.success("✅ Content generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Check your API keys in the .env file")

# Display Results
if 'last_result' in st.session_state:
    st.divider()
    st.header("📄 Generated Content")
    
    result = st.session_state.last_result
    content_type = result.get("content_type", "unknown")
    
    # Metadata display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Content Type", content_type.replace("_", " ").title())
    with col2:
        if content_type in ["blog", "research_report"]:
            word_count = result.get("word_count", len(result.get("final_content", "").split()))
            st.metric("Word Count", f"{word_count:,}")
        elif content_type == "linkedin":
            char_count = result.get("char_count", len(result.get("final_content", "")))
            st.metric("Characters", f"{char_count:,}")
    with col3:
        st.metric("Status", "✅ Complete")
    with col4:
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.metric("Generated", timestamp)
    
    # Content tabs
    content_tab, analysis_tab, sources_tab = st.tabs(["📝 Content", "📊 Analysis", "🔗 Sources"])
    
    with content_tab:
        if content_type == "image":
            # Display image
            image_url = result.get("image_url", "")
            if image_url:
                st.image(image_url, caption="Generated Image", use_container_width=True)
                st.text_area(
                    "Image Prompt Used:",
                    value=result.get("image_prompt", ""),
                    height=100,
                    key="image_prompt_display"
                )
        else:
            # Editable text content
            edited_content = st.text_area(
                "Edit your content:",
                value=result.get("final_content", ""),
                height=500,
                key="content_editor"
            )
            
            # Track edits
            if edited_content != result.get("final_content", ""):
                st.info("💡 Content modified - changes will be saved for learning")
    
    with analysis_tab:
        if content_type in ["blog", "research_report"]:
            # Validate content
            validator = ContentValidator()
            validation = validator.validate_content(
                result.get("final_content", ""),
                content_type
            )
            
            st.subheader("Quality Score")
            st.progress(validation.score / 100)
            st.metric("Overall Score", f"{validation.score}/100")
            
            if validation.issues:
                st.error("**Issues Found:**")
                for issue in validation.issues:
                    st.write(f"• {issue}")
            
            if validation.warnings:
                st.warning("**Warnings:**")
                for warning in validation.warnings:
                    st.write(f"• {warning}")
            
            if validation.suggestions:
                st.info("**Suggestions:**")
                for suggestion in validation.suggestions:
                    st.write(f"• {suggestion}")
            
            # SEO Analysis
            if enable_seo and content_type == "blog":
                st.subheader("SEO Analysis")
                llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
                seo_optimizer = SEOOptimizer(llm)
                
                keywords_list = keywords.split(",") if keywords else ["content", "marketing"]
                seo_analysis = seo_optimizer.analyze_content(
                    result.get("final_content", ""),
                    [k.strip() for k in keywords_list]
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("SEO Score", f"{seo_analysis.get('seo_score', 0)}/100")
                with col2:
                    st.metric("Structure Score", f"{seo_analysis.get('structure_score', 0)}/100")
                
                if seo_analysis.get("improvements"):
                    st.write("**SEO Improvements:**")
                    for imp in seo_analysis["improvements"]:
                        st.write(f"• {imp}")
        else:
            st.info("Analysis available for blog posts and research reports")
    
    with sources_tab:
        research_report = result.get("research_report", {})
        sources = research_report.get("sources", [])
        
        if sources:
            st.subheader(f"📚 {len(sources)} Sources Found")
            for i, source in enumerate(sources, 1):
                with st.expander(f"{i}. {source.get('title', 'Source')}"):
                    st.write(f"**URL:** {source.get('url', 'N/A')}")
                    st.write(f"**Snippet:** {source.get('snippet', 'No description')}")
        else:
            st.info("No sources available for this content type")
    
    # Action buttons
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Download as Markdown
        st.download_button(
            "📥 Download MD",
            data=result.get("final_content", ""),
            file_name=f"content_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col2:
        # Download as TXT
        st.download_button(
            "📄 Download TXT",
            data=result.get("final_content", ""),
            file_name=f"content_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Generate New", use_container_width=True):
            del st.session_state.last_result
            st.rerun()
    
    with col4:
        if st.button("💾 Save & Learn", use_container_width=True):
            # Learn from edits if content was modified
            if 'content_editor' in st.session_state:
                original = result.get("final_content", "")
                edited = st.session_state.content_editor
                if edited != original:
                    st.session_state.profile_manager.learn_from_edits(
                        user_id,
                        original,
                        edited
                    )
            
            # Save conversation
            st.session_state.conversation_manager.save_session(st.session_state.session_id)
            st.success("✅ Saved and learned from your edits!")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Built with ❤️ using LangChain & LangGraph")
with col2:
    st.caption(f"Session: {st.session_state.session_id}")
with col3:
    st.caption("v1.0.0")
```

---

## 🧪 Testing & Deployment

### Testing Strategy

Create `tests/unit/test_agents.py`:
```python
import pytest
from src.agents.query_handler import QueryHandlerAgent
from src.agents.research_agent import DeepResearchAgent
from langchain_openai import ChatOpenAI
from src.core.config import settings

@pytest.fixture
def llm():
    return ChatOpenAI(model="gpt-3.5-turbo", api_key=settings.openai_api_key)

@pytest.fixture
def query_handler(llm):
    return QueryHandlerAgent(llm)

def test_query_handler_blog_intent(query_handler):
    """Test blog intent detection"""
    result = query_handler.analyze("Write a blog post about AI marketing")
    assert result.intent == "blog"
    assert "AI" in result.topic or "marketing" in result.topic

def test_query_handler_research_intent(query_handler):
    """Test research intent detection"""
    result = query_handler.analyze("Research the latest trends in blockchain")
    assert result.intent == "research"
    assert result.requires_research == True

def test_query_handler_image_intent(query_handler):
    """Test image intent detection"""
    result = query_handler.analyze("Create an image of a futuristic city")
    assert result.intent == "image"
    assert result.requires_research == False
```

### Deployment Checklist

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  contentalchemy:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SERP_API_KEY=${SERP_API_KEY}
    volumes:
      - ./data:/app/data
      - ./src:/app/src
    command: streamlit run src/web_app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/web_app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Running the Application

```bash
# Development mode
streamlit run src/web_app/streamlit_app.py

# Docker deployment
docker-compose up --build

# Run tests
pytest tests/ -v --cov=src
```

---

## 🚀 Future Enhancements

1. **Multi-Modal Content**
   - Video script generation
   - Podcast content creation
   - Infographic generation

2. **Advanced Integration**
   - WordPress/CMS publishing
   - Social media scheduling
   - Email campaign integration

3. **Analytics & Learning**
   - Content performance tracking
   - A/B testing suggestions
   - Advanced user preference learning

4. **Collaboration Features**
   - Team workspaces
   - Content approval workflows
   - Version control

---

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Ready to build? Start with Day 1 and create your first agent!**
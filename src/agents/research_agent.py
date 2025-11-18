from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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

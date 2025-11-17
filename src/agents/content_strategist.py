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

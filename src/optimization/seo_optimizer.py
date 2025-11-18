from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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

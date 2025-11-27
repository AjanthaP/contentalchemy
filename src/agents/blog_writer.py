from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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
        
        Create a blog post ({target_words} words) with:
        
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
                   audience: str = "general", tone: str = "professional", target_words: int = 1200) -> str:
        """Generate SEO blog post"""
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "topic": topic,
                "keywords": ", ".join(keywords),
                "audience": audience,
                "tone": tone,
                "target_words": target_words,
                "research_summary": research_summary,
                "key_findings": "\n- ".join(key_findings)
            })
            
            blog_content = response.content.strip()
            
            # Ensure minimum word count
            word_count = len(blog_content.split())
            if word_count < target_words:
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
        # Use UI values if override is selected
        if state.get("override"):
            audience = state.get("ui_target_audience", "general")
            tone = state.get("ui_tone", "professional")
            target_words = state.get("ui_target_words", 1200)
            keywords = state.get("ui_keywords", [])
        else:
            audience = state.get("query_analysis", {}).get("target_audience") or state.get("user_profile", {}).get("target_audience") or "general"
            tone = state.get("query_analysis", {}).get("tone") or state.get("tone", "professional")
            target_words = state.get("query_analysis", {}).get("target_words") or state.get("target_words", 1200)
            keywords = state.get("keywords", [])
        blog_content = self.write_blog(
            topic=state["topic"],
            keywords=keywords,
            research_summary=state.get("research_summary", ""),
            key_findings=state.get("key_findings", []),
            audience=audience,
            tone=tone,
            target_words=target_words
        )
        return {
            "blog_content": blog_content,
            "content_type": "blog",
            "word_count": len(blog_content.split())
        }

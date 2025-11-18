from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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

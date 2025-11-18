from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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

from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
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

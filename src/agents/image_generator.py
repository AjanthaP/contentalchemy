from typing import Dict, Optional, Literal
from abc import ABC, abstractmethod
import requests
import base64
from io import BytesIO
from PIL import Image
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
import os


#============================================================================
# ABSTRACT BASE CLASS FOR IMAGE GENERATORS
# ============================================================================

class ImageGeneratorBase(ABC):
    """Base class for all image generation models"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict:
        """Generate image from prompt"""
        pass
    
    @abstractmethod
    def get_cost_per_image(self) -> float:
        """Return cost per image in USD"""
        pass


# ============================================================================
# DALL-E 3 IMPLEMENTATION
# ============================================================================

class DallE3Generator(ImageGeneratorBase):
    """DALL-E 3 via OpenAI API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.openai.com/v1/images/generations"
    
    def generate(self, prompt: str, size: str = "1024x1024", 
                 quality: str = "standard", style: str = "vivid") -> Dict:
        """
        Generate image using DALL-E 3
        
        Args:
            prompt: Image description
            size: "1024x1024", "1024x1792", "1792x1024"
            quality: "standard" or "hd"
            style: "vivid" or "natural"
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "style": style
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "image_url": data["data"][0]["url"],
                "revised_prompt": data["data"][0].get("revised_prompt", prompt),
                "model": "dall-e-3",
                "cost": self.get_cost_per_image()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": "dall-e-3"
            }
    
    def get_cost_per_image(self) -> float:
        """DALL-E 3 pricing (as of 2024)"""
        return 0.040  # $0.040 per standard 1024x1024 image


# ============================================================================
# HUGGING FACE IMPLEMENTATIONS
# ============================================================================

class StableDiffusionGenerator(ImageGeneratorBase):
    """Stable Diffusion via Hugging Face Inference API"""
    
    def __init__(self, api_key: str, model: str = "black-forest-labs/FLUX.1-schnell"):
        self.api_key = api_key
        self.model = model
        self.endpoint = f"https://router.huggingface.co/hf-inference/models/{model}"
    
    def generate(self, prompt: str, negative_prompt: str = "", 
                 num_inference_steps: int = 50, guidance_scale: float = 7.5) -> Dict:
        """
        Generate image using Stable Diffusion
        
        Args:
            prompt: Image description
            negative_prompt: What to avoid
            num_inference_steps: Quality vs speed (20-100)
            guidance_scale: Prompt adherence (1-20)
        """

        print("StableDiffusionGenerator API Key:", self.api_key)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale
            }
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            # HF returns raw image bytes
            image_bytes = response.content
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to base64 for easy handling
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "success": True,
                "image_base64": img_str,
                "image_object": image,
                "prompt": prompt,
                "model": self.model,
                "cost": self.get_cost_per_image()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }
    
    def get_cost_per_image(self) -> float:
        """HF Inference API is FREE for basic usage!"""
        return 0.0  # Free tier available


class ImageGeneratorAgent:
    """Generates images using DALL-E 3 with prompt optimization"""
     
    SUPPORTED_MODELS = {
        "dalle3": DallE3Generator,
        "stable-diffusion": StableDiffusionGenerator,
    }

    def __init__(self, provider:Literal["dalle3", "stable-diffusion"] = "dalle3", llm=None, openai_api_key: str = None, hf_api_key: str = None):
        self.provider = provider

        # Initialize the selected generator
        if provider == "dalle3":
            if not openai_api_key:
                raise ValueError("OpenAI API key required for DALL-E 3")
            self.generator = DallE3Generator(openai_api_key)
        
        elif provider in ["stable-diffusion"]:
            if not hf_api_key:
                raise ValueError("Hugging Face API key required")
            self.generator = StableDiffusionGenerator(hf_api_key)

        self.llm = llm
        # self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        # self.client = OpenAI(api_key=self.openai_api_key)
        
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
    
    def generate_image(self, prompt: str, **kwargs) -> Dict[str, str]:
        """Generate image using DALL-E 3"""
        # try:
        #     response = self.client.images.generate(
        #         model="dall-e-3",
        #         prompt=prompt,
        #         size=size,
        #         quality=quality,
        #         n=1
        #     )

        #     image_data = response.data[0]
        #     image_url = getattr(image_data, "url", None)
        #     if not image_url:
        #         b64_json = getattr(image_data, "b64_json", "")
        #         if b64_json:
        #             image_url = f"data:image/png;base64,{b64_json}"
            
        #     return {
        #         "url": image_url or "",
        #         "revised_prompt": getattr(image_data, "revised_prompt", prompt),
        #         "status": "success"
        #     }
            
        # except Exception as e:
        #     print(f"Error generating image: {e}")
        #     return {
        #         "url": "",
        #         "revised_prompt": prompt,
        #         "status": "error",
        #         "error": str(e)
        #     }
        return self.generator.generate(prompt, **kwargs)
    
    def create_image(self, user_request: str, context: str = "",
                    size: str = "1024x1024", quality: str = "standard") -> Dict:
        """Main method: optimize prompt and generate image"""
        optimized_prompt = self.optimize_prompt(user_request, context)
        if self.provider == "dalle3":
            result = self.generate_image(optimized_prompt, size=size, quality=quality)
        elif self.provider == "stable-diffusion":
            result = self.generate_image(optimized_prompt)
        else:
            result = self.generate_image(optimized_prompt)
        result["original_request"] = user_request
        result["optimized_prompt"] = optimized_prompt
        return result
    
    def __call__(self, state: Dict) -> Dict:
        """LangGraph node function"""
        # Use UI values if override is selected
        print(f"ImageGeneratorAgent called with state: {state}")
        print(f"ImageGeneratorAgent called provider: {self.provider}")
        
        if state.get("override"):
            user_request = state.get("ui_user_query", "")
            context = state.get("ui_topic", "")
            size = state.get("ui_image_size", "1024x1024")
            quality = state.get("ui_image_quality", "standard")
        else:
            user_request = state.get("user_query", "")
            context = state.get("topic", "")
            size = state.get("image_size", "1024x1024")
            quality = state.get("image_quality", "standard")
        result = self.create_image(
            user_request=user_request,
            context=context,
            size=size,
            quality=quality
        )
        # return {
        #     "image_url": result.get("url", ""),
        #     "image_prompt": result.get("optimized_prompt", ""),
        #     "image_status": result.get("status", "error"),
        #     "content_type": "image"
        # }

        return result
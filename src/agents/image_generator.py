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
    def get_cost_per_image(self) -> Optional[float]:
        """Return cost per image in USD"""
        pass


# ============================================================================
# OpenAI image generation
# ============================================================================

class OpenAIImageGenerator(ImageGeneratorBase):
    """Generate images using OpenAI's Images API."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.openai.com/v1/images/generations"
    
    def generate(self, prompt: str, size: str = "1024x1024",
                 quality: str = "standard", **kwargs) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": {"standard": "medium", "hd": "high"}.get(quality, quality)
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            image_data = data["data"][0]
            
            return {
                "success": True,
                "image_url": image_data.get("url"),
                "image_base64": image_data.get("b64_json"),
                "revised_prompt": image_data.get("revised_prompt", prompt),
                "model": self.model
            }
        except requests.HTTPError as e:
            response_text = e.response.text if e.response is not None else str(e)
            status_code = e.response.status_code if e.response is not None else "unknown"
            return {
                "success": False,
                "error": f"OpenAI image API returned HTTP {status_code}: {response_text}",
                "model": self.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }
    
    def get_cost_per_image(self) -> Optional[float]:
        return None


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
                "revised_prompt": prompt,
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
    """Generates images using OpenAI image models with prompt optimization."""
     
    SUPPORTED_MODELS = {
        "dalle3": OpenAIImageGenerator,
        "stable-diffusion": StableDiffusionGenerator,
    }

    def __init__(self, provider:Literal["dalle3", "stable-diffusion"] = "dalle3", llm=None, openai_api_key: str = None, hf_api_key: str = None, openai_image_model: str = "gpt-image-2.5-flare"):
        self.provider = provider

        # Initialize the selected generator
        if provider == "dalle3":
            if not openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI image generation")
            self.generator = OpenAIImageGenerator(openai_api_key, openai_image_model)
        
        elif provider in ["stable-diffusion"]:
            if not hf_api_key:
                raise ValueError("Hugging Face API key required")
            self.generator = StableDiffusionGenerator(hf_api_key)

        self.llm = llm
        # self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        # self.client = OpenAI(api_key=self.openai_api_key)
        
        self.prompt_optimizer = ChatPromptTemplate.from_template("""
        You are an OpenAI image prompt engineering expert.
        
        User Request: {user_request}
        Context: {context}
        
        Create an optimized prompt for OpenAI image generation that:
        
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
        - Avoid unnecessary text in images
        - Keep under 400 characters
        
        Example good prompt:
        "A modern minimalist office workspace, clean white desk with laptop, green plants, natural sunlight streaming through large windows, professional and inspiring atmosphere, digital illustration style, high quality"
        
        Return ONLY the optimized prompt, nothing else.
        """)
    
    def optimize_prompt(self, user_request: str, context: str = "") -> str:
        """Optimize user prompt for OpenAI image generation"""
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
        """Generate image using OpenAI's Images API."""
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
from typing import Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from diffusers import StableDiffusionPipeline
import torch
from io import BytesIO
import base64
import os

class ImageGeneratorAgent:
    """Generates images using Stable Diffusion with prompt optimization"""
    
    def __init__(self, llm, model_id: str = "stabilityai/stable-diffusion-2-1"):
        self.llm = llm
        self.model_id = model_id
        self.pipe = None
        
        self.prompt_optimizer = ChatPromptTemplate.from_template("""
        You are a Stable Diffusion prompt engineering expert.
        
        User Request: {user_request}
        Context: {context}
        
        Create an optimized Stable Diffusion prompt that:
        
        1. **Style & Medium**: Specify artistic style (e.g., "digital art", "photorealistic", "oil painting")
        2. **Subject**: Clear description of main subject
        3. **Details**: Important visual elements, colors, composition
        4. **Mood/Atmosphere**: Tone and feeling
        5. **Technical**: Lighting, perspective, quality markers (e.g., "highly detailed", "8k", "sharp focus")
        
        Best Practices for Stable Diffusion:
        - Be descriptive and specific
        - Use quality boosters: "masterpiece", "best quality", "highly detailed"
        - Specify composition: "centered", "rule of thirds", "close-up"
        - Include lighting: "soft lighting", "dramatic shadows", "golden hour"
        - Add style keywords: "trending on artstation", "unreal engine"
        - Keep focused and clear
        
        Also create a NEGATIVE prompt to avoid unwanted elements:
        - Common negatives: "blurry, low quality, distorted, ugly, deformed, watermark, text"
        
        Return in this format:
        PROMPT: [your optimized positive prompt]
        NEGATIVE: [your negative prompt]
        """)
    
    def load_model(self):
        """Load Stable Diffusion model (lazy loading)"""
        if self.pipe is None:
            print(f"Loading Stable Diffusion model: {self.model_id}...")
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                safety_checker=None  # Remove if you want content filtering
            )
            
            # Use GPU if available
            if torch.cuda.is_available():
                self.pipe = self.pipe.to("cuda")
                print("Model loaded on GPU")
            else:
                self.pipe = self.pipe.to("cpu")
                print("Warning: Model loaded on CPU (will be slow)")
            
            # Memory optimizations for low VRAM
            if torch.cuda.is_available():
                self.pipe.enable_attention_slicing()
                
        return self.pipe
    
    def optimize_prompt(self, user_request: str, context: str = "") -> Dict[str, str]:
        """Optimize user prompt for Stable Diffusion"""
        try:
            chain = self.prompt_optimizer | self.llm
            response = chain.invoke({
                "user_request": user_request,
                "context": context
            })
            
            content = response.content.strip()
            
            # Parse prompt and negative prompt
            positive_prompt = ""
            negative_prompt = "blurry, low quality, distorted, ugly, deformed, watermark, text, duplicate, morbid, mutilated"
            
            if "PROMPT:" in content and "NEGATIVE:" in content:
                parts = content.split("NEGATIVE:")
                positive_prompt = parts[0].replace("PROMPT:", "").strip()
                negative_prompt = parts[1].strip()
            else:
                positive_prompt = content
            
            return {
                "prompt": positive_prompt,
                "negative_prompt": negative_prompt
            }
            
        except Exception as e:
            print(f"Error optimizing prompt: {e}")
            return {
                "prompt": user_request,
                "negative_prompt": "blurry, low quality, distorted"
            }
    
    def generate_image(self, prompt: str, negative_prompt: str = "",
                      width: int = 1024, height: int = 1024,
                      steps: int = 50, guidance_scale: float = 7.5) -> Dict[str, str]:
        """Generate image using Stable Diffusion"""
        try:
            # Load model if not already loaded
            pipe = self.load_model()
            
            # Generate image
            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                height=height,
                width=width
            ).images[0]
            
            # Convert to base64 (similar to DALL-E format)
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            image_url = f"data:image/png;base64,{img_base64}"
            
            return {
                "url": image_url,
                "revised_prompt": prompt,
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
        # Parse size
        try:
            width, height = map(int, size.split("x"))
        except:
            width, height = 1024, 1024
        
        # Map quality to steps (standard = 30, hd = 50)
        steps = 50 if quality == "hd" else 30
        
        # Optimize prompt
        optimized = self.optimize_prompt(user_request, context)
        
        # Generate image
        result = self.generate_image(
            prompt=optimized["prompt"],
            negative_prompt=optimized["negative_prompt"],
            width=width,
            height=height,
            steps=steps
        )
        
        result["original_request"] = user_request
        result["optimized_prompt"] = optimized["prompt"]
        result["negative_prompt"] = optimized["negative_prompt"]
        
        return result
    
    def __call__(self, state: Dict) -> Dict:
        """LangGraph node function"""
        # Use UI values if override is selected
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
        
        return {
            "image_url": result.get("url", ""),
            "image_prompt": result.get("optimized_prompt", ""),
            "image_status": result.get("status", "error"),
            "content_type": "image"
        }

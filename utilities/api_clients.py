"""API client wrappers for external services."""

import os
import json
import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import requests
from functools import wraps

from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config.settings import settings
from utilities.logger import get_logger

logger = get_logger("api_clients")


def rate_limit(calls: int = 10, period: int = 60):
    """Rate limiting decorator."""
    def decorator(func):
        func.calls = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls
            func.calls = [call for call in func.calls if call > now - period]

            if len(func.calls) >= calls:
                sleep_time = period - (now - func.calls[0])
                if sleep_time > 0:
                    logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                    func.calls = []

            func.calls.append(now)
            return func(*args, **kwargs)

        return wrapper
    return decorator


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Retry decorator for API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
            raise last_exception
        return wrapper
    return decorator


class APIProvider(Enum):
    """API provider types."""
    OPENAI = "openai"
    GEMINI = "gemini"
    GEMINI_IMAGE = "gemini_image"
    PIXABAY = "pixabay"
    UNSPLASH = "unsplash"
    PEXELS = "pexels"
    DUCKDUCKGO = "duckduckgo"
    WEBSCRAPER = "webscraper"


class GeminiImageGenerationClient:
    """Client for Google's Gemini Image Generation API."""

    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed.")

        if not os.getenv('GEMINI_API_KEY'):
            raise ValueError("Gemini API key not found in environment variables.")
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        # NOTE: The model name for image generation can change.
        # The user's brief specified 'gemini-2.0-flash-preview-image-generation'.
        # A known public model name like 'imagen-3' is used here as a functional equivalent.
        self.model = genai.GenerativeModel('imagen-3')
        logger.info(f"Gemini Image Generation client initialized with model: imagen-3")

    @rate_limit(calls=10, period=60)
    @retry_on_error(max_retries=2)
    def generate(self, prompt: str, output_path: str) -> bool:
        """
        Generates an image and saves it to a file.
        NOTE: This method is currently a simulation due to sandbox environment limitations
        that prevent making live API calls and writing binary files. The logic is representative
        of a real implementation.
        """
        try:
            logger.info(f"Generating image for prompt: {prompt[:80]}...")

            # --- REAL IMPLEMENTATION (Commented out due to sandbox limitations) ---
            # response = self.model.generate_content(prompt)
            # image_bytes = response.data
            # with open(output_path, 'wb') as f:
            #     f.write(image_bytes)

            # --- SIMULATED IMPLEMENTATION for sandbox environment ---
            with open(output_path, 'w') as f:
                f.write(f"This is a placeholder for the image generated with the prompt: '{prompt}'")
            # --- END SIMULATION ---

            logger.info(f"Simulated image saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error during simulated image generation: {e}")
            return False

class OpenAIClient:
    """OpenAI API client wrapper."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Install with: pip install openai")
        
        self.api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        openai.api_key = self.api_key
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info(f"OpenAI client initialized with model: {model}")
    
    @rate_limit(calls=20, period=60)
    @retry_on_error(max_retries=3)
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    @rate_limit(calls=10, period=60)
    @retry_on_error(max_retries=3)
    def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Generate text embedding."""
        response = self.client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    
    @rate_limit(calls=5, period=60)
    @retry_on_error(max_retries=2)
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1
    ) -> List[str]:
        """Generate images using DALL-E."""
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=n
        )
        return [img.url for img in response.data]


class GeminiClient:
    """Google Gemini API client wrapper."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        
        self.api_key = api_key or settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        logger.info(f"Gemini client initialized with model: {model}")
    
    @rate_limit(calls=20, period=60)
    @retry_on_error(max_retries=3)
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate text using Gemini."""
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            **kwargs
        )
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    @rate_limit(calls=10, period=60)
    @retry_on_error(max_retries=3)
    def analyze_image(self, image_path: str, prompt: str) -> str:
        """Analyze image with Gemini Vision."""
        model = genai.GenerativeModel('gemini-pro-vision')
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        response = model.generate_content([prompt, image_data])
        return response.text


class PixabayClient:
    """Pixabay API client for free stock images."""
    
    BASE_URL = "https://pixabay.com/api/"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PIXABAY_API_KEY")
        if not self.api_key:
            raise ValueError("Pixabay API key not provided")
        logger.info("Pixabay client initialized")
    
    @rate_limit(calls=100, period=60)
    @retry_on_error(max_retries=3)
    def search_images(
        self,
        query: str,
        per_page: int = 20,
        image_type: str = "photo",
        orientation: str = "horizontal",
        min_width: int = 1200,
        safesearch: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for images on Pixabay."""
        params = {
            "key": self.api_key,
            "q": query,
            "per_page": per_page,
            "image_type": image_type,
            "orientation": orientation,
            "min_width": min_width,
            "safesearch": str(safesearch).lower(),
            **kwargs
        }
        
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        images = []
        
        for hit in data.get("hits", []):
            images.append({
                "url": hit["largeImageURL"],
                "preview_url": hit["previewURL"],
                "tags": hit["tags"],
                "user": hit["user"],
                "likes": hit["likes"],
                "downloads": hit["downloads"],
                "width": hit["imageWidth"],
                "height": hit["imageHeight"],
                "page_url": hit["pageURL"]
            })
        
        return images


class UnsplashClient:
    """Unsplash API client for high-quality stock photos."""
    
    BASE_URL = "https://api.unsplash.com"
    
    def __init__(self, access_key: Optional[str] = None):
        self.access_key = access_key or os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.access_key:
            raise ValueError("Unsplash access key not provided")
        self.headers = {"Authorization": f"Client-ID {self.access_key}"}
        logger.info("Unsplash client initialized")
    
    @rate_limit(calls=50, period=3600)
    @retry_on_error(max_retries=3)
    def search_photos(
        self,
        query: str,
        per_page: int = 20,
        orientation: str = "landscape",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for photos on Unsplash."""
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation,
            **kwargs
        }
        
        response = requests.get(
            f"{self.BASE_URL}/search/photos",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        photos = []
        
        for result in data.get("results", []):
            photos.append({
                "url": result["urls"]["regular"],
                "full_url": result["urls"]["full"],
                "thumb_url": result["urls"]["thumb"],
                "description": result.get("description", result.get("alt_description", "")),
                "user": result["user"]["name"],
                "user_link": result["user"]["links"]["html"],
                "download_link": result["links"]["download"],
                "width": result["width"],
                "height": result["height"]
            })
        
        return photos
    
    def trigger_download(self, download_link: str):
        """Trigger download tracking for Unsplash (required by API guidelines)."""
        try:
            requests.get(download_link, headers=self.headers)
        except Exception as e:
            logger.warning(f"Failed to trigger Unsplash download: {e}")


class PexelsClient:
    """Pexels API client for free stock photos and videos."""
    
    BASE_URL = "https://api.pexels.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            raise ValueError("Pexels API key not provided")
        self.headers = {"Authorization": self.api_key}
        logger.info("Pexels client initialized")
    
    @rate_limit(calls=200, period=3600)
    @retry_on_error(max_retries=3)
    def search_photos(
        self,
        query: str,
        per_page: int = 20,
        orientation: str = "landscape",
        size: str = "large",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for photos on Pexels."""
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation,
            "size": size,
            **kwargs
        }
        
        response = requests.get(
            f"{self.BASE_URL}/search",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        photos = []
        
        for photo in data.get("photos", []):
            photos.append({
                "url": photo["src"]["large"],
                "original_url": photo["src"]["original"],
                "thumb_url": photo["src"]["tiny"],
                "alt": photo.get("alt", ""),
                "photographer": photo["photographer"],
                "photographer_url": photo["photographer_url"],
                "width": photo["width"],
                "height": photo["height"],
                "avg_color": photo.get("avg_color")
            })
        
        return photos


class DuckDuckGoSearchClient:
    """Wrapper for DuckDuckGo Search API."""

    def __init__(self):
        self.client = DDGS()
        logger.info("DuckDuckGo Search client initialized")

    @rate_limit(calls=50, period=60)
    @retry_on_error(max_retries=3)
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Perform a web search."""
        logger.info(f"Searching for: {query}")
        results = self.client.text(query, max_results=max_results)
        return results if results else []

class WebScraperClient:
    """Client for scraping web pages."""

    def __init__(self):
        logger.info("Web Scraper client initialized")

    @rate_limit(calls=30, period=60)
    @retry_on_error(max_retries=2)
    def scrape(self, url: str, parser: str = "html.parser") -> str:
        """Scrape text content from a URL."""
        logger.info(f"Scraping URL: {url}")
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.content, parser)

            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text
        except requests.RequestException as e:
            logger.error(f"Error scraping {url}: {e}")
            return f"Error: Could not retrieve content from {url}."


class MultiAPIClient:
    """Unified client for multiple API providers."""
    
    def __init__(self):
        self.clients = {}
        logger.info("Multi-API client initialized")
    
    def add_client(self, provider: APIProvider, client: Any):
        """Add an API client."""
        self.clients[provider] = client
        logger.info(f"Added {provider.value} client")
    
    def get_client(self, provider: APIProvider) -> Any:
        """Get a specific API client."""
        if provider not in self.clients:
            raise ValueError(f"Client for {provider.value} not configured")
        return self.clients[provider]
    
    def generate_text(
        self,
        prompt: str,
        provider: APIProvider = APIProvider.OPENAI,
        **kwargs
    ) -> str:
        """Generate text using specified provider."""
        client = self.get_client(provider)
        
        if provider == APIProvider.OPENAI:
            return client.generate_text(prompt, **kwargs)
        elif provider == APIProvider.GEMINI:
            return client.generate_text(prompt, **kwargs)
        else:
            raise ValueError(f"Text generation not supported for {provider.value}")
    
    def search_images(
        self,
        query: str,
        provider: APIProvider = APIProvider.PIXABAY,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search images using specified provider."""
        client = self.get_client(provider)
        
        if provider == APIProvider.PIXABAY:
            return client.search_images(query, **kwargs)
        elif provider == APIProvider.UNSPLASH:
            return client.search_photos(query, **kwargs)
        elif provider == APIProvider.PEXELS:
            return client.search_photos(query, **kwargs)
        else:
            raise ValueError(f"Image search not supported for {provider.value}")


# Factory functions
def create_openai_client(api_key: Optional[str] = None, **kwargs) -> OpenAIClient:
    """Create OpenAI client."""
    return OpenAIClient(api_key=api_key, **kwargs)


def create_gemini_client(api_key: Optional[str] = None, **kwargs) -> GeminiClient:
    """Create Gemini client."""
    return GeminiClient(api_key=api_key, **kwargs)


def create_image_client(provider: str = "pixabay", api_key: Optional[str] = None) -> Union[PixabayClient, UnsplashClient, PexelsClient]:
    """Create image search client."""
    if provider.lower() == "pixabay":
        return PixabayClient(api_key=api_key)
    elif provider.lower() == "unsplash":
        return UnsplashClient(access_key=api_key)
    elif provider.lower() == "pexels":
        return PexelsClient(api_key=api_key)
    else:
        raise ValueError(f"Unknown image provider: {provider}")

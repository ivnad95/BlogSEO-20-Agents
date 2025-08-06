"""
Base Agent Class with Gemini API Integration via LangChain
===========================================================
Professional base class for all agents using Google Gemini for advanced AI capabilities.
"""

import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
import json

class BaseAgent:
    """Base class for all agents using Google Gemini API."""
    
    # Subclasses should override this to specify the text model they need, per the brief.
    model_name: str = "gemini-1.5-flash-latest"

    def __init__(self):
        """Initialize the agent with the specified Gemini text model."""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if self.gemini_api_key:
            # Initialize the text-based LLM using the model specified by the subclass
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.gemini_api_key,
                temperature=0.7,
                max_output_tokens=8192,
                top_p=0.95,
                top_k=40
            )
        else:
            self.llm = None
    
    def execute_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """Execute a prompt using the configured Gemini text model.
        
        Args:
            system_prompt: System context for the AI
            user_prompt: User query
            
        Returns:
            AI response as a string
        """
        if not self.llm:
            return "Gemini API key not configured"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error executing prompt with model {self.model_name}: {str(e)}"
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, with robust error handling.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            Parsed dictionary, or a dictionary with the raw response if parsing fails.
        """
        try:
            # Attempt to find a JSON block enclosed in ```json ... ```
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            # If not, find the first '{' and last '}'
            elif "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            else:
                # If no clear JSON structure is found, return the raw response
                return {"response": response}
            
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError) as e:
            # If parsing fails, return the raw response in a dictionary
            return {"error": "Failed to parse JSON response.", "raw_response": response}
    
    def run(self, state: dict) -> dict:
        """
        Default run method. Each agent subclass must implement its own version of this method.
        
        Args:
            state: Current pipeline state dictionary
            
        Returns:
            Updated state dictionary
        """
        raise NotImplementedError("Each agent must implement its own run method")

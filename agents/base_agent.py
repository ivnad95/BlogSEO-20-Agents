"""
Base Agent Class with Gemini API Integration via LangChain
===========================================================
Professional base class for all agents using Google Gemini for advanced AI capabilities.
"""

import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import SystemMessage, HumanMessage
import json


class BaseAgent:
    """Base class for all agents using Google Gemini API."""
    
    def __init__(self):
        """Initialize the agent with Gemini API."""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if self.gemini_api_key:
            # Initialize Gemini Flash model via LangChain (fastest and most cost-effective)
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",  # Using the latest Gemini 2.0 Flash model
                google_api_key=self.gemini_api_key,
                temperature=0.7,
                max_output_tokens=8192,  # Gemini 2.0 Flash supports more tokens
                top_p=0.95,
                top_k=40
            )
        else:
            self.llm = None
    
    def execute_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """Execute a prompt using Gemini API.
        
        Args:
            system_prompt: System context for the AI
            user_prompt: User query
            
        Returns:
            AI response as string
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
            return f"Error: {str(e)}"
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed dictionary
        """
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "{" in response and "}" in response:
                # Find first { and last }
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
            else:
                json_str = response
            
            return json.loads(json_str.strip())
        except:
            # Return as dict with response if parsing fails
            return {"response": response}
    
    def run(self, state: dict) -> dict:
        """Default run method to be overridden by child classes.
        
        Args:
            state: Current pipeline state
            
        Returns:
            Agent output dictionary
        """
        raise NotImplementedError("Each agent must implement its own run method")

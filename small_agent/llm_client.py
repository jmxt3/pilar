from abc import ABC, abstractmethod
from typing import List, Any, Optional
from google.adk import Agent
from google.genai import types

class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def create_agent(self, name: str, instruction: str, tools: List[Any], config: Optional[Any] = None) -> Any:
        """Creates and returns an agent instance."""
        pass

class GeminiADKClient(LLMClient):
    """Gemini client implementation using Google ADK."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        
    def create_agent(self, name: str, instruction: str, tools: List[Any], config: Optional[types.GenerateContentConfig] = None) -> Agent:
        """Creates a Google ADK Agent."""
        return Agent(
            model=self.model_name,
            name=name,
            instruction=instruction,
            tools=tools,
            generate_content_config=config
        )

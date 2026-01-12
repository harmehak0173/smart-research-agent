"""Configuration management for the research agent."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AgentConfig:
    """Configuration settings for the research agent."""
    
    openai_api_key: str
    model: str = "gpt-4o-mini"
    max_iterations: int = 10
    max_search_results: int = 5
    temperature: float = 0.7
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        
        return cls(
            openai_api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "10")),
        )

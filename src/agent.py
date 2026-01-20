"""Core research agent with LLM-controlled decision making."""

import json
from typing import Optional
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from .config import AgentConfig
from .tools import ToolRegistry


class ResearchAgent:
    """An autonomous research agent that uses LLM to control its workflow."""
    
    SYSTEM_PROMPT = """You are an expert research assistant agent. Your goal is to thoroughly research the given topic and compile a comprehensive report.

You have access to the following tools:
1. web_search: Search the web for information (returns search results with URLs)
2. fetch_webpage: Get detailed content from a specific URL (essential for actual information)
3. take_notes: Save important findings for the final report (CRITICAL for building content)
4. compile_report: Create the final research report (call when you have enough information)

CRITICAL WORKFLOW:
1. Use web_search ONCE to find relevant sources
2. IMMEDIATELY use fetch_webpage to read content from the best URLs found
3. Use take_notes to record key information with sources
4. If more information needed, search for specific aspects, then read those pages
5. When you have gathered sufficient information, compile the report

IMPORTANT RULES:
- Do NOT keep searching without reading content
- After each search, you MUST fetch and read from the URLs found
- Take notes on every important finding you discover
- Compile report when you have 3-5 solid sources of information
- Each iteration should progress toward completing the research

The research is complete when you have enough information to write a comprehensive report on the topic."""

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the research agent."""
        self.config = config or AgentConfig.from_env()
        
        # Initialize OpenAI client with minimal parameters to avoid conflicts
        try:
            self.client = OpenAI(api_key=self.config.openai_api_key)
        except Exception as e:
            # Fallback for any initialization issues
            import os
            # Clear any potential proxy environment variables that might interfere
            proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
            original_values = {}
            for var in proxy_vars:
                if var in os.environ:
                    original_values[var] = os.environ[var]
                    del os.environ[var]
            
            try:
                self.client = OpenAI(api_key=self.config.openai_api_key)
            finally:
                # Restore original proxy settings
                for var, value in original_values.items():
                    os.environ[var] = value
        
        self.tools = ToolRegistry(max_search_results=self.config.max_search_results)
        self.console = Console()
        self.messages: list[dict] = []
        self._report: Optional[str] = None
    
    def _log(self, message: str, style: str = ""):
        """Log a message to the console."""
        self.console.print(message, style=style)
    
    def _log_panel(self, content: str, title: str, style: str = "blue"):
        """Log a panel to the console."""
        self.console.print(Panel(content, title=title, border_style=style))
    
    def _call_llm(self) -> dict:
        """Make a call to the LLM with current message history."""
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=self.messages,
            tools=self.tools.get_tool_definitions(),
            tool_choice="auto",
            temperature=self.config.temperature,
        )
        return response.choices[0].message
    
    def _process_tool_calls(self, message) -> list[dict]:
        """Process tool calls from the LLM response."""
        results = []
        
        if not message.tool_calls:
            return results
        
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}
            
            self._log(f"\n🔧 Executing: {tool_name}", style="bold cyan")
            if tool_name == "web_search":
                self._log(f"   Query: {arguments.get('query', 'N/A')}", style="dim")
            elif tool_name == "fetch_webpage":
                self._log(f"   URL: {arguments.get('url', 'N/A')}", style="dim")
            elif tool_name == "take_notes":
                self._log(f"   Note: {arguments.get('note', 'N/A')[:50]}...", style="dim")
            elif tool_name == "compile_report":
                self._log(f"   Title: {arguments.get('title', 'N/A')}", style="dim")
            
            result = self.tools.execute(tool_name, arguments)
            
            if tool_name == "compile_report":
                result_data = json.loads(result)
                if result_data.get("success"):
                    self._report = result_data.get("report")
            
            results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": result
            })
            
            self._log("   ✅ Completed", style="green")
        
        return results
    
    def research(self, topic: str) -> str:
        """
        Conduct research on the given topic.
        
        The agent autonomously decides what steps to take based on LLM reasoning.
        
        Args:
            topic: The research topic or question to investigate
            
        Returns:
            The compiled research report
        """
        self._log_panel(
            f"Research Topic: {topic}",
            title="🔬 Smart Research Agent",
            style="bold green"
        )
        
        self.messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Please research the following topic and compile a comprehensive report:\n\n{topic}"}
        ]
        self.tools.clear_notes()
        self._report = None
        
        iteration = 0
        max_iterations = self.config.max_iterations
        
        while iteration < max_iterations:
            iteration += 1
            self._log(f"\n{'='*50}", style="dim")
            self._log(f"📍 Iteration {iteration}/{max_iterations}", style="bold yellow")
            
            try:
                response = self._call_llm()
            except Exception as e:
                self._log(f"❌ LLM Error: {e}", style="bold red")
                break
            
            if response.content:
                self._log(f"\n💭 Agent thinking: {response.content[:200]}...", style="italic")
            
            self.messages.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in (response.tool_calls or [])
                ]
            })
            
            if not response.tool_calls:
                self._log("\n✨ Agent completed reasoning", style="bold green")
                break
            
            tool_results = self._process_tool_calls(response)
            self.messages.extend(tool_results)
            
            if self._report:
                self._log("\n📄 Report compiled successfully!", style="bold green")
                break
        
        if iteration >= max_iterations and not self._report:
            self._log("\n⚠️ Max iterations reached, compiling partial report...", style="bold yellow")
            notes = self.tools.get_notes()
            self._report = f"""
PARTIAL RESEARCH REPORT
=======================

Research was terminated after {max_iterations} iterations.

Notes gathered:
{chr(10).join(f'- {note}' for note in notes) if notes else 'No notes were saved.'}
"""
        
        if self._report:
            self.console.print("\n")
            self.console.print(Panel(
                self._report,
                title="📊 Research Report",
                border_style="bold green"
            ))
        
        return self._report or "No report was generated."


def run_agent(topic: str, config: Optional[AgentConfig] = None) -> str:
    """
    Convenience function to run the research agent.
    
    Args:
        topic: The research topic or question
        config: Optional configuration (uses env vars if not provided)
        
    Returns:
        The research report
    """
    agent = ResearchAgent(config)
    return agent.research(topic)

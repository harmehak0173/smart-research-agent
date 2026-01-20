"""Tools available to the research agent."""

import json
from typing import Any
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from tenacity import retry, stop_after_attempt, wait_exponential


class ToolRegistry:
    """Registry of tools available to the agent."""
    
    def __init__(self, max_search_results: int = 5):
        self.max_search_results = max_search_results
        self._tools = {
            "web_search": self.web_search,
            "fetch_webpage": self.fetch_webpage,
            "take_notes": self.take_notes,
            "compile_report": self.compile_report,
        }
        self._notes: list[str] = []
    
    def get_tool_definitions(self) -> list[dict]:
        """Get OpenAI-compatible tool definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for information on a given query. Returns a list of search results with titles, URLs, and snippets.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_webpage",
                    "description": "Fetch and extract the main text content from a webpage URL.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the webpage to fetch"
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "take_notes",
                    "description": "Save important findings or notes during research. Use this to record key information you want to include in the final report.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "note": {
                                "type": "string",
                                "description": "The note or finding to save"
                            },
                            "source": {
                                "type": "string",
                                "description": "The source URL or reference for this note"
                            }
                        },
                        "required": ["note"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compile_report",
                    "description": "Compile all gathered notes and findings into a final research report. Call this when you have gathered enough information to answer the research question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title for the research report"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Executive summary of the findings"
                            },
                            "detailed_findings": {
                                "type": "string",
                                "description": "Detailed findings and analysis"
                            },
                            "conclusion": {
                                "type": "string",
                                "description": "Conclusion and key takeaways"
                            }
                        },
                        "required": ["title", "summary", "detailed_findings", "conclusion"]
                    }
                }
            }
        ]
    
    def execute(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool by name with given arguments."""
        if tool_name not in self._tools:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
        
        try:
            result = self._tools[tool_name](**arguments)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def web_search(self, query: str) -> dict:
        """Perform a web search using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_search_results))
            
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    def fetch_webpage(self, url: str) -> dict:
        """Fetch and extract text content from a webpage."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            content = "\n".join(lines[:100])
            
            if len(content) > 4000:
                content = content[:4000] + "... [truncated]"
            
            return {
                "success": True,
                "url": url,
                "content": content,
                "length": len(content)
            }
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}
    
    def take_notes(self, note: str, source: str = "Unknown") -> dict:
        """Save a research note."""
        note_entry = f"[Source: {source}] {note}"
        self._notes.append(note_entry)
        return {
            "success": True,
            "message": "Note saved successfully",
            "total_notes": len(self._notes)
        }
    
    def compile_report(
        self,
        title: str,
        summary: str,
        detailed_findings: str,
        conclusion: str
    ) -> dict:
        """Compile the final research report."""
        report = f"""
{'='*60}
RESEARCH REPORT: {title}
{'='*60}

EXECUTIVE SUMMARY
{'-'*40}
{summary}

DETAILED FINDINGS
{'-'*40}
{detailed_findings}

CONCLUSION
{'-'*40}
{conclusion}

RESEARCH NOTES
{'-'*40}
"""
        for i, note in enumerate(self._notes, 1):
            report += f"{i}. {note}\n"
        
        report += f"\n{'='*60}\n"
        
        return {
            "success": True,
            "report": report,
            "notes_included": len(self._notes)
        }
    
    def get_notes(self) -> list[str]:
        """Get all saved notes."""
        return self._notes.copy()
    
    def clear_notes(self):
        """Clear all saved notes."""
        self._notes.clear()

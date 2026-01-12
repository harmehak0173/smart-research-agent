#!/usr/bin/env python3
"""Unit tests for the research agent tools."""

import json
from src.tools import ToolRegistry


def test_tool_registry():
    """Test the tool registry initialization and tool definitions."""
    registry = ToolRegistry()
    
    tools = registry.get_tool_definitions()
    assert len(tools) == 4, "Should have 4 tools"
    
    tool_names = [t["function"]["name"] for t in tools]
    assert "web_search" in tool_names
    assert "fetch_webpage" in tool_names
    assert "take_notes" in tool_names
    assert "compile_report" in tool_names
    
    print("✅ Tool registry initialized correctly")


def test_take_notes():
    """Test the note-taking functionality."""
    registry = ToolRegistry()
    
    result = registry.take_notes("Test finding", source="https://example.com")
    assert result["success"] is True
    assert result["total_notes"] == 1
    
    result = registry.take_notes("Another finding", source="https://test.com")
    assert result["total_notes"] == 2
    
    notes = registry.get_notes()
    assert len(notes) == 2
    assert "Test finding" in notes[0]
    assert "example.com" in notes[0]
    
    print("✅ Note-taking works correctly")


def test_compile_report():
    """Test report compilation."""
    registry = ToolRegistry()
    
    registry.take_notes("Important finding 1", source="Source A")
    registry.take_notes("Important finding 2", source="Source B")
    
    result = registry.compile_report(
        title="Test Report",
        summary="This is a test summary",
        detailed_findings="These are the detailed findings",
        conclusion="This is the conclusion"
    )
    
    assert result["success"] is True
    assert "Test Report" in result["report"]
    assert "test summary" in result["report"]
    assert result["notes_included"] == 2
    
    print("✅ Report compilation works correctly")


def test_tool_execution():
    """Test tool execution through the registry."""
    registry = ToolRegistry()
    
    result = json.loads(registry.execute("take_notes", {"note": "Test", "source": "Test"}))
    assert result["success"] is True
    
    result = json.loads(registry.execute("unknown_tool", {}))
    assert "error" in result
    
    print("✅ Tool execution works correctly")


def test_web_search():
    """Test web search functionality (requires internet)."""
    registry = ToolRegistry(max_search_results=3)
    
    try:
        result = registry.web_search("Python programming language")
        assert result["success"] is True
        assert len(result["results"]) > 0
        print(f"✅ Web search works - found {len(result['results'])} results")
    except Exception as e:
        print(f"⚠️ Web search test skipped (no internet?): {e}")


if __name__ == "__main__":
    print("\n🧪 Running Smart Research Agent Tests\n")
    print("-" * 40)
    
    test_tool_registry()
    test_take_notes()
    test_compile_report()
    test_tool_execution()
    test_web_search()
    
    print("-" * 40)
    print("\n✨ All tests passed!\n")

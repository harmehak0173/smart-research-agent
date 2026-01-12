#!/usr/bin/env python3
"""
Smart Research Agent - Main Entry Point

An LLM-powered autonomous research assistant that conducts web research
and compiles comprehensive reports.
"""

import argparse
import sys
from rich.console import Console

from src.agent import ResearchAgent
from src.config import AgentConfig


def main():
    """Main entry point for the research agent."""
    console = Console()
    
    parser = argparse.ArgumentParser(
        description="Smart Research Agent - An LLM-powered research assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "What are the latest developments in quantum computing?"
  python main.py "Compare Python and Rust for systems programming" --max-iterations 15
  python main.py "Explain the benefits of microservices architecture" --model gpt-4o
        """
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="The research topic or question to investigate"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: 10)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Save the report to a file"
    )
    
    args = parser.parse_args()
    
    try:
        config = AgentConfig.from_env()
        
        if args.model:
            config.model = args.model
        if args.max_iterations:
            config.max_iterations = args.max_iterations
        
        agent = ResearchAgent(config)
        report = agent.research(args.topic)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            console.print(f"\n💾 Report saved to: {args.output}", style="bold green")
        
        return 0
        
    except ValueError as e:
        console.print(f"\n❌ Configuration Error: {e}", style="bold red")
        console.print("\nPlease ensure you have set the OPENAI_API_KEY environment variable.")
        console.print("You can create a .env file based on .env.example")
        return 1
        
    except KeyboardInterrupt:
        console.print("\n\n⚠️ Research interrupted by user", style="bold yellow")
        return 130
        
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="bold red")
        return 1


if __name__ == "__main__":
    sys.exit(main())

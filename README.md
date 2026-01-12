# Smart Research Agent 🔬

An **LLM-powered autonomous research assistant** that conducts web research and compiles comprehensive reports. The agent's control flow is entirely determined by the Large Language Model, making it a true AI agent that decides its own actions based on the research context.

## 📋 Assignment Overview

This project demonstrates an AI agent that:
- **Automates the research process** - Given any topic, the agent autonomously searches the web, gathers information, and compiles a structured report
- **Uses LLM for control flow** - The agent uses GPT models to decide what actions to take, when to search, what to read, and when to compile results
- **Is production-ready** - Includes proper error handling, configuration management, logging, and retry logic

## 🎯 Problem Being Solved

**Manual research is time-consuming and tedious.** Researchers, students, and professionals often spend hours:
- Formulating search queries
- Sifting through search results
- Reading multiple articles
- Taking notes
- Synthesizing information into coherent reports

This agent automates the entire workflow, allowing users to simply provide a topic and receive a comprehensive research report.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Input                           │
│                  (Research Topic)                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Research Agent                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              LLM Decision Engine                  │  │
│  │         (GPT-4o-mini / GPT-4o)                   │  │
│  │                                                   │  │
│  │  Decides: What to search? What to read?          │  │
│  │           What notes to take? When to stop?      │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                  │
│                      ▼                                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │                Tool Registry                      │  │
│  │  ┌─────────────┐  ┌─────────────┐                │  │
│  │  │ web_search  │  │fetch_webpage│                │  │
│  │  └─────────────┘  └─────────────┘                │  │
│  │  ┌─────────────┐  ┌──────────────┐               │  │
│  │  │ take_notes  │  │compile_report│               │  │
│  │  └─────────────┘  └──────────────┘               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Research Report                        │
│    (Structured output with findings & citations)        │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/harmehak0173/smart-research-agent.git
   cd smart-research-agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_key_here
   ```

### Usage

**Basic usage:**
```bash
python main.py "What are the latest advancements in renewable energy?"
```

**With options:**
```bash
# Use a different model
python main.py "Explain blockchain technology" --model gpt-4o

# Set max iterations
python main.py "Compare cloud providers" --max-iterations 15

# Save report to file
python main.py "AI in healthcare" --output report.txt
```

**Programmatic usage:**
```python
from src.agent import ResearchAgent
from src.config import AgentConfig

config = AgentConfig.from_env()
agent = ResearchAgent(config)
report = agent.research("Your research topic here")
print(report)
```

## 🛠️ Available Tools

The agent has access to four tools that it uses autonomously:

| Tool | Description |
|------|-------------|
| `web_search` | Searches the web using DuckDuckGo |
| `fetch_webpage` | Extracts content from a specific URL |
| `take_notes` | Saves findings with source citations |
| `compile_report` | Creates the final structured report |

## ⚙️ Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `MAX_ITERATIONS` | Max agent iterations | `10` |

## 📝 Assumptions Made

1. **Internet Access**: The agent requires internet access to perform web searches and fetch webpage content.

2. **OpenAI API**: The project uses OpenAI's API for the LLM. Users need a valid API key with sufficient credits.

3. **Search Engine**: DuckDuckGo is used for web searches as it doesn't require API keys and respects privacy.

4. **Content Extraction**: Web scraping is limited to text content. JavaScript-rendered content may not be fully captured.

5. **Iteration Limit**: A default limit of 10 iterations prevents infinite loops and excessive API costs.

6. **Language**: The agent is optimized for English language research queries and sources.

7. **Rate Limiting**: The agent includes retry logic for API calls but assumes reasonable usage within rate limits.

## 📁 Project Structure

```
smart-research-agent/
├── src/
│   ├── __init__.py      # Package initialization
│   ├── agent.py         # Core agent with LLM control flow
│   ├── config.py        # Configuration management
│   └── tools.py         # Tool implementations
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔒 Security Notes

- Never commit your `.env` file with real API keys
- The agent only reads from websites; it does not modify any external resources
- Web requests include a standard user agent for compatibility

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

---


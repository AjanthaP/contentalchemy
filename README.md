# ContentAlchemy ✨

AI-Powered Multi-Agent Content Marketing Assistant -

## Overview

ContentAlchemy is a production-ready multi-agent system that generates research reports, SEO blogs, LinkedIn posts, and AI-generated images using LangChain, LangGraph, and OpenAI.

### Key Features

- 🤖 **6 Specialized AI Agents** with distinct roles
- 🔄 **LangGraph Workflow** orchestration
- 📝 **Multi-Format Content** generation (Blog, LinkedIn, Research, Images)
- 🔍 **SEO Optimization** engine
- 🎨 **DALL-E 3 Integration** for image generation
- 🌐 **Web Research** with SERP API
- 💻 **Streamlit Web Interface**
- 🧠 **Conversation Memory** system

## Tech Stack

- **LLM**: OpenAI GPT-4
- **Framework**: LangChain + LangGraph
- **Research**: SERP API
- **Images**: DALL-E 3
- **Python**: 3.10+

## Project Structure

```
contentalchemy/
├── src/
│   ├── agents/          # 6 specialized AI agents
│   ├── core/            # Configuration & routing
│   ├── integrations/    # API clients
│   ├── optimization/    # SEO & validation
│   ├── memory/          # Conversation management
│   ├── utils/           # Helper functions
│   ├── workflow/        # LangGraph orchestration
│   └── web_app/         # Streamlit UI
├── tests/               # Unit, integration, e2e tests
├── config/              # Configuration files
├── data/                # Templates & conversations
└── docs/                # Documentation
```

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- SERP API key (optional, for web research)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd contentalchemy
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env and add your API keys
   ```

   Required environment variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SERP_API_KEY=your_serp_api_key_here  # Optional
   ```

## Usage

### Running the Web Application

```bash
streamlit run src/web_app/streamlit_app.py
```

The application will be available at `http://localhost:8501`

### Using the CLI (Coming Soon)

```python
from src.workflow.langgraph_flow import generate_content

result = generate_content("Write a blog post about AI marketing trends in 2024")
print(result["final_content"])
```

## Agents

### 1. Query Handler Agent
Routes user requests to appropriate specialized agents based on intent detection.

### 2. Deep Research Agent
Conducts comprehensive web research using SERP API and generates analytical reports.

### 3. SEO Blog Writer Agent
Creates search-optimized long-form content (1000-2000 words) with proper structure.

### 4. LinkedIn Post Writer Agent
Generates engaging professional social media content optimized for LinkedIn.

### 5. Image Generator Agent
Produces custom visuals using DALL-E 3 with automatic prompt optimization.

### 6. Content Strategist Agent
Formats and organizes research into readable, actionable content.

## Configuration

Edit `src/core/config.py` or use environment variables to configure:

- LLM models and parameters
- Content generation settings
- API keys and endpoints
- Memory and caching options

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/
```

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8501
```

## API Documentation

### Generate Content

```python
from src.workflow.langgraph_flow import generate_content

# Research report
result = generate_content(
    user_query="Research AI marketing trends in 2024"
)

# Blog post
result = generate_content(
    user_query="Write an SEO blog about email automation for small businesses"
)

# LinkedIn post
result = generate_content(
    user_query="Create a LinkedIn post about our company's new AI product"
)

# Image
result = generate_content(
    user_query="Generate a professional header image for a tech blog"
)
```

## Roadmap

- [ ] Complete Streamlit UI implementation
- [ ] Add workflow orchestration
- [ ] Implement memory system
- [ ] Add optimization engines
- [ ] Create comprehensive tests
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] API endpoint exposure
- [ ] WordPress/CMS integration
- [ ] Multi-language support

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [LangChain](https://python.langchain.com/)
- Powered by [OpenAI](https://openai.com/)
- UI with [Streamlit](https://streamlit.io/)
- Research via [SERP API](https://serpapi.com/)

## Support

For questions and support:
- Create an issue on GitHub
- Email: support@contentalchemy.io
- Documentation: [docs/](docs/)

---

**Built with ❤️ for content marketers everywhere**

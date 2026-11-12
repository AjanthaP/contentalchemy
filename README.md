# ContentAlchemy ✨

AI-Powered Multi-Agent Content Marketing Assistant

## Overview

ContentAlchemy is a multi-agent system that generates research reports, SEO blogs, LinkedIn posts, and AI-generated images using LangChain, LangGraph, and OpenAI. A React web app talks to a FastAPI backend that runs the agent workflow.

### Key Features

- 🤖 **6 Specialized AI Agents** with distinct roles
- 🔄 **LangGraph Workflow** orchestration
- 📝 **Multi-Format Content** generation (Blog, LinkedIn, Research, Images)
- 🔍 **SEO Optimization** and content validation
- 🎨 **Image Generation** with OpenAI GPT Image, or Stable Diffusion via Hugging Face
- 🌐 **Web Research** with SERP API
- 💻 **React + Vite Web App** backed by a **FastAPI** REST API
- 🔗 **LinkedIn Integration**: sign in with LinkedIn and publish posts directly
- 🧠 **Conversation Memory** and user profiles
- 📈 **LangSmith Tracing** (optional)
- 🛡️ **Rate Limiting** to protect the paid LLM and image endpoints

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite — deployed on Vercel |
| Backend API | FastAPI + Uvicorn (Python 3.10+) — Docker image deployed on Google Cloud Run |
| Agents & workflow | LangChain + LangGraph |
| LLM | OpenAI chat models (configurable with `OPENAI_MODEL`) |
| Images | OpenAI GPT Image (default), Stable Diffusion via Hugging Face |
| Research | SERP API |
| Observability | LangSmith (optional) |
| Caching | Redis (optional) |
| Rate limiting | slowapi |

## Project Structure

```
contentalchemy/
├── src/
│   ├── api/             # FastAPI app, request/response schemas, rate limiting
│   ├── agents/          # 6 specialized AI agents + Stable Diffusion generator
│   ├── core/            # Settings (loaded from environment variables / .env)
│   ├── integrations/    # LinkedIn OAuth, Redis client
│   ├── memory/          # Conversation history & user profiles
│   ├── optimization/    # SEO, brand voice, content validation
│   ├── utils/           # Helper functions
│   ├── workflow/        # LangGraph orchestration
│   └── web_app/         # Legacy Streamlit prototype (no longer used)
├── frontend/            # React + Vite + TypeScript web app
├── backend/             # Copy of the backend Dockerfile
├── tests/               # Unit, integration, e2e tests
├── Dockerfile           # FastAPI backend image (Cloud Run)
├── vercel.json          # Vercel build config + /api rewrite to the backend
└── requirements.txt     # Backend Python dependencies
```

## Local Development

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- OpenAI API key
- SERP API key (optional, for web research)

### 1. Backend (FastAPI)

```powershell
git clone https://github.com/AjanthaP/contentalchemy.git
cd contentalchemy

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

copy .env.example .env         # Windows  (cp on Mac/Linux)
# Edit .env and add your API keys

uvicorn src.api.app:app --reload --port 8080
```

The API runs at `http://localhost:8080`, with interactive docs at `http://localhost:8080/docs`.

### 2. Frontend (React + Vite)

```bash
cd frontend
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8080
npm install
npm run dev
```

The web app runs at `http://localhost:5173`. See [frontend/README.md](frontend/README.md) for more.

## Configuration

All backend settings live in `src/core/config.py` and can be set through environment variables or `.env`. See [.env.example](.env.example) for the full list.

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | LLM calls and GPT Image generation |
| `OPENAI_MODEL` | No | Chat model used by the agents |
| `SERP_API_KEY` | No | Web research (mock data is used without it) |
| `HF_API_KEY` | No | Stable Diffusion image provider |
| `LANGSMITH_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT` | No | LangSmith tracing |
| `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REDIRECT_URI` | No | LinkedIn sign-in and posting |
| `FRONTEND_BASE_URL` | No | Where the LinkedIn callback sends users back to |
| `ALLOWED_ORIGINS` | No | Comma-separated frontend origins allowed by CORS |
| `RATE_LIMIT_*`, `TRUSTED_PROXY_HOPS` | No | Rate limiting (see below) |

> Never commit `.env`. It is already in `.gitignore`. In production, set these values in the Cloud Run service configuration.

### Rate Limiting

The API is rate limited per client IP using [slowapi](https://github.com/laurentS/slowapi). Requests over the limit get `429 Too Many Requests`.

| Setting | Default | Applies to |
|---------|---------|------------|
| `RATE_LIMIT_DEFAULT` | `120/minute` | Every endpoint, per IP (`/health` is exempt) |
| `RATE_LIMIT_GENERATE` | `5/minute;50/day` | `POST /api/generate`, per IP |
| `RATE_LIMIT_GENERATE_GLOBAL` | `500/day` | `POST /api/generate`, all callers combined (caps total OpenAI spend) |
| `RATE_LIMIT_ENABLED` | `true` | Turn rate limiting on/off |
| `RATE_LIMIT_STORAGE_URI` | `memory://` | Where counters are kept |
| `TRUSTED_PROXY_HOPS` | `1` | Proxies that append to `X-Forwarded-For` |

Notes:
- The client IP is taken from the right-most `X-Forwarded-For` entry, which Cloud Run adds itself, so callers can't bypass limits by sending a fake header. If you put another proxy (e.g. a load balancer) in front of Cloud Run, increase `TRUSTED_PROXY_HOPS` by one per proxy.
- `memory://` counts per container instance. If Cloud Run scales to several instances, either cap max instances or point `RATE_LIMIT_STORAGE_URI` at Redis (e.g. `redis://host:6379/1`) so all instances share the counts.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/generate` | Run the agent workflow (`content_type`: `research`, `blog`, `linkedin`, `image`, `strategy`) |
| `GET` | `/api/history/{session_id}` | Conversation history for a session |
| `GET` / `PUT` | `/api/profile/{user_email}` | Read / update a user profile |
| `GET` | `/api/linkedin/login` | Start LinkedIn OAuth |
| `GET` | `/api/linkedin/callback` | LinkedIn OAuth callback |
| `GET` | `/api/linkedin/profile` | Fetch the signed-in LinkedIn profile |
| `POST` | `/api/linkedin/post` | Publish a post to LinkedIn |

Example:

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Write an SEO blog about email automation for small businesses", "content_type": "blog"}'
```

You can also call the workflow directly from Python:

```python
from src.workflow.langgraph_flow import generate_content

result = generate_content(
    query="Create a LinkedIn post about our company's new AI product",
    content_type="linkedin",
)
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
Produces custom visuals with OpenAI GPT Image (or Stable Diffusion) with automatic prompt optimization.

### 6. Content Strategist Agent
Formats and organizes research into readable, actionable content.

## Deployment

### Backend → Google Cloud Run

The root `Dockerfile` builds the FastAPI backend and serves it on port 8080.

```bash
# Build and run locally
docker build -t contentalchemy-api .
docker run -p 8080:8080 --env-file .env contentalchemy-api
```

Deploy the image to Cloud Run and set the environment variables (API keys, `ALLOWED_ORIGINS`, rate limits) in the service configuration.

### Frontend → Vercel

`vercel.json` builds the `frontend/` app and rewrites `/api/*` to the Cloud Run backend. `frontend/.env.production` sets `VITE_API_BASE_URL` to the backend URL.

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
black src/ tests/   # Format
flake8 src/ tests/  # Lint
mypy src/           # Type checking
```

## Roadmap

- [x] LangGraph workflow orchestration
- [x] Memory system (conversations & user profiles)
- [x] SEO and content optimization engines
- [x] React web app (replaced the Streamlit prototype)
- [x] REST API with FastAPI
- [x] Docker containerization and Cloud Run deployment
- [x] LinkedIn sign-in and posting
- [x] API rate limiting
- [ ] Comprehensive test coverage
- [ ] CI/CD pipeline
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

- Built with [LangChain](https://python.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)
- Powered by [OpenAI](https://openai.com/)
- API with [FastAPI](https://fastapi.tiangolo.com/), UI with [React](https://react.dev/) + [Vite](https://vitejs.dev/)
- Research via [SERP API](https://serpapi.com/)

## Support

For questions and support, please [open an issue on GitHub](https://github.com/AjanthaP/contentalchemy/issues).

---

**Built with ❤️ for content marketers everywhere**

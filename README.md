# ReqLens AI

ReqLens AI is an evidence-first requirements intelligence application. Teams upload PDF, DOCX, or TXT requirements, search them with project-isolated hybrid retrieval, review possible quality issues, ask grounded questions, compare versions, and export an audit report.

This repository deliberately keeps the architecture understandable for an intern: routes handle HTTP, services coordinate use cases, repositories own MongoDB access, and dedicated modules own ingestion, retrieval, audits, and LangGraph orchestration.

## What works

- JWT registration, login, current-user lookup, and protected routes
- Owner-scoped projects and dashboard metrics
- Secure PDF, DOCX, and TXT upload with type/size validation
- Structure-aware chunks, optional OpenAI embeddings, and source metadata
- Hybrid keyword/vector retrieval with exact-ID support, safe self-query filters, multi-query expansion, reranking, and generation-only context compression
- Bounded LangGraph retrieve → grade → rewrite → retry → answer flow
- Grounded project chat with citations and optional, labelled Tavily results
- Audit candidates for ambiguity, missing measurability, duplicates, and time conflicts
- Human review states: pending, approved, rejected, needs more evidence
- Semantic version comparison and structured JSON reports
- Responsive React/Tailwind interface and Docker setup

AI findings are always candidates. The UI and report distinguish them from human decisions.

## Architecture

```text
React + Vite + Tailwind
          │ REST / JWT
          ▼
FastAPI routes → services → repositories → MongoDB
                    │
                    ├─ ingestion → chunks → embeddings
                    ├─ hybrid retrieval → LangGraph → grounded answer
                    ├─ deterministic audit candidates → human review
                    └─ optional Tavily research (explicit opt-in)
```

The API never sends OpenAI, Tavily, MongoDB, or JWT credentials to React. Retrieval always filters by `project_id`, and every protected project request checks ownership first.

## First run (recommended: Docker)

1. Revoke the keys that were pasted into chat and create fresh OpenAI, Tavily, and MongoDB credentials.
2. Copy `.env.example` to `.env`.
3. Set a random `JWT_SECRET` with at least 32 characters and add any API keys. Docker Compose automatically points the API container at its MongoDB service.
4. Start everything:

```powershell
docker compose up --build
```

After the services start, open:

- **ReqLens frontend:** [http://localhost:5173](http://localhost:5173)
- **FastAPI documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend health check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## Run without Docker (Windows PowerShell)

Start MongoDB locally on port `27017`, then:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

In another terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to port 8000.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `MONGODB_URL` | MongoDB connection string; backend only |
| `MONGODB_DB_NAME` | Database name, default `reqlens` |
| `JWT_SECRET` | Signs access tokens; use a long random value |
| `OPENAI_API_KEY` | Enables embeddings and grounded answer generation |
| `TAVILY_API_KEY` | Enables explicitly requested external research |
| `OPENAI_CHAT_MODEL` | Central chat model setting |
| `OPENAI_EMBEDDING_MODEL` | Central embedding model setting |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |

Without an OpenAI key, upload, lexical retrieval, audit, review, compare, and reports still work. Chat returns retrieved evidence without synthesizing it.

For throwaway development only, `ALLOW_IN_MEMORY_DB=true` enables a temporary database when MongoDB is unavailable. All accounts and project data disappear when the backend stops, so the example configuration keeps this fallback disabled. Production environments never use it.

## Code map

```text
backend/
├── app/
│   ├── main.py            # app lifecycle, middleware
│   ├── routes.py          # thin HTTP endpoints
│   ├── services.py        # business use cases
│   ├── repositories.py    # MongoDB queries
│   ├── ingestion.py       # extraction and chunking
│   ├── rag.py             # embeddings and hybrid retrieval
│   ├── agent_graph.py     # bounded LangGraph chat workflow
│   └── audit.py           # explainable audit candidate checks
└── tests/
frontend/
└── src/
    ├── components/        # reusable UI
    ├── features/          # auth, dashboard, projects
    └── lib/               # API and auth infrastructure
```

Read [docs/architecture.md](docs/architecture.md) for request and data flows and [docs/learning-guide.md](docs/learning-guide.md) for a beginner-friendly walkthrough.

## Tests and builds

```powershell
python -m pytest backend/tests
Set-Location frontend
npm run build
```

The tests do not call OpenAI or Tavily. External APIs should stay mocked in automated tests.

## Production notes

- Put secrets in a managed secret store, not `.env` in Git.
- Use HTTPS and a restrictive `CORS_ORIGINS` value.
- Use Atlas Vector Search when the corpus grows beyond the bounded application-side candidate set; `RetrievalService` is the replacement boundary.
- Move synchronous document processing to a durable worker/queue for large files or high upload volume.
- Add refresh-token rotation/SSO and role-based access before multi-team deployment.
- Add malware scanning and object storage before accepting untrusted public uploads.


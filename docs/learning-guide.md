# Learning guide

Use one feature to understand the whole stack: “Ask ReqLens”.

1. `ProjectPage.tsx` sends a question through the shared `api()` client.
2. `routes.py` validates `ChatRequest`, loads the current user, and checks project ownership.
3. `IntelligenceService.chat()` starts the graph and persists the conversation.
4. `agent_graph.py` makes workflow decisions with an explicit `ChatState` TypedDict.
5. `rag.py` retrieves project-scoped evidence and calls OpenAI only after evidence exists.
6. The response contains the answer, grounded flag, original evidence, and source metadata.
7. React renders the answer separately from internal and external evidence.

Good exercises, in order:

1. Add a `priority` field to projects end-to-end.
2. Add a reviewer comment input before a finding decision.
3. Add pagination to documents and findings.
4. Replace the heuristic relevance threshold with an LLM structured-output grader.
5. Implement Atlas Vector Search inside `RetrievalService`.

When debugging, follow one request in this order: browser Network tab → FastAPI `/docs` → route → service → repository/AI module → MongoDB document. The API returns an `x-request-id` header and logs it for correlation.


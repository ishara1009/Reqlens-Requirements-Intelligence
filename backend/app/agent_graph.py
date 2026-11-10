from typing import Any, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from app.rag import RetrievalService


MAX_RETRIEVAL_RETRIES = 2


class ChatState(TypedDict, total=False):
    user_id: str
    project_id: str
    question: str
    retrieval_query: str
    retrieved_documents: list[dict[str, Any]]
    retry_count: int
    answer: str
    grounded: bool
    errors: list[str]


def build_chat_graph(retrieval: RetrievalService):
    async def retrieve(state: ChatState) -> ChatState:
        rows = await retrieval.search(state["project_id"], state.get("retrieval_query", state["question"]))
        return {"retrieved_documents": rows}

    def route_relevance(state: ChatState) -> Literal["generate", "rewrite", "insufficient"]:
        rows = state.get("retrieved_documents", [])
        if rows and rows[0].get("score", 0) >= 0.04: return "generate"
        if state.get("retry_count", 0) < MAX_RETRIEVAL_RETRIES: return "rewrite"
        return "insufficient"

    async def rewrite(state: ChatState) -> ChatState:
        count = state.get("retry_count", 0) + 1
        expanded = f"{state['question']} requirements policy constraint acceptance criteria"
        return {"retrieval_query": expanded, "retry_count": count}

    async def generate(state: ChatState) -> ChatState:
        rows = state.get("retrieved_documents", [])
        return {"answer": await retrieval.answer(state["question"], rows), "grounded": bool(rows)}

    def insufficient(_: ChatState) -> ChatState:
        return {"answer": "Insufficient supporting evidence was found in the uploaded project documents.", "grounded": False}

    graph = StateGraph(ChatState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("rewrite", rewrite)
    graph.add_node("generate", generate)
    graph.add_node("insufficient", insufficient)
    graph.add_edge(START, "retrieve")
    graph.add_conditional_edges("retrieve", route_relevance, {"generate": "generate", "rewrite": "rewrite", "insufficient": "insufficient"})
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("generate", END)
    graph.add_edge("insufficient", END)
    return graph.compile()


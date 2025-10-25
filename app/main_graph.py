from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph_nodes import (
    retrieve_node,
    grade_docs_node,
    generate_node,
    grade_answer_node,
    rewrite_question_node,
    answer_router_node,
    filtered_docs_router,
)

class GraphState(TypedDict, total=False):
    question: str
    retrieved_docs: List[dict]
    filtered_docs: List[dict]
    answer: str
    useful: str
    supported: str
    iterations: int
    rewrite_count: int
    generation_count: int

builder = StateGraph(GraphState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("grade_docs", grade_docs_node)
builder.add_node("generate", generate_node)
builder.add_node("grade_answer", grade_answer_node)
builder.add_node("rewrite_question", rewrite_question_node)


builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "grade_docs")


builder.add_conditional_edges(
    "grade_docs",
    filtered_docs_router,
    {"rewrite": "rewrite_question", "generate": "generate"}
)

builder.add_edge("generate", "grade_answer")


builder.add_conditional_edges(
    "grade_answer",
    answer_router_node,
    {"retry": "generate", "rewrite": "rewrite_question", "end": END}
)
#builder.add_edge("grade_answer", "answer_router")

builder.add_edge("rewrite_question", "retrieve")

graph = builder.compile()

if __name__ == "__main__":
    question = input("❓ Sormak istediğiniz soruyu yazın: ")
    state = {"question": question}
    result = graph.invoke(state)

    print("\n📄 Retrieve edilen belgeler:")
    for i, doc in enumerate(result.get("retrieved_docs", []), 1):
        print(f"\n--- Belge {i} ---")
        print(f"Kaynak: {doc.get('source')} | Sayfa: {doc.get('page_number')}")
        print(doc.get("text"))

    print("\n✅ 🔚 Final Answer:\n", result.get("answer"))
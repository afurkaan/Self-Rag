from typing import Dict, Any, List
import requests
from sentence_transformers import SentenceTransformer
from llm_interface import is_rel, is_sup, is_useful, generate_answer, rewrite_question

embedding_model = SentenceTransformer("emrecan/bert-base-turkish-cased-mean-nli-stsb-tr")
VESPA_SEARCH_URL = "http://localhost:8080/search/"

def vespa_search(question: str, top_k: int = 2) -> list[Dict[str, Any]]:
    embedding = embedding_model.encode(question).tolist()
    vespa_query = {
        "yql": f"select * from sources * where ([{{\"targetNumHits\":{top_k}}}]nearestNeighbor(embedding, query_embedding));",
        "hits": top_k,
        "ranking": {
            "profile": "default",
            "features": {
                "query(query_embedding)": embedding
            }
        }
    }
    response = requests.post(VESPA_SEARCH_URL, json=vespa_query)
    if response.status_code == 200:
        hits = response.json().get("root", {}).get("children", [])
        return [
            {
                "text": hit["fields"]["text"],
                "source": hit["fields"]["source"],
                "page_number": hit["fields"]["page_number"],
            }
            for hit in hits
        ]
    else:
        return []

def retrieve_node(state: dict) -> dict:
    print("\n🟢 [RETRIEVE NODE] input state:", state)
    question = state["question"]
    retrieved_docs = vespa_search(question, top_k=2)
    print(f"\n🔍 Vespa'dan gelen {len(retrieved_docs)} belge:")
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"\n--- Belge {i} ---")
        print(f"Kaynak: {doc['source']} | Sayfa: {doc['page_number']}")
        print(doc["text"])
    out = {
        "retrieved_docs": retrieved_docs,
        "iterations": state.get("iterations", 0) + 1
    }
    print("🟢 [RETRIEVE NODE] output:", out)
    return out

def grade_docs_node(state: dict) -> dict:
    print("\n🔵 [GRADE_DOCS NODE] input state:", state)
    question = state["question"]
    retrieved_docs = state["retrieved_docs"]
    filtered_docs = []
    for doc in retrieved_docs:
        text = doc["text"]
        result = is_rel(question, text)
        print(f"   → is_rel? '{result}' for:\n{text[:200]}")
        if result == "evet":
            filtered_docs.append(doc)
    out = {"filtered_docs": filtered_docs}
    print("🔵 [GRADE_DOCS NODE] output:", out)
    return out

def generate_node(state: dict) -> dict:
    print("\n🟣 [GENERATE NODE] input state:", state)
    question = state["question"]
    docs = state["filtered_docs"]
    answer = generate_answer(question, docs)
    out = {"answer": answer,
           "generation_count": state.get("generation_count", 0) + 1}
    print("🟣 [GENERATE NODE] output:", out)
    return out

def grade_answer_node(state: dict) -> dict:
    print("\n🟠 [GRADE_ANSWER NODE] input state:", state)
    question = state["question"]
    answer = state["answer"]
    docs = state["filtered_docs"]
    useful = is_useful(question, answer)
    print("IS USEFUL SONUCU: ", useful)
    supported = "hayır"
    for doc in docs:
        text = doc["text"]
        result = is_sup(question, answer, doc["text"])
        print(f"   → is_sup? '{result}' for:\n{text[:200]}")
        if result == "evet":
            supported = "evet"
            break
    out = {"useful": useful, "supported": supported}
    print("🟠 [GRADE_ANSWER NODE] output:", out)
    return out

def rewrite_question_node(state: dict) -> dict:
    print("\n🟡 [REWRITE NODE] input state:", state)
    question = state["question"]
    rewritten = rewrite_question(question)
    out = {"question": rewritten,
           "rewrite_count": state.get("rewrite_count", 0) + 1}
    print("🟡 [REWRITE NODE] output:", out)
    return out

def filtered_docs_router(state: dict) -> str:
    print("\n🔁 [ROUTER: filtered_docs_router] state:", state)
    filtered = state.get("filtered_docs", [])
    rewrite_count = state.get("rewrite_count", 0)
    if filtered:
        decision= "generate"
    elif rewrite_count >= 5:
        print("🔁 Rewrite sınırına ulaşıldı. Cevap üretilecek.")
        decision= "generate"
    else:
        decision= "rewrite"
    print(f"🔁 [ROUTER: filtered_docs_router] decision → {decision}")
    return decision

def answer_router_node(state: dict) -> str:
    print("\n🔁 [ROUTER: answer_router_node] state:", state)
    useful = state.get("useful", "hayır")
    supported = state.get("supported", "hayır")
    generation_count = state.get("generation_count", 0)
    rewrite_count = state.get("rewrite_count", 0)
    if supported == "hayır" and generation_count < 5:
        decision = "retry"
    elif useful == "hayır" and rewrite_count < 5:
        decision = "rewrite"
    else:
        decision = "end"
    print(f"🔁 [ROUTER: answer_router_node] decision → {decision}")
    return decision

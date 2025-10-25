import requests
from sentence_transformers import SentenceTransformer
import json

# Load the same embedding model used during indexing
model = SentenceTransformer("emrecan/bert-base-turkish-cased-mean-nli-stsb-tr")

# Vespa search endpoint
VESPA_SEARCH_URL = "http://localhost:8080/search/"

# Ask user for a question
query_text = input("Enter your question in Turkish: ")

# Encode question to get embedding
query_embedding = model.encode(query_text).tolist()

# Construct Vespa nearest neighbor query
vespa_query = {
    "yql": "select * from sources * where ([{\"targetNumHits\":2}]nearestNeighbor(embedding, query_embedding));",
    "hits": 2,
    "ranking": {
        "profile": "default",
        "features": {
            "query(query_embedding)": query_embedding
        }
    }
}

# Send POST request to Vespa
response = requests.post(VESPA_SEARCH_URL, json=vespa_query)

# Print status and results
print("\n🔍 Vespa Response Status:", response.status_code)

if response.status_code == 200:
    results = response.json()
    hits = results.get("root", {}).get("children", [])
    
    print(f"\n📄 Top {len(hits)} retrieved chunks:\n")
    for i, hit in enumerate(hits):
        fields = hit.get("fields", {})
        print(f"Chunk {i+1}:")
        print("Text:", fields.get("text"))
        print("Source:", fields.get("source"))
        print("Page:", fields.get("page_number"))
        print("-" * 80)
else:
    print("❌ Error in querying Vespa:", response.text)

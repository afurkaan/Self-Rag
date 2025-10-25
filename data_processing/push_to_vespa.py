import os
import jsonlines
import requests
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Load the embedding model
model = SentenceTransformer("emrecan/bert-base-turkish-cased-mean-nli-stsb-tr")

# Define the path to the processed .jsonl files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNK_DIR = os.path.join(BASE_DIR, "../data/processed_chunks")

# Vespa index configuration
VESPA_ENDPOINT = "http://localhost:8080"
NAMESPACE = "myselfrag"
DOC_TYPE = "documents"

# Iterate through all .jsonl files in the processed_chunks folder
for file in os.listdir(CHUNK_DIR):
    if not file.endswith(".jsonl"):
        continue

    file_path = os.path.join(CHUNK_DIR, file)
    with jsonlines.open(file_path, mode="r") as reader:
        chunks = list(reader)

    print(f"📄 Indexing {file} with {len(chunks)} chunks...")

    for chunk in tqdm(chunks, desc=f"→ Sending chunks from {file}"):
        text = chunk["text"]
        source = chunk["source"]
        page = chunk["page_number"]
        chunk_id = chunk["chunk_id"]

        # Generate embedding
        embedding = model.encode(text, normalize_embeddings=True).tolist()

        # Create document payload
        vespa_doc = {
            "fields": {
                "text": text,
                "source": source,
                "page_number": page,
                "chunk_id": chunk_id,
                "embedding": embedding
            }
        }

        # Create document ID and endpoint
        doc_id = f"{source}_{chunk_id}".replace("/", "_")
        url = f"{VESPA_ENDPOINT}/document/v1/{NAMESPACE}/{DOC_TYPE}/docid/{doc_id}"

        # Send to Vespa
        try:
            resp = requests.post(url, json=vespa_doc)
            if resp.status_code != 200:
                print(f"❌ Failed ({resp.status_code}): {doc_id}")
        except Exception as e:
            print(f"⚠️ Error while sending {doc_id}: {e}")

import os
import jsonlines
import requests

# Ayarlar
VESPA_ENDPOINT = "http://localhost:8080"
NAMESPACE = "myselfrag"
DOC_TYPE = "documents"

# Chunk verilerinin bulunduğu klasör
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNK_DIR = os.path.join(BASE_DIR, "../processed_chunks")  # senin yapına göre ayarlı

# Tüm dokümanları sil
for file in os.listdir(CHUNK_DIR):
    if not file.endswith(".jsonl"):
        continue

    file_path = os.path.join(CHUNK_DIR, file)
    with jsonlines.open(file_path, mode="r") as reader:
        for chunk in reader:
            doc_id = f"{chunk['source']}_{chunk['chunk_id']}".replace("/", "_")
            url = f"{VESPA_ENDPOINT}/document/v1/{NAMESPACE}/{DOC_TYPE}/docid/{doc_id}"
            try:
                resp = requests.delete(url)
                if resp.status_code in (200, 404):
                    print(f"🗑️ Deleted {doc_id}")
                else:
                    print(f"❌ Failed to delete {doc_id}: {resp.status_code}")
            except Exception as e:
                print(f"⚠️ Error deleting {doc_id}: {e}")

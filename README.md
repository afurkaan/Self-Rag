# Self-RAG: Custom Implementation

This is my custom implementation of  
[Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511).

---

## Overview

This project is a personal re-implementation of the Self-RAG architecture —  
a system that learns to retrieve, generate, and self-critique its outputs through iterative reflection.

It integrates multiple modern tools to reproduce the core ideas of the paper using practical components.

---

## Components Used

- **Ollama** — for local LLM inference and prompt execution  
- **Vespa** — as the vector database for document embeddings and retrieval  
- **LangGraph** — for orchestrating the data flow and logic graph between modules  

---

## How It Works

1. **Text Chunking & Embedding:**  
   Input documents are split into semantically coherent chunks.  
   Each chunk is embedded into a dense vector representation.

2. **Vector Storage & Retrieval:**  
   These embeddings are stored in Vespa, which enables fast vector similarity search for relevant chunks.

3. **LLM Reasoning via Ollama:**  
   Queries are sent to an Ollama-served LLM.  
   The retrieved context from Vespa is combined with the user’s input to generate a first draft answer.

4. **Self-Reflection with LangGraph:**  
   Using LangGraph, the system organizes the reasoning flow —  
   feeding generated responses back into the LLM for critique and refinement, inspired by Self-RAG’s reflection mechanism.

---

## Technologies

| Component | Purpose |
|------------|----------|
| Ollama | Local LLM interface |
| Vespa | Vector database for embeddings |
| LangGraph | Graph-based orchestration |
| Docker | Containerized setup for reproducibility |

---

## Reference

Shinn, N., Cassano, F., Kiela, D., & Weston, J. (2023).  
*Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.*  
[arXiv:2310.11511](https://arxiv.org/abs/2310.11511)

---

## Notes

This implementation is experimental and simplified compared to the original Self-RAG paper.  
It focuses on practical integration of retrieval, generation, and reflection using available open-source components.

---

## License

This project is released for educational and research purposes.

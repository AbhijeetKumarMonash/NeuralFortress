# 🧠 NeuralFortress

> **Beyond RAG: an agentic "second brain" that thinks when you *write*, and decides how to search when you *ask*.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3%20(Vite)-4FC08D?logo=vuedotjs&logoColor=white)
![Postgres](https://img.shields.io/badge/Neon-pgvector-336791?logo=postgresql&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-8E75B2?logo=google&logoColor=white)

NeuralFortress is an **Agentic Personal Knowledge Management System (PKMS)**. You drop in raw text, documents, or code — of any length — and it autonomously summarizes, tags, embeds, *and reasons about* what you saved, surfacing connections you never explicitly drew.

Most note apps are write-only graveyards. NeuralFortress is built on a simple inversion: **the system should think about your knowledge, not just store it.**

---

## ✨ What it does (v3)

| Capability | Description |
|---|---|
| **Autonomous ingestion** | Gemini summarizes + tags every note. Large documents are **chunked automatically** so nothing is too big to absorb. |
| **Synthesis-on-ingest** | The moment you save, the system retrieves your most related memories and reasons about how the new note *connects, overlaps, or contradicts* them — unprompted. |
| **Semantic recall** | Text becomes 1536-dim vectors in pgvector; search works on *meaning*, not keywords. |
| **Three retrieval modes** | **RAG** (fixed pipeline), **Agent** (autonomous tool-calling), and **GraphRAG** (multi-hop traversal of an entity-relationship graph — beyond vector distance). |
| **Two graphs** | A document-similarity **Neural Map** and an entity-relationship **Knowledge Graph**, both interactive. |

---

## 🏗️ Architecture

```
Vue 3 (Vite)  ──HTTP/JSON──▶  FastAPI  ──SQL──▶  Neon PostgreSQL + pgvector
                                  │
                                  └──▶  Google Gemini
                                        ├─ gemini-2.5-flash      (reasoning · synthesis · agent · extraction)
                                        └─ gemini-embedding-001  (1536-dim embeddings)
```

One database holds vectors **and** relational metadata **and** the knowledge graph — no separate vector DB to operate.

---

## 🚀 Getting started

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows  (source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require
GEMINI_API_KEY=your_google_gemini_api_key
```

Create the tables (additive & safe — never drops data), then run:

```bash
python create_tables.py
python -m uvicorn main:app --reload
```

Backend serves on `http://127.0.0.1:8000` (interactive docs at `/docs`).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App serves on `http://localhost:5173`.

---

## 🔌 API reference

| Method | Endpoint | Purpose | Since |
|---|---|---|---|
| `GET` | `/api/status` | Health check | v1 |
| `POST` | `/api/ingest` | Chunk → embed → summarize → **synthesize** → graph-extract | v1 (v2/v3 upgraded) |
| `POST` | `/api/search` | **RAG**: embed → top-3 cosine → answer | v1 |
| `POST` | `/api/agent` | **Agent**: autonomous tool-calling (`search_notes`, `list_topics`, …) | v2 |
| `POST` | `/api/graphrag` | **GraphRAG**: multi-hop entity traversal + answer with reasoning path | v3 |
| `GET` | `/api/graph` | Document-similarity Neural Map (nodes + cosine edges) | v2 |
| `GET` | `/api/knowledge-graph` | Entity Knowledge Graph (typed nodes + relationship edges) | v3 |
| `GET` | `/api/documents` | List all memories | v1 |
| `DELETE` | `/api/documents/{id}` | Purge a memory (cascades to chunks + relationships) | v2 |
| `POST` / `GET` | `/api/watchers` | Manage autonomous source watchers | v3 *(in dev)* |

---

## 🧩 The three minds

- **RAG_MODE — The Librarian.** Fixed, deterministic, cheap. Embed the question, fetch the closest three memories, answer strictly from them.
- **AGENT_MODE — The Investigator.** Gemini is handed tools and decides which to call, reformulating its own queries and searching again until satisfied. The server log prints each tool call — live proof of autonomy.
- **GRAPH_MODE — The Cartographer.** Traverses a graph of entities and relationships *extracted* from your notes, reaching connections across documents that pure vector distance can't — and returns the multi-hop path it walked.

---

## 📁 Project structure

```
NeuralFortress/
├── backend/
│   ├── main.py             # FastAPI app + all endpoints
│   ├── models.py           # SQLAlchemy models (Document, DocumentChunk, Entity, Relationship)
│   ├── database.py         # engine + session (pool_pre_ping for Neon)
│   ├── knowledge_graph.py  # chunking, triple extraction, multi-hop BFS  (v3)
│   ├── create_tables.py    # one-time table creation  (v3)
│   ├── mcp_server.py        # exposes the brain as MCP tools  (v3, in dev)
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api.js
        ├── views/      HomeView.vue · AboutView.vue
        └── components/ IngestionEngine.vue · RetrievalTerminal.vue ·
                        MatrixArchive.vue · KnowledgeGraph.vue · EntityGraph.vue
```

---

## 🛣️ Roadmap (The Autonomous Frontier)

- **MCP Integration** — expose the brain as a standard tool any AI client (VS Code / Copilot, Cursor, Claude) can call.
- **Async Watchers** — background agents that read sources overnight, deduplicate, and self-ingest.
- **Deeper GraphRAG** — community detection and richer multi-hop reasoning over the entity graph.

---

## 📚 Documentation

Full version history lives in the [Wiki](https://github.com/AbhijeetKumarMonash/NeuralFortress/wiki):
**[v1 — Foundation](https://github.com/AbhijeetKumarMonash/NeuralFortress/wiki/Version-1-%E2%80%94-Foundation)** · **[v2 — Beyond RAG](https://github.com/AbhijeetKumarMonash/NeuralFortress/wiki/Version-2-%E2%80%94-Beyond-RAG)** · **[v3 — The Knowledge Graph](https://github.com/AbhijeetKumarMonash/NeuralFortress/wiki/Version-3-%E2%80%94-The-Knowledge-Graph)**

---

## 🎤 Credits

Built by **Abhijeet Kumar**. First presented at **Melbourne Python** — *"Beyond RAG: Building an Agentic Second Brain with FastAPI, pgvector, and Gemini."*

> *"RAG thinks when you ask. NeuralFortress thinks when you write — and decides how to search when you ask."*

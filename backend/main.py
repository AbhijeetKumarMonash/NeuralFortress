import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai
from google.genai import types # Added to configure the embedding size
import numpy as np
import knowledge_graph as kg

from database import engine, Base, get_db , SessionLocal
import models
import re 

import asyncio
import hashlib
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
# 1. Load Environment Variables
load_dotenv()

# 2. Initialize the Database Tables
Base.metadata.create_all(bind=engine)

# 3. Initialize the FastAPI Application
app = FastAPI(
    title="NeuralFortress API",
    description="The Backend for the NeuralFortress System",
    version="1.0.0"
)

# 4. Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Initialize the Gemini AI Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("CRITICAL ERROR: GEMINI_API_KEY is missing from the .env file")
client = genai.Client(api_key=GEMINI_API_KEY)

# 6. Define the Expected Data Structure
class IngestRequest(BaseModel):
    text: str
    source: str = "manual_input"

class SearchRequest(BaseModel):
    query: str

# 7. Root Route
@app.get("/")
async def root():
    return {"message": "NeuralFortress API is online. Go to /docs to view the dashboard."}

# 8. System Status Route 
@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "message": "Neural Core Initialized and Running"
    }

# ----------------- Async Watchers config + helpers -----------------
WATCH_INTERVAL_SECONDS = 60       # poll cadence; 60s for demo, raise to ~900 in production
WATCHER_MIN_CHARS = 200            # ignore fetches that returned almost nothing
WATCHER_MAX_CHARS = 12000          # cap per-fetch text (chunking handles the rest at ingest)



async def fetch_url_text(url: str) -> str:
    """Fetch a URL and return cleaned visible text.
    Wikipedia article URLs are routed through the official REST summary API
    (no scraping, no 403). Everything else is fetched and stripped with BeautifulSoup."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # --- Wikipedia: use the sanctioned REST API instead of scraping the HTML ---
    m = re.match(r"https?://(\w+)\.wikipedia\.org/wiki/(.+)", url)
    if m:
        lang, title = m.group(1), m.group(2)
        api = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
        async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as c:
            r = await c.get(api)
            r.raise_for_status()
            data = r.json()
        extract = data.get("extract", "")
        desc = data.get("description", "")
        title_clean = data.get("title", title.replace("_", " "))
        return f"{title_clean}. {desc}. {extract}"[:WATCHER_MAX_CHARS]

    # --- everything else: fetch + strip ---
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as c:
        r = await c.get(url)
        r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return text[:WATCHER_MAX_CHARS]


# ----------------- Watcher polling engine -----------------
async def poll_one_source(src, db: Session) -> dict:
    """Fetch one source; ingest only if the content changed since last time."""
    print(f"[WATCHER] polling {src.url}")
    src_id = src.id
    try:
        text = await fetch_url_text(src.url)
        if len(text) < WATCHER_MIN_CHARS:
            src.last_status = f"error: only {len(text)} chars fetched"
            src.last_checked = datetime.now(timezone.utc)
            db.commit()
            return {"watcher_id": src_id, "status": src.last_status}

        h = hashlib.sha256(text.encode()).hexdigest()
        if h == src.last_hash:
            src.last_status = "unchanged"
            src.last_checked = datetime.now(timezone.utc)
            db.commit()
            return {"watcher_id": src_id, "status": "unchanged"}

        # content changed -> run the FULL pipeline (chunk·synthesize·graph-extract)
        result = await perform_ingest(text, source=f"watcher:{src.url}", db=db)

        # perform_ingest committed; re-fetch src to update its status fields safely
        src = db.query(models.WatchedSource).filter(models.WatchedSource.id == src_id).first()
        src.last_hash = h
        src.last_status = f"ok: doc {result['document_id']}"
        src.last_checked = datetime.now(timezone.utc)
        db.commit()
        print(f"[WATCHER] ingested {src.url} -> doc {result['document_id']}")
        return {"watcher_id": src_id, "status": "ingested",
                "document_id": result["document_id"], "insight": result["insight"]}

    except Exception as e:
        db.rollback()
        try:
            src = db.query(models.WatchedSource).filter(models.WatchedSource.id == src_id).first()
            if src:
                src.last_status = f"error: {str(e)[:120]}"
                src.last_checked = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            pass
        print(f"[WATCHER ERROR] {src_id}: {repr(e)}")
        return {"watcher_id": src_id, "status": f"error: {e}"}
    
async def watcher_loop():
    """Runs forever; every WATCH_INTERVAL_SECONDS it polls all active watchers."""
    print(f"[WATCHER] loop started, interval={WATCH_INTERVAL_SECONDS}s")
    while True:
        try:
            db = SessionLocal()
            sources = db.query(models.WatchedSource).filter(
                models.WatchedSource.active == 1
            ).all()
            for src in sources:
                await poll_one_source(src, db)
            db.close()
        except Exception as e:
            print(f"[WATCHER LOOP ERROR] {repr(e)}")
        await asyncio.sleep(WATCH_INTERVAL_SECONDS)


@app.on_event("startup")
async def start_watchers():
    asyncio.create_task(watcher_loop())

async def perform_ingest(raw_text: str, source: str, db: Session) -> dict:
    """Core ingestion logic — chunk, embed, summarize, synthesize, graph-extract.
    Used by both /api/ingest and the watcher loop."""
    chunks = kg.chunk_text(raw_text, max_chars=MAX_EMBED_CHARS, overlap_chars=200)
    if not chunks:
        raise HTTPException(status_code=400, detail="Empty text")

    chunk_vectors = kg.embed_texts(client, chunks)
    doc_vector = np.mean(np.array(chunk_vectors, dtype=float), axis=0).tolist()

    summary_prompt = (
        "Analyze the following text. Provide a 2-sentence summary and extract 3-5 tags. "
        "Format EXACTLY as:\nSummary: [text]\nTags: [tag1, tag2, tag3]\n\n"
        f"Text: {raw_text[:12000]}"
    )
    ai_summary = client.models.generate_content(
        model='gemini-2.5-flash', contents=summary_prompt
    ).text

    related = db.query(models.Document).order_by(
        models.Document.embedding.cosine_distance(doc_vector)
    ).limit(3).all()
    if related:
        ctx = "\n\n---\n\n".join(d.content[:2000] for d in related)
        synthesis_prompt = (
            "You are the synthesis engine of a second brain. A new note is being ingested. "
            "Compare it to the related memories below. In ONE concise sentence, state the most "
            "interesting connection, overlap, or contradiction. Start with a verb.\n\n"
            f"EXISTING MEMORIES:\n{ctx}\n\nNEW NOTE:\n{raw_text[:4000]}"
        )
        insight = client.models.generate_content(
            model='gemini-2.5-flash', contents=synthesis_prompt
        ).text.strip()
    else:
        insight = "New neural pathway created. No prior related memories found."

    new_document = models.Document(
        content=(f"RAW_TEXT:\n{raw_text}\n\n"
                 f"AI_ANALYSIS:\n{ai_summary}\n\n"
                 f"SYNTHESIS_INSIGHT:\n{insight}"),
        source=source,
        embedding=doc_vector,
    )
    db.add(new_document)
    db.flush()

    for i, (c_text, c_vec) in enumerate(zip(chunks, chunk_vectors)):
        db.add(models.DocumentChunk(
            document_id=new_document.id, chunk_index=i, content=c_text, embedding=c_vec
        ))

    ents_n, rels_n = 0, 0
    try:
        triples = kg.extract_triples(client, raw_text)
        ents_n, rels_n = kg.store_triples(db, models, triples, new_document.id)
    except Exception as ge:
        print(f"[GRAPH INGEST WARN] {repr(ge)}")

    db.commit()
    db.refresh(new_document)

    return {
        "status": "success",
        "message": "Data successfully ingested and stored.",
        "document_id": new_document.id,
        "insight": insight,
        "chunks": len(chunks),
        "entities_extracted": ents_n,
        "relationships_extracted": rels_n,
    }

# 9. The Data Ingestion Route (now with Agentic Synthesis)
MAX_EMBED_CHARS = 1800  # safe per-chunk size, well under the ~2,048-token limit


async def perform_ingest(raw_text: str, source: str | None, db: Session) -> dict:
    """Core ingestion logic — chunk, embed, summarize, synthesize, graph-extract.
    Used by both /api/ingest and the async watcher loop.

    Caller is responsible for handling exceptions and rolling back if needed.
    """
    # A: chunk (1 chunk for short notes -> identical to old behaviour)
    chunks = kg.chunk_text(raw_text, max_chars=MAX_EMBED_CHARS, overlap_chars=200)
    if not chunks:
        raise HTTPException(status_code=400, detail="Empty text")

    # B: embed each chunk, then document vector = mean of chunk vectors
    chunk_vectors = kg.embed_texts(client, chunks)
    doc_vector = np.mean(np.array(chunk_vectors, dtype=float), axis=0).tolist()

    # C: summary + tags (format must stay EXACT for the Vue parser)
    summary_prompt = (
        "Analyze the following text. Provide a 2-sentence summary and extract 3-5 tags. "
        "Format EXACTLY as:\nSummary: [text]\nTags: [tag1, tag2, tag3]\n\n"
        f"Text: {raw_text[:12000]}"
    )
    ai_summary = client.models.generate_content(
        model='gemini-2.5-flash', contents=summary_prompt
    ).text

    # D: synthesis-on-ingest (unchanged) using the document vector
    related = db.query(models.Document).order_by(
        models.Document.embedding.cosine_distance(doc_vector)
    ).limit(3).all()
    if related:
        ctx = "\n\n---\n\n".join(d.content[:2000] for d in related)
        synthesis_prompt = (
            "You are the synthesis engine of a second brain. A new note is being ingested. "
            "Compare it to the related memories below. In ONE concise sentence, state the most "
            "interesting connection, overlap, or contradiction. Start with a verb.\n\n"
            f"EXISTING MEMORIES:\n{ctx}\n\nNEW NOTE:\n{raw_text[:4000]}"
        )
        insight = client.models.generate_content(
            model='gemini-2.5-flash', contents=synthesis_prompt
        ).text.strip()
    else:
        insight = "New neural pathway created. No prior related memories found."

    # E: persist the document (same content format as before)
    new_document = models.Document(
        content=(f"RAW_TEXT:\n{raw_text}\n\n"
                 f"AI_ANALYSIS:\n{ai_summary}\n\n"
                 f"SYNTHESIS_INSIGHT:\n{insight}"),
        source=source,
        embedding=doc_vector,
    )
    db.add(new_document)
    db.flush()  # get new_document.id

    # F: persist chunks
    for i, (c_text, c_vec) in enumerate(zip(chunks, chunk_vectors)):
        db.add(models.DocumentChunk(
            document_id=new_document.id, chunk_index=i, content=c_text, embedding=c_vec
        ))

    # G: GraphRAG extraction (entities + relationships). Never break ingest on failure.
    ents_n, rels_n = 0, 0
    try:
        triples = kg.extract_triples(client, raw_text)
        ents_n, rels_n = kg.store_triples(db, models, triples, new_document.id)
    except Exception as ge:
        print(f"[GRAPH INGEST WARN] {repr(ge)}")

    db.commit()
    db.refresh(new_document)

    return {
        "status": "success",
        "message": "Data successfully ingested and stored.",
        "document_id": new_document.id,
        "insight": insight,
        "chunks": len(chunks),
        "entities_extracted": ents_n,
        "relationships_extracted": rels_n,
    }


@app.post("/api/ingest")
async def ingest_data(payload: IngestRequest, db: Session = Depends(get_db)):
    try:
        return await perform_ingest(payload.text, payload.source, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[INGEST ERROR] {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 11. The Memory Browser (Fetch all notes)
@app.get("/api/documents")
async def get_documents(db: Session = Depends(get_db)):
    try:
        # We fetch the ID, content, and creation date, explicitly LEAVING OUT the heavy 'embedding' column
        docs = db.query(
            models.Document.id, 
            models.Document.content, 
            models.Document.source, 
            models.Document.created_at
        ).order_by(models.Document.created_at.desc()).all()

        # Format the data cleanly for the Vue frontend
        formatted_docs = []
        for doc in docs:
            formatted_docs.append({
                "id": doc.id,
                "content": doc.content,
                "source": doc.source,
                "created_at": doc.created_at
            })

        return {
            "status": "success",
            "count": len(formatted_docs),
            "documents": formatted_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 12. The Neural Map (knowledge graph of semantic links)
@app.get("/api/graph")
async def get_graph(threshold: float = 0.55, db: Session = Depends(get_db)):
    try:
        docs = [d for d in db.query(models.Document).all() if d.embedding is not None]
        nodes, vectors = [], []
        for d in docs:
            label = f"DOC_{d.id}"
            if d.content and "Summary:" in d.content:
                label = d.content.split("Summary:")[1].split("\n")[0].strip()[:40]
            elif d.content:
                label = d.content.replace("RAW_TEXT:\n", "")[:40]
            nodes.append({"id": d.id, "label": label})
            vectors.append(d.embedding)

        edges = []
        if len(vectors) > 1:
            M = np.array(vectors, dtype=float)
            norms = np.linalg.norm(M, axis=1, keepdims=True)
            norms[norms == 0] = 1e-9
            sim = (M / norms) @ (M / norms).T
            for i in range(len(docs)):
                for j in range(i + 1, len(docs)):
                    s = float(sim[i, j])
                    if s >= threshold:
                        edges.append({"from": docs[i].id, "to": docs[j].id, "value": round(s, 3)})

        return {"nodes": nodes, "edges": edges, "threshold": threshold}
    except Exception as e:
        print(f"[GRAPH ERROR] {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 10. The Retrieval Agent (Chatting with your data)
@app.post("/api/search")
async def search_data(payload: SearchRequest, db: Session = Depends(get_db)):
    try:
        user_question = payload.query
        
        # Step A: Convert the user's question into math (a vector)
        # We must use the exact same model and size (1536) as we did for saving
        question_embedding_response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=user_question,
            config=types.EmbedContentConfig(output_dimensionality=1536)
        )
        question_vector = question_embedding_response.embeddings[0].values

        # Step B: Search the Neon database for the closest matching notes
        # It compares the math of the question to the math of the saved notes
        similar_docs = db.query(models.Document).order_by(
            models.Document.embedding.cosine_distance(question_vector)
        ).limit(3).all()

        if not similar_docs:
            return {"answer": "I don't have any notes on this topic yet."}

        # Step C: Combine the found notes into one big text block
        context_text = "\n\n---\n\n".join([doc.content for doc in similar_docs])

        # Step D: Ask Gemini to answer the question using ONLY those notes
        prompt = f"""You are the AI brain of NeuralFortress. 
        Answer the user's question using ONLY the context provided below. 
        If the answer is not in the context, say "I cannot find this in your notes."
        
        Context from notes:
        {context_text}
        
        User Question: {user_question}
        """
        
        answer_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )

        return {
            "status": "success",
            "question": user_question,
            "answer": answer_response.text,
            "sources_used": len(similar_docs)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 13. Delete a memory
@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: int, db: Session = Depends(get_db)):
    try:
        doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        db.delete(doc)
        db.commit()
        return {"status": "success", "deleted_id": doc_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[DELETE ERROR] {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    #agent feature to delete memories that are no longer relevant or were added by mistake. 
@app.post("/api/agent")
async def agent_query(payload: SearchRequest, db: Session = Depends(get_db)):
    try:
        def search_notes(query: str) -> str:
            """Search the knowledge base for notes related to `query`. Returns the most relevant note contents."""
            print(f"[AGENT TOOL] search_notes({query!r})")
            qvec = client.models.embed_content(
                model="gemini-embedding-001", contents=query,
                config=types.EmbedContentConfig(output_dimensionality=1536)
            ).embeddings[0].values
            hits = db.query(models.Document).order_by(
                models.Document.embedding.cosine_distance(qvec)).limit(3).all()
            return "\n\n---\n\n".join(h.content for h in hits) if hits else "NO_MATCHES"

        def list_topics() -> str:
            """List the topics/tags currently stored. Use to plan a multi-topic answer or answer 'what do I know about?'."""
            print("[AGENT TOOL] list_topics()")
            tags = set()
            for (content,) in db.query(models.Document.content).all():
                if content and "Tags:" in content:
                    seg = content.split("Tags:")[1].split("]")[0].replace("[", "")
                    tags.update(t.strip() for t in seg.split(",") if t.strip())
            return ", ".join(sorted(tags)) or "No topics yet."

        system = ("You are the agentic brain of NeuralFortress. You have tools to search notes and list "
                  "topics. Decide which to call, call them as many times as needed (reformulate if a search "
                  "is weak), then answer ONLY from retrieved notes. If nothing relevant, say "
                  "'I cannot find this in your notes.'")

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{system}\n\nUser question: {payload.query}",
            config=types.GenerateContentConfig(tools=[search_notes, list_topics]),
        )

        steps = []
        try:
            for c in (getattr(response, "automatic_function_calling_history", None) or []):
                for p in (getattr(c, "parts", []) or []):
                    fc = getattr(p, "function_call", None)
                    if fc: steps.append(fc.name)
        except Exception:
            pass

        return {"status": "success", "question": payload.query,
                "answer": response.text, "agent_steps": steps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/graphrag")
async def graphrag_query(payload: SearchRequest, db: Session = Depends(get_db)):
    try:
        # 1) seed entities from the question
        names = kg.extract_query_entities(client, payload.query)
        seed_ids = []
        for n in names:
            norm = " ".join(n.strip().lower().split())
            ent = db.query(models.Entity).filter(models.Entity.norm_name == norm).first()
            if ent:
                seed_ids.append(ent.id)

        # 2) fallback: vector-search entry documents -> their entities
        if not seed_ids:
            qvec = client.models.embed_content(
                model="gemini-embedding-001", contents=payload.query,
                config=types.EmbedContentConfig(output_dimensionality=1536)
            ).embeddings[0].values
            top_docs = db.query(models.Document).order_by(
                models.Document.embedding.cosine_distance(qvec)).limit(3).all()
            doc_ids = [d.id for d in top_docs]
            if doc_ids:
                for r in db.query(models.Relationship).filter(
                        models.Relationship.document_id.in_(doc_ids)).limit(20).all():
                    seed_ids.extend([r.source_id, r.target_id])
            seed_ids = list(set(seed_ids))

        if not seed_ids:
            return {"answer": "No entities for this query yet — ingest more documents.",
                    "reasoning_path": [], "entities": [], "hops": 0, "source_documents": []}

        # 3) multi-hop traversal
        rels, entity_ids = kg.multi_hop_subgraph(db, models, seed_ids, max_hops=2)

        # 4) resolve names + supporting documents
        ent_map = {e.id: e for e in db.query(models.Entity).filter(
            models.Entity.id.in_(entity_ids)).all()}
        path, doc_ids = [], set()
        for r in rels:
            s, o = ent_map.get(r.source_id), ent_map.get(r.target_id)
            if s and o:
                path.append({"from": s.name, "predicate": r.predicate, "to": o.name})
            if r.document_id:
                doc_ids.add(r.document_id)

        docs = db.query(models.Document).filter(models.Document.id.in_(doc_ids)).all() if doc_ids else []
        notes = "\n\n---\n\n".join(d.content[:1500] for d in docs)
        triples_text = "\n".join(f"- {p['from']} --{p['predicate']}--> {p['to']}" for p in path)

        # 5) answer by walking the path
        prompt = (
            "You are a GraphRAG engine. Answer the QUESTION using the KNOWLEDGE GRAPH PATH and "
            "SUPPORTING NOTES. When relevant, explain the answer by walking the connection path "
            "across multiple hops. If the path lacks the answer, say so plainly.\n\n"
            f"QUESTION: {payload.query}\n\nKNOWLEDGE GRAPH PATH:\n{triples_text}\n\nSUPPORTING NOTES:\n{notes}"
        )
        answer = client.models.generate_content(
            model='gemini-2.5-flash', contents=prompt).text

        return {
            "answer": answer,
            "reasoning_path": path[:25],
            "entities": [ent_map[i].name for i in entity_ids if i in ent_map][:30],
            "hops": 2,
            "source_documents": sorted(doc_ids),
        }
    except Exception as e:
        print(f"[GRAPHRAG ERROR] {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/knowledge-graph")
async def knowledge_graph_view(db: Session = Depends(get_db)):
    type_color = {"PERSON": "#FF007F", "ORG": "#FFB000", "TECHNOLOGY": "#00D2FF",
                  "CONCEPT": "#27E0A6", "PLACE": "#9B6BFF", "EVENT": "#FF6B6B", "OTHER": "#9AA2B8"}
    ents = db.query(models.Entity).all()
    rels = db.query(models.Relationship).all()
    nodes = [{"id": e.id, "label": e.name, "group": e.type,
              "color": type_color.get(e.type, "#9AA2B8")} for e in ents]
    seen, edges = set(), []
    for r in rels:
        key = (r.source_id, r.target_id, (r.predicate or "").lower())
        if key in seen:
            continue
        seen.add(key)
        edges.append({"from": r.source_id, "to": r.target_id, "label": r.predicate})
    return {"nodes": nodes, "edges": edges,
            "entity_count": len(nodes), "relationship_count": len(edges)}

# ----------------- Watcher CRUD endpoints -----------------
class WatcherCreate(BaseModel):
    url: str
    label: str | None = None


@app.post("/api/watchers")
async def add_watcher(payload: WatcherCreate, db: Session = Depends(get_db)):
    try:
        src = models.WatchedSource(
            url=payload.url,
            label=payload.label or payload.url[:40],
        )
        db.add(src); db.commit(); db.refresh(src)
        return {"id": src.id, "url": src.url, "label": src.label, "active": src.active}
    except Exception as e:
        db.rollback()
        print(f"[WATCHER ADD ERROR] {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/watchers")
async def list_watchers(db: Session = Depends(get_db)):
    rows = db.query(models.WatchedSource).order_by(models.WatchedSource.id.desc()).all()
    return {"watchers": [{
        "id": s.id,
        "url": s.url,
        "label": s.label,
        "last_checked": s.last_checked.isoformat() if s.last_checked else None,
        "last_status": s.last_status,
        "active": s.active,
    } for s in rows]}


@app.delete("/api/watchers/{wid}")
async def delete_watcher(wid: int, db: Session = Depends(get_db)):
    src = db.query(models.WatchedSource).filter(models.WatchedSource.id == wid).first()
    if not src:
        raise HTTPException(status_code=404, detail="Watcher not found")
    db.delete(src); db.commit()
    return {"status": "deleted", "id": wid}


@app.post("/api/watchers/{wid}/toggle")
async def toggle_watcher(wid: int, db: Session = Depends(get_db)):
    src = db.query(models.WatchedSource).filter(models.WatchedSource.id == wid).first()
    if not src:
        raise HTTPException(status_code=404, detail="Watcher not found")
    src.active = 0 if src.active else 1
    db.commit()
    return {"id": wid, "active": src.active}

@app.post("/api/watchers/{wid}/run")
async def run_watcher_now(wid: int, db: Session = Depends(get_db)):
    src = db.query(models.WatchedSource).filter(models.WatchedSource.id == wid).first()
    if not src:
        raise HTTPException(status_code=404, detail="Watcher not found")
    return await poll_one_source(src, db)
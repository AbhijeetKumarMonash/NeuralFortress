import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai
from google.genai import types # Added to configure the embedding size
import numpy as np

from database import engine, Base, get_db
import models

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
# 9. The Data Ingestion Route (now with Agentic Synthesis)
MAX_EMBED_CHARS = 6000  # gemini-embedding-001 input limit is ~2048 tokens

@app.post("/api/ingest")
async def ingest_data(payload: IngestRequest, db: Session = Depends(get_db)):
    try:
        raw_text = payload.text
        embed_text = raw_text[:MAX_EMBED_CHARS]  # FIX: prevents 500 on long pastes

        # A: Summary + tags (format must stay EXACT — the Vue parser depends on it)
        summary_prompt = (
            "Analyze the following text. Provide a 2-sentence summary and extract 3-5 tags. "
            "Format EXACTLY as:\nSummary: [text]\nTags: [tag1, tag2, tag3]\n\n"
            f"Text: {raw_text}"
        )
        ai_summary = client.models.generate_content(
            model='gemini-2.5-flash', contents=summary_prompt
        ).text

        # B: Embed the new note (truncated to stay under the model's input limit)
        vector_math = client.models.embed_content(
            model="gemini-embedding-001",
            contents=embed_text,
            config=types.EmbedContentConfig(output_dimensionality=1536)
        ).embeddings[0].values

        # C: AGENTIC SYNTHESIS — retrieve related memories, reason about the link
        related = db.query(models.Document).order_by(
            models.Document.embedding.cosine_distance(vector_math)
        ).limit(3).all()

        if related:
            context = "\n\n---\n\n".join(d.content[:2000] for d in related)
            synthesis_prompt = (
                "You are the synthesis engine of a second brain. A new note is being ingested. "
                "Compare it to the related existing memories below. In ONE concise sentence, state "
                "the most interesting connection, overlap, or contradiction. Start with a verb "
                "(e.g. 'Connects to...', 'Contradicts...', 'Extends...').\n\n"
                f"EXISTING MEMORIES:\n{context}\n\nNEW NOTE:\n{raw_text[:4000]}"
            )
            insight = client.models.generate_content(
                model='gemini-2.5-flash', contents=synthesis_prompt
            ).text.strip()
        else:
            insight = "New neural pathway created. No prior related memories found."

        # D: Persist — SYNTHESIS_INSIGHT block is what MatrixArchive.vue parses
        new_document = models.Document(
            content=(f"RAW_TEXT:\n{raw_text}\n\n"
                     f"AI_ANALYSIS:\n{ai_summary}\n\n"
                     f"SYNTHESIS_INSIGHT:\n{insight}"),
            source=payload.source,
            embedding=vector_math
        )
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        return {
            "status": "success",
            "message": "Data successfully ingested and stored.",
            "document_id": new_document.id,
            "insight": insight,  # IngestionEngine.vue already displays this
        }

    except Exception as e:
        db.rollback()
        print(f"[INGEST ERROR] {repr(e)}")  # always see the real error in terminal
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
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai
from google.genai import types # Added to configure the embedding size

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

# 9. The Data Ingestion Route
@app.post("/api/ingest")
async def ingest_data(payload: IngestRequest, db: Session = Depends(get_db)):
    try:
        raw_text = payload.text
        
        # Step A: Create a summary using the Gemini Flash model
        prompt = f"Analyze the following text. Provide a 2-sentence summary and extract 3-5 tags. Format as: 'Summary: [text]\nTags: [tag1, tag2]'.\n\nText: {raw_text}"
        
        summary_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        ai_summary = summary_response.text

        # Step B: Convert text to numbers using the new embedding model
        # We tell it to output 1536 dimensions so it matches our database
        embedding_response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=raw_text,
            config=types.EmbedContentConfig(output_dimensionality=1536)
        )
        vector_math = embedding_response.embeddings[0].values

        # Step C: Save everything to the database
        new_document = models.Document(
            content=f"RAW_TEXT:\n{raw_text}\n\nAI_ANALYSIS:\n{ai_summary}",
            source=payload.source,
            embedding=vector_math
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        return {
            "status": "success", 
            "message": "Data successfully ingested and stored.",
            "document_id": new_document.id
        }

    except Exception as e:
        db.rollback()
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
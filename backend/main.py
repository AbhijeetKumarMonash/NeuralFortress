from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#Initialize the NeuralFortress Core
app = FastAPI(
    title ="NeuralFortress API",
    description="The Agentic Backend for the NeuralFortress PKMS",
    version= "1.0.0"
)

#Configure CORS(Allows Vue frontend to communicate with the python backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#System Status Route 
@app.get("/api/status")
async def get_status():
    return {
        "status":"online",
        "message":"SYS.VIDYA Neural Core Initialized and Running"
    }

#Data Ingestion Route (Placeholder for AI Agent Data Ingestion)
@app.post("/api/ingest")
async def ingest_data(payload: dict):
    #The Ai Summarization and vectore embedding will happen here
    return {"status":"received","data_length": len(payload.get("text",""))}

@app.get("/")
async def root():
    return {"message": "NeuralFortress API is online. Go to /docs to view the dashboard."}
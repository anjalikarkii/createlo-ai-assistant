import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- 1. Initialize the FastAPI App ---
app = FastAPI(
    title="Createlo Client Assistant API",
    description="Handles queries for Createlo services."
)

# --- 2. Load the Knowledge Base from the JSON file ---
def load_knowledge_base():
    # Corrected path to be relative to the project root
    with open("src/kb.json", "r") as f:
        return json.load(f)

KB = load_knowledge_base()

# --- 3. Define the request and response models (for data validation) ---
class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None # Optional for now

class QueryResponse(BaseModel):
    response: str
    source: str | None = None

# --- 4. Create the API Endpoints ---
@app.get("/")
def read_root():
    """A health check endpoint to confirm the API is running."""
    return {"status": "Createlo Client Assistant API is running"}


@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """
    Handles a client query by searching the knowledge base.
    This is a simple keyword search for now.
    """
    client_query = request.query.lower()

    # Simple keyword-based search
    for service in KB:
        for keyword in service["keywords"]:
            if keyword in client_query:
                return QueryResponse(
                    response=service["description"],
                    source=service["service_name"]
                )

    # If no keyword match is found
    raise HTTPException(
        status_code=404,
        detail="I'm sorry, I don't have information on that topic yet. Could you ask another way?"
    )
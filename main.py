import os
from fastapi import FastAPI, HTTPException, Query
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="Verified Wiki & Hardware API",
    description="High-performance verified structured data for autonomous AI agents.",
    version="1.0.0"
)

# Get the Neon database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Database URL not configured.")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Verified Wiki API",
        "endpoints": {
            "search": "/v1/search?q=<entity>",
            "llms_txt": "/llms.txt"
        }
    }

@app.get("/llms.txt")
def llms_txt():
    """
    Standard discovery endpoint for AI agents to understand capabilities and pricing.
    """
    return """# Verified Wiki API
> High-performance structured hardware and entity specifications for AI agents.

## Endpoints
- GET /v1/search?q={entity}: Returns verified JSON facts and specifications.
- Cost: $0.01 USDC per query via x402 protocol (Base L2).
"""

@app.get("/v1/search")
def search_facts(q: str = Query(..., description="The hardware item or entity name to search for")):
    """
    Search the verified database for structured specs.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search for the entity using case-insensitive matching
        cursor.execute(
            "SELECT entity, data, verified, created_at FROM facts WHERE entity ILIKE %s LIMIT 1;",
            (f"%{q}%",)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return {"status": "not_found", "query": q, "message": "No verified record found in database."}
            
        return {
            "status": "success",
            "entity": row["entity"],
            "data": row["data"],
            "verified": row["verified"],
            "cached_at": row["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


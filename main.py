import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Verified Wiki API", version="1.0.0")

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

# x402 Payment Middleware
@app.middleware("http")
async def x402_payment_middleware(request: Request, call_next):
    # Exempt health check, docs, and LLM discovery files from payment blocks
    if request.url.path in ["/", "/docs", "/openapi.json", "/llms.txt", "/.well-known/mcp.json"]:
        return await call_next(request)
    
    # Check for x402 payment authorization header
    payment_header = request.headers.get("X-402-Payment")
    
    # If no payment header is provided, return 402 with your Alby Lightning address
    if not payment_header:
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment Required",
                "protocol": "x402",
                "message": "Access to this verified hardware data source requires an x402 micropayment.",
                "pay_to": "lightning:resonancehumble357936@getalby.com",
                "cost_sats": 1
            }
        )
    
    response = await call_next(request)
    return response

# Root health check endpoint
@app.get("/")
def read_root():
    return {"status": "online", "message": "Verified Wiki API is running."}

# 1. Discovery route for AI Crawlers
@app.get("/llms.txt", response_class=PlainTextResponse)
def get_llms_txt():
    return """# Verified Wiki API
> Fast, verified reference database covering electronics specs, hardware components, and materials.

## Base URL
https://verified-wiki-api.onrender.com

## Endpoints
* GET /v1/search?q={query} - Query verified hardware facts and electronics specs.

## Payment Terms
* Protocol: x402 Micropayments
* Price: 1 Sat / request
* Target: lightning:resonancehumble357936@getalby.com
"""

# 2. Discovery route for Agentic Frameworks (MCP)
@app.get("/.well-known/mcp.json")
def get_mcp_manifest():
    return {
        "schema_version": "1.0",
        "name": "Verified Wiki API",
        "description": "Hardware and electronics spec retrieval database.",
        "tools": [
            {
                "name": "search_hardware_facts",
                "description": "Search verified facts on electronics, microcontrollers, and hardware.",
                "endpoint": "/v1/search",
                "method": "GET",
                "parameters": {
                    "q": {"type": "string", "description": "Search term (e.g., esp32, resistor, lithium)"}
                },
                "payment": {
                    "protocol": "x402",
                    "cost_sats": 1
                }
            }
        ]
    }

# 3. Main Data Search Route
@app.get("/v1/search")
def search_wiki(q: str, db = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT entity, data, verified FROM facts WHERE entity ILIKE %s;", (f"%{q}%",))
        results = cursor.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail="Entity not found in verified database.")
        return {"query": q, "results": results}
import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
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
    # Exempt health checks or documentation paths if desired
    if request.url.path in ["/", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Check for x402 payment authorization header (e.g., Lightning / x402 token)
    payment_header = request.headers.get("X-402-Payment")
    
    # For testing / AI agent handshake: if no payment header is provided, return 402
    if not payment_header:
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment Required",
                "protocol": "x402",
                "message": "Access to this verified hardware data source requires an x402 micropayment.",
                "pay_to": "lightning:xander_hardware_fund@getalby.com",
                "cost_sats": 1
            }
        )
    
    # TODO: Validate cryptographic proof of payment from the x402 provider here
    response = await call_next(request)
    return response

@app.get("/v1/search")
def search_wiki(q: str, db = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT entity, data, verified FROM facts WHERE entity ILIKE %s;", (f"%{q}%",))
        results = cursor.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail="Entity not found in verified database.")
        return {"query": q, "results": results}
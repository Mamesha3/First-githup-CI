from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

## roters
from app.routers import (
    notes as notes_router
)

# Import your synchronous engine from your database config file
from app.db.sqlalchemy import engine

# 1. CONFIGURE LIFESPAN TO VERIFY DATABASE CONNECTION ON STARTUP
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP PHASE ---
    print("[STARTUP] Testing connection pool to PostgreSQL...")

    yield 
    # --- SHUTDOWN PHASE ---
    print("[SHUTDOWN] Cleaning up application context...")
    await engine.dispose()


# 2. INITIALIZE FASTAPI APP WITH THE LIFESPAN
app = FastAPI(lifespan=lifespan)


# 3. SET UP CORS MIDDLEWARE FOR YOUR NEXT.JS FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Matches your frontend local port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. BASIC ROOT CHECK ENDPOINT
@app.get("/")
def read_root():
    return {"status": "FastAPI is running and database connection is healthy"}

## include routers
app.include_router(notes_router.router)


# test only 
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1")

@app.post("/test-ollama")
def test_ollama(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    try:
        result = llm.invoke(query)
        return {"res": result.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    
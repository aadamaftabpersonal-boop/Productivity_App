from fastapi import FastAPI
from app.routers import auth, reviewer

app = FastAPI(title="Student Portal API", version="0.1.0")

app.include_router(auth.router)
app.include_router(reviewer.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
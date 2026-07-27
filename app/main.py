from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.routers import auth, reviewer, contests, weakness, dashboard, analytics, leaderboard
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from app.database import engine, Base, AsyncSessionLocal
from app.weakness.matcher import load_concept_index
from app.reviewer.rag_index import build_index


from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Build RAG knowledge index on startup
    build_index()
    # Ensure all tables exist on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE weakness_records ADD COLUMN IF NOT EXISTS stability_days FLOAT DEFAULT 1.0;"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS discord_webhook_url VARCHAR(500);"))
        await conn.execute(text("ALTER TABLE code_submissions ADD COLUMN IF NOT EXISTS user_predicted_complexity VARCHAR(50);"))
        await conn.execute(text("ALTER TABLE code_submissions ADD COLUMN IF NOT EXISTS confidence_level VARCHAR(50);"))

    # Seed taxonomy tags if empty
    async with AsyncSessionLocal() as session:
        await load_concept_index(session)
    yield




limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="CP Hub API", version="2.0.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reviewer.router)
app.include_router(contests.router)
app.include_router(weakness.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(leaderboard.router)




@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # consistent error shape across the app — makes frontend error handling simpler
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exc.errors(), "message": "Validation failed"},
    )



@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    # never leak raw SQLAlchemy internals to the client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Database error occurred"},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}
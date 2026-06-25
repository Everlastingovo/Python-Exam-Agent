from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db, seed_db
from app.db.session import SessionLocal
from app.routers import ai, auth, exams, submissions, topics


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Python Exam Agent",
    description="A beginner-friendly Python coding practice and feedback API.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router)
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(exams.router)
app.include_router(submissions.router)


@app.get("/")
def health_check() -> dict:
    return {"message": "Python Exam Agent API is running."}

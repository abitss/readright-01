from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from readright.assessment.routes import router as assessment_router
from readright.intelligence.routes import router as intelligence_router
from readright.persistence.database import Base, check_storage, engine
from readright.persistence.routes import router as learner_router
from readright.teacher_decision.routes import router as teacher_decision_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pilot bootstrap. Production migration tooling will replace create_all as the
    # schema evolves, but this remains deterministic for the current v1 tables.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ReadRight Engine",
    version="0.5.0",
    description="Scientific assessment, longitudinal learning intelligence, and teacher decision service.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    storage = check_storage()
    return {
        "status": "ok" if storage.ok else "degraded",
        "service": "readright-engine",
        "storage": {
            "ok": storage.ok,
            "backend": storage.backend,
            "persistent": storage.persistent,
            "persistent_required": storage.requirement_enabled,
        },
    }


@app.get("/ready")
def readiness() -> dict:
    storage = check_storage()
    if not storage.ok:
        raise HTTPException(status_code=503, detail="Storage connection is unavailable")
    if storage.requirement_enabled and not storage.persistent:
        raise HTTPException(status_code=503, detail="Persistent PostgreSQL storage is required but not configured")
    return {
        "status": "ready",
        "storage_backend": storage.backend,
        "persistent": storage.persistent,
    }


app.include_router(assessment_router, prefix="/assessments", tags=["assessments"])
app.include_router(intelligence_router, prefix="/intelligence", tags=["intervention-intelligence"])
app.include_router(learner_router, prefix="/learners", tags=["longitudinal-learner-state"])
app.include_router(teacher_decision_router, prefix="/teacher-decision", tags=["teacher-decision"])

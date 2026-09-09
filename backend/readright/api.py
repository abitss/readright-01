from contextlib import asynccontextmanager

from fastapi import FastAPI

from readright.assessment.routes import router as assessment_router
from readright.intelligence.routes import router as intelligence_router
from readright.persistence.database import Base, engine
from readright.persistence.routes import router as learner_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pilot bootstrap. Production should move schema evolution to migrations.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ReadRight Engine",
    version="0.3.0",
    description="Scientific assessment and longitudinal learning intelligence service.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "readright-engine"}


app.include_router(assessment_router, prefix="/assessments", tags=["assessments"])
app.include_router(intelligence_router, prefix="/intelligence", tags=["intervention-intelligence"])
app.include_router(learner_router, prefix="/learners", tags=["longitudinal-learner-state"])

from fastapi import FastAPI

from readright.assessment.routes import router as assessment_router

app = FastAPI(
    title="ReadRight Engine",
    version="0.1.0",
    description="Scientific assessment and learning intelligence service.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "readright-engine"}


app.include_router(assessment_router, prefix="/assessments", tags=["assessments"])

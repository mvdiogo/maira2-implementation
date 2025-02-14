import asyncio
import logging
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.model_loader import ModelLoader
from core.report_generator import ReportGenerator
from config import config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the application's startup and shutdown events.
    """
    model_loader = ModelLoader()
    await asyncio.to_thread(model_loader.load_model)
    report_generator = ReportGenerator(model_loader)
    report_generator.setup()
    app.state.report_generator = report_generator
    yield
    logger.info("Shutting down the model...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://localhost",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate_report/")
async def generate_report_endpoint(
    request: Request,
    frontal_url: str = Form(...),
    lateral_url: str = Form(...),
    indication: str = Form(...),
    comparison: str = Form(...),
    technique: str = Form(...)
):
    """
    API endpoint to generate a chest X-ray report.
    """
    report_generator: ReportGenerator = request.app.state.report_generator

    try:
        result = await report_generator.generate_report(
            frontal_url, lateral_url, indication, comparison, technique
        )
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        logger.error(f"Error in generate_report_endpoint: {exc}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {exc}")


@app.get("/test")
async def test_endpoint():
    """
    Test endpoint to check if the backend is reachable.
    """
    return {"message": "Backend is reachable!"}


@app.get("/")
async def read_root():
    """
    Root endpoint with basic API information.
    """
    return {
        "message": "Welcome to the MAIRA-2 CXR Report Generator API!",
        "usage": (
            "Send a POST request to /generate_report/ with form data: "
            "frontal_url, lateral_url, indication, comparison, and technique."
        )
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        workers=2
    )

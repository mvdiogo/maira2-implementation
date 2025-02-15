import sys
import pytest
from os import path
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from api import app
from fastapi import HTTPException
from PIL import Image

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), "..")))


FRONTAL_URL = "https://openi.nlm.nih.gov/imgs/512/145/145/CXR145_IM-0290-1001.png"
LATERAL_URL = "https://openi.nlm.nih.gov/imgs/512/145/145/CXR145_IM-0290-2001.png"

@pytest.fixture(autouse=True)
def mock_dependencies():
    """
    Patch the key dependencies so that the tests do not perform actual model loading,
    image downloading, or file I/O.
    """
    with patch("core.model_loader.ModelLoader") as mock_model_loader, \
         patch("core.report_generator.ReportGenerator") as mock_report_generator, \
         patch("core.image_utils.httpx.AsyncClient") as mock_async_client, \
         patch("core.report_generator.ImageUtils") as mock_image_utils:
        
        mock_loader_instance = MagicMock()
        mock_model_loader.return_value = mock_loader_instance

        mock_report_gen_instance = MagicMock()
        mock_report_gen_instance.load_result_from_file.return_value = None
        mock_report_gen_instance.generate_report = AsyncMock(return_value={
            "frontal_image": "frontal_base64",
            "lateral_image": "lateral_base64",
            "report": "Test report"
        })
        mock_report_generator.return_value = mock_report_gen_instance

        mock_image_utils.download_image_async = AsyncMock()
        mock_image_utils.image_to_base64 = MagicMock()

        mock_client_instance = MagicMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        yield {
            "model_loader": mock_model_loader,
            "report_generator": mock_report_gen_instance,
            "image_utils": mock_image_utils,
            "http_client": mock_client_instance,
        }

@pytest.fixture
def client(mock_dependencies):
    with TestClient(app) as client:
        client.app.state.report_generator = mock_dependencies["report_generator"]
        yield client

def test_test_endpoint(client):
    """Test the basic test endpoint."""
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is reachable!"}

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

@pytest.mark.asyncio
async def test_generate_report_valid(client, mock_dependencies):
    """Test successful report generation."""
    test_image = Image.new("RGB", (256, 256))
    mock_dependencies["image_utils"].download_image_async.side_effect = [test_image, test_image]
    mock_dependencies["image_utils"].image_to_base64.side_effect = ["frontal_base64", "lateral_base64"]

    form_data = {
        "frontal_url": FRONTAL_URL,
        "lateral_url": LATERAL_URL,
        "indication": "Cough",
        "comparison": "None",
        "technique": "Digital"
    }
    response = client.post("/generate_report", data=form_data)
    assert response.status_code == 200
    result = response.json()
    assert "frontal_image" in result
    assert "lateral_image" in result
    assert "report" in result
    assert "Test report" in result["report"]

@pytest.mark.asyncio
async def test_generate_report_invalid_image_url(client, mock_dependencies):
    """Test handling of invalid image URL."""
    mock_dependencies["report_generator"].generate_report.side_effect = HTTPException(
        status_code=400, detail="Invalid image URL"
    )
    form_data = {
        "frontal_url": "http://invalid.com/image.jpg",
        "lateral_url": "http://invalid.com/image.jpg",
        "indication": "Test",
        "comparison": "None",
        "technique": "Digital"
    }
    response = client.post("/generate_report", data=form_data)
    assert response.status_code == 400
    assert "Invalid image URL" in response.json()["detail"]

def test_generate_report_missing_form_data(client):
    """Test validation when form data is missing."""
    response = client.post("/generate_report", data={})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert len(errors) == 5

@pytest.mark.asyncio
async def test_generate_report_model_not_loaded(client, mock_dependencies):
    """Test error handling when the model is not loaded."""
    mock_dependencies["report_generator"].generate_report.side_effect = HTTPException(
        status_code=503, detail="Model not loaded"
    )
    form_data = {
        "frontal_url": FRONTAL_URL,
        "lateral_url": LATERAL_URL,
        "indication": "Test",
        "comparison": "None",
        "technique": "Digital"
    }
    response = client.post("/generate_report", data=form_data)
    assert response.status_code == 503
    assert "Model not loaded" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_report_cached_result(client, mock_dependencies):
    """Test returning a cached report result."""
    cached_result = {"report": "Cached report"}
    mock_dependencies["report_generator"].generate_report.side_effect = lambda *args, **kwargs: cached_result

    form_data = {
        "frontal_url": "http://cached.com/image.jpg",
        "lateral_url": "http://cached.com/image.jpg",
        "indication": "Cached",
        "comparison": "None",
        "technique": "Digital"
    }
    response = client.post("/generate_report", data=form_data)
    assert response.status_code == 200
    assert response.json() == cached_result

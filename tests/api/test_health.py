from fastapi.testclient import TestClient
from app.main import app

# Initialize the TestClient with our FastAPI app
client = TestClient(app)

def test_health_check_endpoint():
    """
    Test the /api/health endpoint.
    Verifies that the API routes correctly and returns the expected schema,
    even if underlying services like Redis are not reachable in the CI environment.
    """
    response = client.get("/api/health")
    
    # 1. Check HTTP Status
    assert response.status_code == 200
    
    # 2. Check Payload Structure
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "fastapi-backend"
    
    # Assert the key exists. It will be 'False' in CI (no Redis) and 'True' locally,
    # but the API contract guarantees the key must exist.
    assert "redis_connected" in data
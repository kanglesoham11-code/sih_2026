from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_system_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "system" in data
    assert "data_sources" in data
    assert "agents" in data
    assert data["agents_total"] == 10
    
    # Check that roadmap sources are not 'live'
    for src in data["data_sources"]:
        if src["kind"] == "roadmap":
            assert src["status"] == "planned"

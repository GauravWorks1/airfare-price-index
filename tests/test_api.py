import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_fares" in data

def test_routes_endpoint(client):
    response = client.get("/api/v1/fares/routes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "origin" in data[0]
    assert "destination" in data[0]

def test_index_daily_endpoint(client):
    response = client.get("/api/v1/index/daily?index_type=LASPEYRES")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data

def test_carriers_endpoint(client):
    response = client.get("/api/v1/carriers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "carrier" in data[0]
        assert "avg_fare" in data[0]

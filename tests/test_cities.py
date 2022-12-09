from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_companies():
    response = client.get("/companies")
    assert response.status_code == 200
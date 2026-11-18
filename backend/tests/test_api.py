from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_reports_dataset_version():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["records"] >= 4
    assert body["dataset_version"]


def test_list_schemes_is_read_only_and_cached():
    response = client.get("/v1/schemes")
    assert response.status_code == 200
    body = response.json()
    assert body["schemes"]
    assert response.headers["etag"]
    assert "nosniff" in response.headers["x-content-type-options"]

    cached = client.get("/v1/schemes", headers={"If-None-Match": response.headers["etag"]})
    assert cached.status_code == 304


def test_get_scheme_returns_citation_fields():
    response = client.get("/v1/schemes/adip")
    assert response.status_code == 200
    body = response.json()
    assert body["source_url"].startswith("http")
    assert body["last_verified"]
    assert body["eligibility"]["income_slabs"][0]["max_monthly_inr"] == 22500


def test_unknown_scheme_returns_404():
    response = client.get("/v1/schemes/does-not-exist")
    assert response.status_code == 404


def test_no_write_endpoints():
    assert client.post("/v1/schemes").status_code == 405
    assert client.delete("/v1/schemes/adip").status_code == 405


def test_category_filter():
    response = client.get("/v1/schemes?category=identity")
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["schemes"]]
    assert ids == ["udid"]

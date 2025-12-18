from fastapi.testclient import TestClient
from urllib.parse import quote
import uuid

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect known activity keys exist
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_duplicate_and_delete():
    activity = "Chess Club"
    # use a unique email to avoid collisions
    email = f"test-{uuid.uuid4().hex}@example.com"

    # signup should succeed
    resp1 = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp1.status_code == 200
    assert f"Signed up {email}" in resp1.json().get("message", "")

    # duplicate signup should fail with 400
    resp2 = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp2.status_code == 400

    # delete the participant
    resp3 = client.delete(f"/activities/{quote(activity)}/participants/{quote(email, safe='')}" )
    assert resp3.status_code == 200
    assert f"Removed {email}" in resp3.json().get("message", "")

    # deleting again should return 404
    resp4 = client.delete(f"/activities/{quote(activity)}/participants/{quote(email, safe='')}" )
    assert resp4.status_code == 404


def test_signup_nonexistent_activity():
    resp = client.post(f"/activities/{quote('No Such Activity')}/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_remove_participant_nonexistent_activity():
    resp = client.delete(f"/activities/{quote('No Such Activity')}/participants/{quote('a%40b.com', safe='')}" )
    assert resp.status_code == 404

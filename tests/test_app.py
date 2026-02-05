import importlib.util
import pathlib
from fastapi.testclient import TestClient

# Load the app from src/app.py by file path
ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "src" / "app.py"

spec = importlib.util.spec_from_file_location("app_module", str(APP_PATH))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = module.app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "test_student@example.com"

    # Ensure clean state: remove if already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        del_resp = client.delete(f"/activities/{activity}/participants?email={email}")
        assert del_resp.status_code == 200

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Confirm participant added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # Confirm removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]

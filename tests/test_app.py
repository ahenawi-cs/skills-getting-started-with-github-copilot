from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_state))


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    response = client.delete(
        "/activities/Chess%20Club/participants/michael@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"

    activity = client.get("/activities").json()["Chess Club"]
    assert "michael@mergington.edu" not in activity["participants"]


def test_unregister_unknown_participant_returns_not_found():
    response = client.delete(
        "/activities/Chess%20Club/participants/unknown@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_activities_endpoint_returns_fresh_data_after_signup():
    signup_response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )

    assert signup_response.status_code == 200

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    assert "newstudent@mergington.edu" in activities_response.json()["Chess Club"]["participants"]
    assert activities_response.headers["cache-control"] == "no-store"

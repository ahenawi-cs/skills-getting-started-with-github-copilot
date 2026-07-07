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
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{participant_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant_email} from {activity_name}"

    activity = client.get("/activities").json()[activity_name]
    assert participant_email not in activity["participants"]


def test_unregister_unknown_participant_returns_not_found():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "unknown@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{participant_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_activities_endpoint_returns_fresh_data_after_signup():
    # Arrange
    activity_name = "Chess Club"
    new_participant = "newstudent@mergington.edu"

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup?email={new_participant}")
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert activities_response.status_code == 200
    assert new_participant in activities_response.json()[activity_name]["participants"]
    assert activities_response.headers["cache-control"] == "no-store"

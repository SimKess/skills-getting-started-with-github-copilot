"""
Tests for the Mergington High School API

Uses the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Set up test data and initial state
- Act: Execute the code being tested
- Assert: Verify the results are as expected
"""

from fastapi.testclient import TestClient
from src.app import app
import pytest


@pytest.fixture
def client():
    """Fixture that provides a TestClient for the FastAPI app"""
    return TestClient(app)


# ===== GET /activities =====

def test_get_activities_returns_200(client):
    """Test that GET /activities returns a 200 status code"""
    # ARRANGE
    expected_status = 200

    # ACT
    response = client.get("/activities")

    # ASSERT
    assert response.status_code == expected_status


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all 9 activities"""
    # ARRANGE
    expected_count = 9

    # ACT
    response = client.get("/activities")
    data = response.json()

    # ASSERT
    assert len(data) == expected_count


def test_get_activities_contains_expected_activities(client):
    """Test that GET /activities contains specific activities"""
    # ARRANGE
    expected_activities = {"Chess Club", "Programming Class", "Gym Class"}

    # ACT
    response = client.get("/activities")
    data = response.json()

    # ASSERT
    for activity in expected_activities:
        assert activity in data


def test_get_activities_has_correct_structure(client):
    """Test that each activity has the required fields"""
    # ARRANGE
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # ACT
    response = client.get("/activities")
    data = response.json()

    # ASSERT
    for activity_name, activity_data in data.items():
        assert isinstance(activity_name, str)
        assert isinstance(activity_data, dict)
        for field in required_fields:
            assert field in activity_data, f"Field '{field}' missing in {activity_name}"


def test_get_activities_participants_is_list(client):
    """Test that participants field is a list"""
    # ARRANGE
    # ACT
    response = client.get("/activities")
    data = response.json()

    # ASSERT
    for activity_data in data.values():
        assert isinstance(activity_data["participants"], list)


# ===== GET / (Redirect) =====

def test_root_redirects_to_static_index(client):
    """Test that GET / redirects to /static/index.html"""
    # ARRANGE
    expected_url_part = "/static/index.html"
    expected_status_codes = {307, 308}

    # ACT
    response = client.get("/", follow_redirects=False)

    # ASSERT
    assert response.status_code in expected_status_codes
    assert expected_url_part in response.headers.get("location", "")


# ===== POST /activities/{activity_name}/signup =====

def test_signup_success_new_participant(client):
    """Test that a new participant can successfully sign up"""
    # ARRANGE
    activity = "Soccer Team"
    email = "newsignup@example.com"

    # ACT
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up" in data["message"]
    assert email in data["message"]
    assert activity in data["message"]


def test_signup_activity_not_found(client):
    """Test that signup returns 404 when activity doesn't exist"""
    # ARRANGE
    activity = "Nonexistent Activity"
    email = "student@example.com"
    expected_status = 404

    # ACT
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # ASSERT
    assert response.status_code == expected_status
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_registered(client):
    """Test that signup returns 400 when participant already registered"""
    # ARRANGE
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already registered in Chess Club
    expected_status = 400

    # ACT
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # ASSERT
    assert response.status_code == expected_status
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_adds_participant_to_activity(client):
    """Test that signup actually adds the participant to the activity"""
    # ARRANGE
    activity = "Basketball Club"
    email = "basketball_newbie@example.com"

    # ACT
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # ASSERT
    assert response.status_code == 200
    # Verify by fetching activities
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]


# ===== DELETE /activities/{activity_name}/unregister =====

def test_unregister_success(client):
    """Test that a participant can successfully unregister"""
    # ARRANGE
    activity = "Programming Class"
    email = "emma@mergington.edu"

    # ACT
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]
    assert email in data["message"]
    assert activity in data["message"]


def test_unregister_activity_not_found(client):
    """Test that unregister returns 404 when activity doesn't exist"""
    # ARRANGE
    activity = "Nonexistent Activity"
    email = "student@example.com"
    expected_status = 404

    # ACT
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # ASSERT
    assert response.status_code == expected_status
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_not_registered(client):
    """Test that unregister returns 400 when participant not registered"""
    # ARRANGE
    activity = "Programming Class"
    email = "notregistered@example.com"
    expected_status = 400

    # ACT
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # ASSERT
    assert response.status_code == expected_status
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_removes_participant_from_activity(client):
    """Test that unregister actually removes the participant from the activity"""
    # ARRANGE
    activity = "Gym Class"
    email = "john@mergington.edu"

    # ACT
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # ASSERT
    assert response.status_code == 200
    # Verify by fetching activities
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]

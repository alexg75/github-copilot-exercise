from urllib.parse import quote

from src.app import activities


def _activity_signup_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


def _activity_participants_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/participants"


def test_root_redirects_to_static_index(client):
    # Given
    root_path = "/"

    # When
    response = client.get(root_path, follow_redirects=False)

    # Then
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Given
    activities_path = "/activities"

    # When
    response = client.get(activities_path)

    # Then
    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == set(activities.keys())


def test_signup_for_activity_adds_new_student(client):
    # Given
    activity_name = "Debate Team"
    email = "new.student@mergington.edu"
    signup_path = _activity_signup_path(activity_name)

    # When
    response = client.post(signup_path, params={"email": email})

    # Then
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404(client):
    # Given
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"
    signup_path = _activity_signup_path(activity_name)

    # When
    response = client.post(signup_path, params={"email": email})

    # Then
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_duplicate_student_returns_400(client):
    # Given
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]
    signup_path = _activity_signup_path(activity_name)

    # When
    response = client.post(signup_path, params={"email": existing_email})

    # Then
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_student_from_activity(client):
    # Given
    activity_name = "Basketball Team"
    email = activities[activity_name]["participants"][0]
    participants_path = _activity_participants_path(activity_name)

    # When
    response = client.delete(participants_path, params={"email": email})

    # Then
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_unknown_activity_returns_404(client):
    # Given
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"
    participants_path = _activity_participants_path(activity_name)

    # When
    response = client.delete(participants_path, params={"email": email})

    # Then
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_non_participant_returns_404(client):
    # Given
    activity_name = "Art Studio"
    email = "not-enrolled@mergington.edu"
    participants_path = _activity_participants_path(activity_name)

    # When
    response = client.delete(participants_path, params={"email": email})

    # Then
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}

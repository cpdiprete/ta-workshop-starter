import pytest

import app as app_module


@pytest.fixture
def client(monkeypatch):
    """Provide a client with the default task state."""
    monkeypatch.setattr(
        app_module,
        "tasks",
        [
            {"id": 1, "title": "Project-1 Report"},
            {"id": 2, "title": "Project-2 MMFs"}
        ]
    )
    monkeypatch.setattr(app_module, "next_id", 3)
    return app_module.app.test_client()


@pytest.mark.parametrize("priority", ["Low", "Medium", "High"])
def test_explicit_priority_is_stored_and_returned(client, priority):
    """Store and return each supported explicit priority."""
    response = client.post(
        "/api/tasks",
        json={"title": "Priority task", "priority": priority}
    )

    assert response.status_code == 201
    assert response.get_json()["priority"] == priority

    tasks_response = client.get("/api/tasks")
    created_task = tasks_response.get_json()[-1]
    assert created_task["priority"] == priority


def test_missing_priority_defaults_to_medium(client):
    """Default a newly created task to Medium when priority is omitted."""
    response = client.post("/api/tasks", json={"title": "Default task"})

    assert response.status_code == 201
    assert response.get_json()["priority"] == "Medium"


def test_existing_task_without_priority_is_returned_as_medium(client):
    """Treat legacy tasks without priority as Medium in responses."""
    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert [task["priority"] for task in response.get_json()] == [
        "Medium",
        "Medium"
    ]


def test_initial_task_list_is_preserved(client):
    """Preserve the initial task IDs and titles."""
    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "title": "Project-1 Report",
            "priority": "Medium"
        },
        {
            "id": 2,
            "title": "Project-2 MMFs",
            "priority": "Medium"
        }
    ]


def test_missing_title_returns_bad_request(client):
    """Reject task creation when the title is missing."""
    response = client.post("/api/tasks", json={"priority": "High"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Title is required"


def test_delete_task_preserves_existing_behavior(client):
    """Delete the requested task and return a success response."""
    response = client.delete("/api/tasks/1")

    assert response.status_code == 200
    assert response.get_json() == {"result": "success"}
    assert [task["id"] for task in client.get("/api/tasks").get_json()] == [2]


@pytest.mark.parametrize("priority", [["High"], {"priority": "High"}, None])
def test_invalid_priority_returns_bad_request(client, priority):
    """Reject invalid priority values without raising a server error."""
    response = client.post(
        "/api/tasks",
        json={"title": "Invalid priority task", "priority": priority}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Priority must be Low, Medium, or High"
    )

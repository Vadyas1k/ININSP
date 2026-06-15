import pytest
import json
from app import app


@pytest.fixture
def client():
    """Test client для Flask"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_create_note(client):
    """Тест создания заметки через API"""
    response = client.post(
        "/api/notes",
        data=json.dumps({"session_id": "test1", "title": "New Note"}),
        content_type="application/json",
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert "id" in data
    assert data["status"] == "created"


def test_get_notes_list(client):
    """Тест получения списка заметок"""
    # Сначала создадим заметку
    client.post(
        "/api/notes",
        data=json.dumps({"session_id": "test2", "title": "Note 1"}),
        content_type="application/json",
    )

    response = client.get("/api/notes?session_id=test2")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 1


def test_load_specific_note(client):
    """Тест загрузки конкретной заметки"""
    # Создаём
    create_resp = client.post(
        "/api/notes",
        data=json.dumps({"session_id": "test3", "title": "Note Title"}),
        content_type="application/json",
    )
    note_id = json.loads(create_resp.data)["id"]

    # Загружаем
    response = client.get(f"/api/notes/{note_id}?session_id=test3")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["title"] == "Note Title"


def test_update_note(client):
    """Тест обновления заметки"""
    # Создаём
    create_resp = client.post(
        "/api/notes",
        data=json.dumps({"session_id": "test4", "title": "Old Title"}),
        content_type="application/json",
    )
    note_id = json.loads(create_resp.data)["id"]

    # Обновляем
    response = client.put(
        f"/api/notes/{note_id}",
        data=json.dumps(
            {"session_id": "test4", "title": "New Title", "content": "New Content"}
        ),
        content_type="application/json",
    )

    assert response.status_code == 200

    # Проверяем
    get_resp = client.get(f"/api/notes/{note_id}?session_id=test4")
    data = json.loads(get_resp.data)
    assert data["title"] == "New Title"
    assert data["content"] == "New Content"


def test_delete_note(client):
    """Тест удаления заметки"""
    # Создаём
    create_resp = client.post(
        "/api/notes",
        data=json.dumps({"session_id": "test5", "title": "To Delete"}),
        content_type="application/json",
    )
    note_id = json.loads(create_resp.data)["id"]

    # Удаляем
    response = client.delete(
        f"/api/notes/{note_id}",
        data=json.dumps({"session_id": "test5"}),
        content_type="application/json",
    )
    assert response.status_code == 200

    # Проверяем, что удалена
    get_resp = client.get(f"/api/notes/{note_id}?session_id=test5")
    assert get_resp.status_code == 404


def test_validation_error(client):
    """Тест валидации (отсутствие session_id)"""
    response = client.post(
        "/api/notes",
        data=json.dumps({"title": "No Session"}),
        content_type="application/json",
    )

    assert response.status_code == 400

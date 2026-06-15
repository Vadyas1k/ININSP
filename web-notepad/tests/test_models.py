import pytest
import os
from models import init_db, get_note, save_note, clear_note, get_connection

# Тестовая БД
TEST_DB = "test_notes.db"


@pytest.fixture
def setup_db():
    """Инициализация тестовой БД"""
    os.environ["DB_PATH"] = TEST_DB
    init_db()
    yield
    # Очистка после теста
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_create_and_get_note(setup_db):
    """Тест создания и получения заметки"""
    session_id = "test_session_1"
    content = "Test content"

    save_note(session_id, content)
    result = get_note(session_id)

    assert result == content


def test_update_note(setup_db):
    """Тест обновления заметки"""
    session_id = "test_session_2"

    save_note(session_id, "First content")
    save_note(session_id, "Updated content")

    result = get_note(session_id)
    assert result == "Updated content"


def test_clear_note(setup_db):
    """Тест очистки заметки"""
    session_id = "test_session_3"

    save_note(session_id, "To be deleted")
    clear_note(session_id)

    result = get_note(session_id)
    assert result == ""


def test_multiple_sessions(setup_db):
    """Тест изоляции сессий"""
    save_note("session_a", "Content A")
    save_note("session_b", "Content B")

    assert get_note("session_a") == "Content A"
    assert get_note("session_b") == "Content B"

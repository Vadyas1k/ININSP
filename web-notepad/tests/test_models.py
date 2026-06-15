import pytest
import os
import models

TEST_DB = "test_notes.db"


@pytest.fixture
def setup_db():
    """Инициализация тестовой БД с переопределением пути"""
    models.DB_PATH = TEST_DB
    models.init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_create_and_get_note(setup_db):
    session_id = "test_session_1"
    note_id = models.create_note(session_id, title="Test Title")
    result = models.get_note(session_id, note_id)
    assert result is not None
    assert result["title"] == "Test Title"


def test_update_note(setup_db):
    session_id = "test_session_2"
    note_id = models.create_note(session_id, title="Old Title")
    models.update_note(session_id, note_id, title="New Title", content="New Content")
    result = models.get_note(session_id, note_id)
    assert result["title"] == "New Title"
    assert result["content"] == "New Content"


def test_delete_note(setup_db):
    session_id = "test_session_3"
    note_id = models.create_note(session_id, title="To Delete")
    models.delete_note(session_id, note_id)
    result = models.get_note(session_id, note_id)
    assert result is None


def test_multiple_sessions(setup_db):
    note_a = models.create_note("session_a", title="Note A")
    note_b = models.create_note("session_b", title="Note B")
    data_a = models.get_note("session_a", note_a)
    data_b = models.get_note("session_b", note_b)
    assert data_a["title"] == "Note A"
    assert data_b["title"] == "Note B"

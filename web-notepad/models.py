import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT 'Без названия',
            content TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_notes(session_id):
    conn = get_connection()
    rows = conn.execute(
        'SELECT id, title, content, updated_at FROM notes WHERE session_id = ? ORDER BY updated_at DESC',
        (session_id,)
    ).fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        # Конвертируем строку из БД в ISO-формат с явным указанием UTC
        if d['updated_at']:
            dt = datetime.fromisoformat(d['updated_at'].replace(' ', 'T') + '+00:00')
            d['updated_at'] = dt.isoformat()
        result.append(d)
    return result

def get_note(session_id, note_id):
    conn = get_connection()
    row = conn.execute(
        'SELECT * FROM notes WHERE id = ? AND session_id = ?', (note_id, session_id)
    ).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if d['updated_at']:
        dt = datetime.fromisoformat(d['updated_at'].replace(' ', 'T') + '+00:00')
        d['updated_at'] = dt.isoformat()
    return d
def create_note(session_id, title='Новая заметка'):
    conn = get_connection()
    cursor = conn.execute(
        'INSERT INTO notes (session_id, title) VALUES (?, ?)', (session_id, title)
    )
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return note_id

def update_note(session_id, note_id, title=None, content=None):
    conn = get_connection()
    if title is not None:
        conn.execute('UPDATE notes SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND session_id = ?', (title, note_id, session_id))
    if content is not None:
        conn.execute('UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND session_id = ?', (content, note_id, session_id))
    conn.commit()
    conn.close()

def delete_note(session_id, note_id):
    conn = get_connection()
    conn.execute('DELETE FROM notes WHERE id = ? AND session_id = ?', (note_id, session_id))
    conn.commit()
    conn.close()
    def clear_note(session_id):
        conn = get_connection()
        conn.execute('DELETE FROM notes WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()

document.addEventListener('DOMContentLoaded', () => {
    const notesListEl = document.getElementById('notes-list');
    const newNoteBtn = document.getElementById('new-note-btn');
    const titleInput = document.getElementById('note-title');
    const contentInput = document.getElementById('note-content');
    const deleteBtn = document.getElementById('delete-note-btn');
    const statusEl = document.getElementById('status');
    const charCountEl = document.getElementById('char-count');

    let sessionId = localStorage.getItem('notepad_session_id');
    if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).substring(2) + Date.now().toString(36);
        localStorage.setItem('notepad_session_id', sessionId);
    }

    let currentNoteId = null;
    const API = '/api/notes';

    function debounce(fn, delay) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), delay);
        };
    }

    function showStatus(text, isError = false) {
        statusEl.textContent = text;
        statusEl.style.color = isError ? '#e74c3c' : '#27ae60';
        if (!isError) setTimeout(() => statusEl.textContent = 'Готово', 1500);
    }

    function updateCharCount() {
        charCountEl.textContent = `${contentInput.value.length} символов`;
    }

    // Безопасный парсинг JSON (не падает на HTML-ошибках сервера)
    async function safeJson(response) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        const text = await response.text();
        throw new Error(`Сервер вернул ${response.status}: ${text.substring(0, 150)}`);
    }

    async function fetchNotes() {
        try {
            const res = await fetch(`${API}?session_id=${sessionId}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const notes = await safeJson(res);
            renderNotesList(notes);
            return notes;
        } catch (err) {
            console.error('Ошибка загрузки списка:', err);
            showStatus(err.message, true);
            return [];
        }
    }

    function renderNotesList(notes) {
        notesListEl.innerHTML = '';
        if (notes.length === 0) {
            notesListEl.innerHTML = '<li class="note-item" style="padding:1rem; color:#888; text-align:center; cursor:default;">Нет заметок. Создайте первую!</li>';
            return;
        }
        notes.forEach(note => {
            const li = document.createElement('li');
            li.className = `note-item ${note.id === currentNoteId ? 'active' : ''}`;
            const date = new Date(note.updated_at).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute:'2-digit' });
            li.innerHTML = `<div class="title">${note.title || 'Без названия'}</div><div class="meta">${date}</div>`;
            li.addEventListener('click', () => loadNote(note.id));
            notesListEl.appendChild(li);
        });
    }

    async function loadNote(id) {
        try {
            showStatus('Загрузка...');
            const res = await fetch(`${API}/${id}?session_id=${sessionId}`);
            if (!res.ok) throw new Error('Заметка не найдена');
            const note = await safeJson(res);
            currentNoteId = note.id;
            titleInput.value = note.title;
            contentInput.value = note.content;
            updateCharCount();
            document.querySelectorAll('.note-item').forEach(el => el.classList.remove('active'));
            const activeLi = document.querySelector(`.note-item:nth-child(${notes.indexOf(note) + 1})`);
            if (activeLi) activeLi.classList.add('active');
            showStatus('Загружено');
        } catch (err) {
            showStatus(err.message, true);
        }
    }

    async function createNote() {
        try {
            showStatus('Создание...');
            const res = await fetch(API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, title: 'Новая заметка' })
            });
            if (!res.ok) {
                const errData = await safeJson(res);
                throw new Error(errData.error || 'Ошибка сервера');
            }
            const data = await safeJson(res);
            await fetchNotes();
            loadNote(data.id);
            titleInput.focus();
            titleInput.select();
        } catch (err) {
            console.error('Ошибка создания:', err);
            showStatus(err.message, true);
        }
    }

    async function updateCurrentNote() {
        if (!currentNoteId) return;
        try {
            const res = await fetch(`${API}/${currentNoteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, title: titleInput.value, content: contentInput.value })
            });
            if (!res.ok) throw new Error('Ошибка сохранения');
            showStatus('Сохранено');
        } catch (err) {
            showStatus(err.message, true);
        }
    }

    async function deleteCurrentNote() {
        if (!currentNoteId) return;
        if (!confirm('Удалить эту заметку? Действие нельзя отменить.')) return;
        try {
            showStatus('Удаление...');
            const res = await fetch(`${API}/${currentNoteId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            if (!res.ok) throw new Error('Ошибка удаления');
            currentNoteId = null;
            titleInput.value = '';
            contentInput.value = '';
            updateCharCount();
            await fetchNotes();
            showStatus('Удалено');
        } catch (err) {
            showStatus(err.message, true);
        }
    }

    newNoteBtn.addEventListener('click', createNote);
    deleteBtn.addEventListener('click', deleteCurrentNote);
    contentInput.addEventListener('input', updateCharCount);

    const autoSave = debounce(() => {
        if (currentNoteId) updateCurrentNote();
    }, 600);

    titleInput.addEventListener('input', autoSave);
    contentInput.addEventListener('input', autoSave);

    // Инициализация
    fetchNotes().then(notes => {
        if (notes.length > 0) loadNote(notes[0].id);
    });
});

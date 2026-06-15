🚀 Запуск Web-Notepad
📋 Требования

    Python 3.10+
    pip (входит в стандартную установку Python)

▶️ Установка и запуск

    Установите зависимости: pip install -r requirements.txt
    Запустите сервер: python app.py

🌐 Доступ
Откройте в браузере: http://localhost:5000
💾 Примечания

    Файл notes.db создаётся автоматически при первом запуске.
    Для полного сброса заметок удалите notes.db и перезапустите сервер.
    Сессия привязана к браузеру. Регистрация не требуется.
    Текст сохраняется автоматически при вводе.
## 🐳 Docker
```bash
# Сборка
docker build -t web-notepad .

# Запуск
docker run -d -p 5000:5000 --name notepad web-notepad

# Остановка
docker stop notepad && docker rm notepad

## 🔒 Безопасность

### Статический анализ
```bash
# Проверка кода на уязвимости
bandit -r . -f custom

# Проверка зависимостей
safety check

# Расширенный анализ
semgrep --config auto .
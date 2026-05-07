from flask import Flask, render_template, request, jsonify
from models import init_db, get_notes, get_note, create_note, update_note, delete_note

app = Flask(__name__)

with app.app_context():
    init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/notes", methods=["GET"])
def list_notes():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Отсутствует session_id"}), 400
    return jsonify(get_notes(session_id))


@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    if not data or "session_id" not in data:
        return jsonify({"error": "Отсутствует session_id"}), 400
    note_id = create_note(data["session_id"], data.get("title", "Без названия"))
    return jsonify({"id": note_id, "status": "created"}), 201


@app.route("/api/notes/<int:note_id>", methods=["GET"])
def load_note(note_id):
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Отсутствует session_id"}), 400
    note = get_note(session_id, note_id)
    if not note:
        return jsonify({"error": "Заметка не найдена"}), 404
    return jsonify(note)


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def save_note(note_id):
    data = request.get_json()
    if not data or "session_id" not in data:
        return jsonify({"error": "Отсутствует session_id"}), 400
    update_note(
        data["session_id"],
        note_id,
        title=data.get("title"),
        content=data.get("content"),
    )
    return jsonify({"status": "updated"})


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def remove_note(note_id):
    data = request.get_json()
    if not data or "session_id" not in data:
        return jsonify({"error": "Отсутствует session_id"}), 400
    delete_note(data["session_id"], note_id)
    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

from flask import Flask, jsonify
from .mongo import get_db

app = Flask(__name__)

@app.route("/health")
def health():
    return "Stats service is running!", 200

@app.route("/stats")
def stats():
    db = get_db()
    stats = list(db.workouts.find())
    for s in stats:
        s["_id"] = str(s["_id"])
    return jsonify(stats), 200

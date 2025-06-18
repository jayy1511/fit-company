from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

mongo = MongoClient("mongodb://stats_mongo:27017/")
db = mongo["stats_db"]
workout_stats = db["workout_stats"]

@app.route("/stats", methods=["GET"])
def get_user_stats():
    user_email = request.args.get("user_email")
    if not user_email:
        return jsonify({"error": "user_email query param is required"}), 400

    data = list(workout_stats.find({"user_email": user_email}, {"_id": 0}))
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)

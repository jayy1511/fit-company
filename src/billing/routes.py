from flask import Blueprint, request, jsonify

billing_bp = Blueprint("billing", __name__)

# In-memory mock database
subscriptions = {}

@billing_bp.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    subscriptions[email] = True
    return jsonify({"message": f"{email} subscribed successfully"}), 200

@billing_bp.route("/cancel", methods=["POST"])
def cancel():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    subscriptions[email] = False
    return jsonify({"message": f"{email} unsubscribed"}), 200

@billing_bp.route("/status", methods=["GET"])
def status():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email query param is required"}), 400
    is_premium = subscriptions.get(email, False)
    return jsonify({"premium": is_premium}), 200

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from src.fit.models_dto import UserSchema
from src.fit.services.auth_service import admin_required, jwt_required
from src.fit.services.user_service import create_user as create_user_service, get_all_users as get_all_users_service, update_user_profile, get_user_profile, hash_password
from src.fit.models_db import UserModel
from src.fit.database import db_session
import os, re

bp_users = Blueprint("users", __name__)
BOOTSTRAP_KEY = os.environ.get("BOOTSTRAP_KEY", "bootstrap-secret-key")

@bp_users.route("/users", methods=["POST"])
@admin_required
def create_user():
    try:
        user_data = request.get_json()
        required_fields = ["email", "name", "role"]
        for field in required_fields:
            if field not in user_data:
                return jsonify({"error": f"'{field}' is required"}), 400

        def is_valid_email(email):
            return re.match(r"[^@]+@[^@]+\\.[^@]+", email) is not None

        if not is_valid_email(user_data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        if user_data["role"] not in ["user", "admin"]:
            return jsonify({"error": "Invalid role, must be 'user' or 'admin'"}), 400

        user = UserSchema.model_validate(user_data)
        created_user = create_user_service(user)
        return jsonify(created_user.model_dump()), 201

    except ValidationError as e:
        return jsonify({"error": "Invalid user data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating user", "details": str(e)}), 500

@bp_users.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    try:
        users = get_all_users_service()
        return jsonify([user.model_dump() for user in users]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving users", "details": str(e)}), 500

@bp_users.route("/bootstrap/admin", methods=["POST"])
def create_bootstrap_admin():
    try:
        bootstrap_key = request.headers.get('X-Bootstrap-Key')
        if not bootstrap_key or bootstrap_key != BOOTSTRAP_KEY:
            return jsonify({"error": "Invalid bootstrap key"}), 401

        db = db_session()
        admin_exists = db.query(UserModel).filter(UserModel.role == "admin").first() is not None
        db.close()

        if admin_exists:
            return jsonify({"error": "Admin user already exists"}), 409

        admin_data = request.get_json()
        admin_data["role"] = "admin"
        admin_data["password"] = hash_password(admin_data["password"])

        admin_user = UserSchema.model_validate(admin_data)
        created_admin = create_user_service(admin_user)
        return jsonify(created_admin.model_dump()), 201

    except ValidationError as e:
        return jsonify({"error": "Invalid admin data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating admin", "details": str(e)}), 500

@bp_users.route("/profile/onboarding", methods=["POST"])
@jwt_required
def onboard_user():
    try:
        user_email = g.user_email
        profile_data = request.get_json()
        profile = UserProfileSchema.model_validate(profile_data)
        updated_profile = update_user_profile(user_email, profile)
        if not updated_profile:
            return jsonify({"error": "User not found"}), 404
        return jsonify(updated_profile.model_dump()), 200

    except ValidationError as e:
        return jsonify({"error": "Invalid profile data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error updating profile", "details": str(e)}), 500

@bp_users.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    try:
        user_email = g.user_email
        profile = get_user_profile(user_email)
        if not profile:
            return jsonify({"error": "User not found"}), 404
        return jsonify(profile.model_dump()), 200

    except Exception as e:
        return jsonify({"error": "Error retrieving profile", "details": str(e)}), 500

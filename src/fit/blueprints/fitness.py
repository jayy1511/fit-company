from flask import Blueprint, request, jsonify, g
from src.fit.services.fitness_service import get_all_exercises, get_exercise_by_id, get_exercises_by_muscle_group
from src.fit.services.fitness_coach_service import calculate_intensity, request_wod
from src.fit.models_dto import WodExerciseSchema, WodResponseSchema, MuscleGroupImpact
from src.fit.database import db_session
from src.fit.models_db import UserExerciseHistoryModel
from src.fit.services.auth_service import jwt_required
from datetime import datetime, date
import random

bp_fitness = Blueprint("fitness", __name__)

@bp_fitness.route("/fitness/exercises", methods=["GET"])
def get_exercises():
    try:
        muscle_group_id = request.args.get("muscle_group_id")
        if muscle_group_id:
            exercises = get_exercises_by_muscle_group(int(muscle_group_id))
        else:
            exercises = get_all_exercises()
        return jsonify([ex.model_dump() for ex in exercises]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving exercises", "details": str(e)}), 500

@bp_fitness.route("/fitness/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    try:
        exercise = get_exercise_by_id(exercise_id)
        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify(exercise.model_dump()), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving exercise", "details": str(e)}), 500

@bp_fitness.route("/fitness/wod", methods=["GET"])
@jwt_required
def get_wod():
    try:
        exercises_with_muscles = request_wod()
        wod_exercises = []
        for exercise, muscle_groups in exercises_with_muscles:
            muscle_impacts = [
                MuscleGroupImpact(
                    id=mg.id,
                    name=mg.name,
                    body_part=mg.body_part,
                    is_primary=is_primary,
                    intensity=calculate_intensity(exercise.difficulty) * (1.2 if is_primary else 0.8)
                )
                for mg, is_primary in muscle_groups
            ]
            wod_exercise = WodExerciseSchema(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                difficulty=exercise.difficulty,
                muscle_groups=muscle_impacts,
                suggested_weight=random.uniform(5.0, 50.0),
                suggested_reps=random.randint(8, 15)
            )
            wod_exercises.append(wod_exercise)

        response = WodResponseSchema(
            exercises=wod_exercises,
            generated_at=datetime.now().isoformat()
        )

        db = db_session()
        try:
            for exercise in wod_exercises:
                history_entry = UserExerciseHistoryModel(
                    user_email=g.user_email,
                    exercise_id=exercise.id,
                    date_assigned=date.today()
                )
                db.add(history_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            print("Error saving exercise history:", e)
        finally:
            db.close()

        return jsonify(response.model_dump()), 200
    except Exception as e:
        return jsonify({"error": "Error generating workout of the day", "details": str(e)}), 500

@bp_fitness.route("/history", methods=["GET"])
@jwt_required
def get_exercise_history():
    try:
        db = db_session()
        history = (
            db.query(UserExerciseHistoryModel)
            .filter(UserExerciseHistoryModel.user_email == g.user_email)
            .order_by(UserExerciseHistoryModel.date_assigned.desc())
            .all()
        )

        history_data = [
            {
                "exercise_id": record.exercise_id,
                "date_assigned": record.date_assigned.isoformat()
            }
            for record in history
        ]
        return jsonify({"history": history_data}), 200
    except Exception as e:
        return jsonify({"error": "Could not retrieve history", "details": str(e)}), 500
    finally:
        db.close()

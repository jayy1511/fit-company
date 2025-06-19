import logging
import os
from typing import List, Tuple
import requests
from .models_db import ExerciseModel, MuscleGroupModel, exercise_muscle_groups
from .database import db_session
import random
from time import time

logger = logging.getLogger(__name__)

def heavy_computation(duration_seconds: int = 3):
    start_time = time()
    while (time() - start_time) < duration_seconds:
        j = 0
        while j < 1000000:
            j += 1

def calculate_intensity(difficulty: int) -> float:
    return (difficulty - 1) / 4.0

def get_last_workout_exercises(user_email: str) -> List[int]:
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"X-API-Key": os.getenv("FIT_API_KEY")}
    history_response = requests.post(
        f"{monolith_url}/workouts/last", headers=headers, json={"email": user_email}
    )
    history_response.raise_for_status()
    return history_response.json()

def save_workout_exercises(user_email: str, exercise_ids: List[int]):
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"X-API-Key": os.getenv("FIT_API_KEY")}
    requests.post(
        f"{monolith_url}/workouts/", headers=headers, json={"email": user_email, "exercises": exercise_ids}
    )

def is_premium_user(user_email: str) -> bool:
    billing_url = os.getenv("BILLING_URL", "http://billing:5000")
    try:
        response = requests.get(f"{billing_url}/status", params={"email": user_email})
        if response.status_code == 200:
            return response.json().get("premium", False)
    except Exception as e:
        logger.warning(f"Billing check failed: {e}")
    return False

def create_wod_for_user(user_email: str) -> List[Tuple[ExerciseModel, List[Tuple[MuscleGroupModel, bool]]]]:
    logger.debug(f"running heavy computation to generate wod for user {user_email}")
    heavy_computation(random.randint(1, 5))
    logger.debug(f"heavy computation completed for user {user_email}")

    db = db_session()
    try:
        last_exercise_ids = get_last_workout_exercises(user_email)
        available_exercises = db.query(ExerciseModel).filter(
            ~ExerciseModel.id.in_(last_exercise_ids)
        ).all()

        if len(available_exercises) < 9:
            available_exercises = db.query(ExerciseModel).all()

        premium = is_premium_user(user_email)
        count = 9 if premium else 6
        selected_exercises = random.sample(available_exercises, min(count, len(available_exercises)))

        save_workout_exercises(user_email, [exercise.id for exercise in selected_exercises])

        result = []
        for exercise in selected_exercises:
            stmt = db.query(
                MuscleGroupModel,
                exercise_muscle_groups.c.is_primary
            ).join(
                exercise_muscle_groups,
                MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
            ).filter(
                exercise_muscle_groups.c.exercise_id == exercise.id
            )
            muscle_groups = [(mg, is_primary) for mg, is_primary in stmt.all()]
            result.append((exercise, muscle_groups))
        return result
    finally:
        db.close()

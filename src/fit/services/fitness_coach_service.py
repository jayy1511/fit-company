from typing import List, Tuple
from ..models_db import ExerciseModel, MuscleGroupModel, exercise_muscle_groups
from ..database import db_session
import random
from time import time
from datetime import date, timedelta
from src.fit.models_db import ExerciseModel, UserExerciseHistoryModel
from src.fit.database import db_session
import random

def heavy_computation(duration_seconds: int = 3):
    """
    Perform CPU-intensive calculations to simulate heavy processing.
    Uses matrix operations which are CPU-intensive.
    """
    start_time = time()
    i = 0
    while (time() - start_time) < duration_seconds:
        j = 0
        while j < 1000000:
            j += 1
        i += 1

def calculate_intensity(difficulty: int) -> float:
    """
    Calculate the intensity of an exercise based on its difficulty level (1-5).
    Returns a value between 0.0 and 1.0.
    """
    # Convert difficulty (1-5) to intensity (0.0-1.0)
    return (difficulty - 1) / 4.0

def request_wod(user_email: str = None):
    db = db_session()

    try:
        query = db.query(ExerciseModel)

        # 👇 If user_email is provided, fetch yesterday’s exercises
        if user_email:
            yesterday = date.today() - timedelta(days=1)
            subquery = db.query(UserExerciseHistoryModel.exercise_id).filter(
                UserExerciseHistoryModel.user_email == user_email,
                UserExerciseHistoryModel.date_assigned == yesterday
            )
            excluded_ids = [row.exercise_id for row in subquery]
            if excluded_ids:
                query = query.filter(~ExerciseModel.id.in_(excluded_ids))

        exercises = query.all()
        selected = random.sample(exercises, min(len(exercises), 5))  # Pick 5 random

        result = []
        for ex in selected:
            muscle_groups = []
            for mg in ex.muscle_groups:
                is_primary = True  # placeholder logic
                muscle_groups.append((mg, is_primary))
            result.append((ex, muscle_groups))

        return result

    finally:
        db.close()
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import requests
import random
import datetime

app = FastAPI()

# --- Schema models (matching monolith WodExerciseSchema + MuscleGroupImpact) ---
class MuscleGroupImpact(BaseModel):
    id: int
    name: str
    body_part: str
    is_primary: bool
    intensity: float

class WodExercise(BaseModel):
    id: int
    name: str
    description: str
    difficulty: int
    muscle_groups: List[MuscleGroupImpact]
    suggested_weight: float
    suggested_reps: int

class WodResponse(BaseModel):
    exercises: List[WodExercise]
    generated_at: str

# --- Endpoint ---
@app.get("/generate-wod", response_model=WodResponse)
def generate_wod(user_email: str):
    try:
        # 📡 1. Get exercise history for the user from the monolith
        history_resp = requests.get(f"http://fit-monolith:5001/history", headers={"X-User-Email": user_email})
        if history_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get user history")

        history_data = history_resp.json().get("history", [])
        recent_exercise_ids = {record["exercise_id"] for record in history_data if record["date_assigned"] == datetime.date.today().isoformat()}

        # 📡 2. Get all exercises
        exercises_resp = requests.get("http://fit-monolith:5001/fitness/exercises")
        if exercises_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get exercises")

        all_exercises = exercises_resp.json()

        # ❌ Filter out today's exercises
        filtered_exercises = [ex for ex in all_exercises if ex["id"] not in recent_exercise_ids]

        # 🎲 Select random 3-5 exercises
        selected = random.sample(filtered_exercises, min(5, len(filtered_exercises)))

        # 🧠 Format response
        wod_exercises = []
        for ex in selected:
            impacts = []
            for mg in ex["muscle_groups"]:
                impacts.append(MuscleGroupImpact(**mg))

            wod_exercises.append(WodExercise(
                id=ex["id"],
                name=ex["name"],
                description=ex["description"],
                difficulty=ex["difficulty"],
                muscle_groups=impacts,
                suggested_weight=random.uniform(5.0, 50.0),
                suggested_reps=random.randint(8, 15)
            ))

        return WodResponse(
            exercises=wod_exercises,
            generated_at=datetime.datetime.now(datetime.UTC).isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
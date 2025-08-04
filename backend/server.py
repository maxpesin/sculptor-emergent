from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import json
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# JSON file storage paths
DATA_DIR = ROOT_DIR.parent / 'data' / 'json'
DATA_DIR.mkdir(parents=True, exist_ok=True)

EXERCISES_FILE = DATA_DIR / 'exercises.json'
SPLITS_FILE = DATA_DIR / 'splits.json'
SESSIONS_FILE = DATA_DIR / 'sessions.json'

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JSON Database Helper Functions
class JSONDatabase:
    @staticmethod
    def load_json(file_path: Path, default_data: list = None):
        if default_data is None:
            default_data = []
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return default_data
        except (json.JSONDecodeError, FileNotFoundError):
            return default_data
    
    @staticmethod
    def save_json(file_path: Path, data: list):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving to {file_path}: {e}")
            return False
    
    @staticmethod
    def find_by_id(data: list, item_id: str):
        return next((item for item in data if item.get('id') == item_id), None)
    
    @staticmethod
    def filter_by(data: list, **filters):
        result = data
        for key, value in filters.items():
            if value is not None:
                result = [item for item in result if item.get(key) == value]
        return result

db = JSONDatabase()


# Define Models
class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    muscle_group: str
    equipment: Optional[str] = None
    instructions: Optional[str] = None

class ExerciseCreate(BaseModel):
    name: str
    muscle_group: str
    equipment: Optional[str] = None
    instructions: Optional[str] = None

class Set(BaseModel):
    set_number: int
    weight: float
    reps: int

class WorkoutExercise(BaseModel):
    exercise_id: str
    exercise_name: str
    rep_range: Optional[str] = None
    sets: List[Set] = []
    completed_count: int = 0
    target_completions: int = 3
    is_archived: bool = False

class WorkoutDay(BaseModel):
    day_number: int
    day_name: str
    muscle_groups: List[str]
    exercises: List[WorkoutExercise] = []
    completed: bool = False

class WorkoutSplit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    days_per_week: int
    days: List[WorkoutDay]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WorkoutSplitCreate(BaseModel):
    name: str
    days_per_week: int
    days: List[WorkoutDay]

class WorkoutSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    split_id: str
    day_number: int
    exercises: List[WorkoutExercise]
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class WorkoutSessionCreate(BaseModel):
    split_id: str
    day_number: int
    exercises: List[WorkoutExercise]

# Predefined exercise data
PREDEFINED_EXERCISES = [
    # Chest
    {"name": "Bench Press", "muscle_group": "Chest", "equipment": "Barbell"},
    {"name": "Incline Dumbbell Press", "muscle_group": "Chest", "equipment": "Dumbbells"},
    {"name": "Dips", "muscle_group": "Chest", "equipment": "Bodyweight"},
    {"name": "Push-ups", "muscle_group": "Chest", "equipment": "Bodyweight"},
    {"name": "Chest Flyes", "muscle_group": "Chest", "equipment": "Dumbbells"},
    {"name": "Cable Crossovers", "muscle_group": "Chest", "equipment": "Cable"},
    {"name": "Decline Bench Press", "muscle_group": "Chest", "equipment": "Barbell"},
    
    # Back
    {"name": "Pull-ups", "muscle_group": "Back", "equipment": "Bodyweight"},
    {"name": "Bent-over Row", "muscle_group": "Back", "equipment": "Barbell"},
    {"name": "Lat Pulldown", "muscle_group": "Back", "equipment": "Cable"},
    {"name": "Deadlift", "muscle_group": "Back", "equipment": "Barbell"},
    {"name": "T-Bar Row", "muscle_group": "Back", "equipment": "T-Bar"},
    {"name": "Cable Rows", "muscle_group": "Back", "equipment": "Cable"},
    {"name": "Face Pulls", "muscle_group": "Back", "equipment": "Cable"},
    
    # Shoulders
    {"name": "Overhead Press", "muscle_group": "Shoulders", "equipment": "Barbell"},
    {"name": "Lateral Raises", "muscle_group": "Shoulders", "equipment": "Dumbbells"},
    {"name": "Rear Delt Flyes", "muscle_group": "Shoulders", "equipment": "Dumbbells"},
    {"name": "Arnold Press", "muscle_group": "Shoulders", "equipment": "Dumbbells"},
    {"name": "Upright Rows", "muscle_group": "Shoulders", "equipment": "Barbell"},
    {"name": "Front Raises", "muscle_group": "Shoulders", "equipment": "Dumbbells"},
    {"name": "Shrugs", "muscle_group": "Shoulders", "equipment": "Dumbbells"},
    
    # Arms
    {"name": "Bicep Curls", "muscle_group": "Arms", "equipment": "Dumbbells"},
    {"name": "Tricep Dips", "muscle_group": "Arms", "equipment": "Bodyweight"},
    {"name": "Hammer Curls", "muscle_group": "Arms", "equipment": "Dumbbells"},
    {"name": "Tricep Extensions", "muscle_group": "Arms", "equipment": "Dumbbells"},
    {"name": "Close-Grip Bench Press", "muscle_group": "Arms", "equipment": "Barbell"},
    {"name": "Cable Curls", "muscle_group": "Arms", "equipment": "Cable"},
    {"name": "Diamond Push-ups", "muscle_group": "Arms", "equipment": "Bodyweight"},
    
    # Legs
    {"name": "Squats", "muscle_group": "Legs", "equipment": "Barbell"},
    {"name": "Leg Press", "muscle_group": "Legs", "equipment": "Machine"},
    {"name": "Lunges", "muscle_group": "Legs", "equipment": "Dumbbells"},
    {"name": "Leg Curls", "muscle_group": "Legs", "equipment": "Machine"},
    {"name": "Calf Raises", "muscle_group": "Legs", "equipment": "Bodyweight"},
    {"name": "Romanian Deadlift", "muscle_group": "Legs", "equipment": "Barbell"},
    {"name": "Bulgarian Split Squats", "muscle_group": "Legs", "equipment": "Bodyweight"},
    
    # Core
    {"name": "Plank", "muscle_group": "Core", "equipment": "Bodyweight"},
    {"name": "Russian Twists", "muscle_group": "Core", "equipment": "Bodyweight"},
    {"name": "Bicycle Crunches", "muscle_group": "Core", "equipment": "Bodyweight"},
    {"name": "Mountain Climbers", "muscle_group": "Core", "equipment": "Bodyweight"},
    {"name": "Dead Bug", "muscle_group": "Core", "equipment": "Bodyweight"},
    {"name": "Hanging Leg Raises", "muscle_group": "Core", "equipment": "Pull-up Bar"},
    {"name": "Ab Wheel Rollouts", "muscle_group": "Core", "equipment": "Ab Wheel"}
]

# Initialize database with exercises
@app.on_event("startup")
async def startup_event():
    # Check if exercises already exist
    existing_exercises = db.load_json(EXERCISES_FILE, [])
    if len(existing_exercises) == 0:
        # Insert predefined exercises
        exercises_to_insert = []
        for exercise_data in PREDEFINED_EXERCISES:
            exercise = Exercise(**exercise_data)
            exercises_to_insert.append(exercise.dict())
        db.save_json(EXERCISES_FILE, exercises_to_insert)
        logger.info(f"Inserted {len(exercises_to_insert)} exercises into JSON database")

# Exercise routes
@api_router.get("/exercises", response_model=List[Exercise])
async def get_exercises(muscle_group: Optional[str] = None):
    exercises_data = db.load_json(EXERCISES_FILE, [])
    if muscle_group:
        exercises_data = db.filter_by(exercises_data, muscle_group=muscle_group)
    return [Exercise(**exercise) for exercise in exercises_data]

@api_router.post("/exercises", response_model=Exercise)
async def create_exercise(exercise: ExerciseCreate):
    exercise_obj = Exercise(**exercise.dict())
    exercises_data = db.load_json(EXERCISES_FILE, [])
    exercises_data.append(exercise_obj.dict())
    db.save_json(EXERCISES_FILE, exercises_data)
    return exercise_obj

@api_router.get("/exercises/{exercise_id}", response_model=Exercise)
async def get_exercise(exercise_id: str):
    exercises_data = db.load_json(EXERCISES_FILE, [])
    exercise = db.find_by_id(exercises_data, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return Exercise(**exercise)

@api_router.get("/muscle-groups")
async def get_muscle_groups():
    exercises_data = db.load_json(EXERCISES_FILE, [])
    muscle_groups = list(set(exercise.get('muscle_group') for exercise in exercises_data))
    return sorted(muscle_groups)

# Workout Split routes
@api_router.get("/splits", response_model=List[WorkoutSplit])
async def get_workout_splits():
    splits_data = db.load_json(SPLITS_FILE, [])
    # Sort by created_at descending
    splits_data.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return [WorkoutSplit(**split) for split in splits_data]

@api_router.post("/splits", response_model=WorkoutSplit)
async def create_workout_split(split: WorkoutSplitCreate):
    split_obj = WorkoutSplit(**split.dict())
    splits_data = db.load_json(SPLITS_FILE, [])
    splits_data.append(split_obj.dict())
    db.save_json(SPLITS_FILE, splits_data)
    return split_obj

@api_router.get("/splits/{split_id}", response_model=WorkoutSplit)
async def get_workout_split(split_id: str):
    splits_data = db.load_json(SPLITS_FILE, [])
    split = db.find_by_id(splits_data, split_id)
    if not split:
        raise HTTPException(status_code=404, detail="Workout split not found")
    return WorkoutSplit(**split)

@api_router.put("/splits/{split_id}", response_model=WorkoutSplit)
async def update_workout_split(split_id: str, split_update: WorkoutSplitCreate):
    splits_data = db.load_json(SPLITS_FILE, [])
    existing_split = db.find_by_id(splits_data, split_id)
    if not existing_split:
        raise HTTPException(status_code=404, detail="Workout split not found")
    
    updated_split = WorkoutSplit(id=split_id, **split_update.dict())
    # Replace the existing split
    for i, split in enumerate(splits_data):
        if split.get('id') == split_id:
            splits_data[i] = updated_split.dict()
            break
    
    db.save_json(SPLITS_FILE, splits_data)
    return updated_split

@api_router.delete("/splits/{split_id}")
async def delete_workout_split(split_id: str):
    splits_data = db.load_json(SPLITS_FILE, [])
    original_length = len(splits_data)
    splits_data = [split for split in splits_data if split.get('id') != split_id]
    
    if len(splits_data) == original_length:
        raise HTTPException(status_code=404, detail="Workout split not found")
    
    db.save_json(SPLITS_FILE, splits_data)
    return {"message": "Workout split deleted successfully"}

# Workout Session routes
@api_router.get("/sessions", response_model=List[WorkoutSession])
async def get_workout_sessions():
    sessions_data = db.load_json(SESSIONS_FILE, [])
    # Sort by completed_at descending
    sessions_data.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
    return [WorkoutSession(**session) for session in sessions_data]

@api_router.post("/sessions", response_model=WorkoutSession)
async def create_workout_session(session: WorkoutSessionCreate):
    session_obj = WorkoutSession(**session.dict())
    sessions_data = db.load_json(SESSIONS_FILE, [])
    sessions_data.append(session_obj.dict())
    db.save_json(SESSIONS_FILE, sessions_data)
    return session_obj

@api_router.get("/sessions/{session_id}", response_model=WorkoutSession)
async def get_workout_session(session_id: str):
    sessions_data = db.load_json(SESSIONS_FILE, [])
    session = db.find_by_id(sessions_data, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Workout session not found")
    return WorkoutSession(**session)

@api_router.patch("/sessions/{session_id}/exercises/{exercise_id}/complete")
async def complete_exercise(session_id: str, exercise_id: str):
    """Mark an exercise as completed and handle archiving logic"""
    sessions_data = db.load_json(SESSIONS_FILE, [])
    session = db.find_by_id(sessions_data, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Workout session not found")
    
    # Find the exercise in the session
    session_obj = WorkoutSession(**session)
    exercise_found = False
    
    for exercise in session_obj.exercises:
        if exercise.exercise_id == exercise_id:
            exercise_found = True
            exercise.completed_count += 1
            
            # Check if exercise should be archived
            if exercise.completed_count >= exercise.target_completions:
                exercise.is_archived = True
            break
    
    if not exercise_found:
        raise HTTPException(status_code=404, detail="Exercise not found in session")
    
    # Update the session in the data
    for i, s in enumerate(sessions_data):
        if s.get('id') == session_id:
            sessions_data[i] = session_obj.dict()
            break
    
    db.save_json(SESSIONS_FILE, sessions_data)
    
    return {
        "message": "Exercise completed successfully",
        "exercise_id": exercise_id,
        "completed_count": exercise.completed_count,
        "is_archived": exercise.is_archived
    }

@api_router.patch("/sessions/{session_id}/exercises/{exercise_id}/reset")
async def reset_exercise_completion(session_id: str, exercise_id: str):
    """Reset exercise completion count (useful for testing or mistakes)"""
    sessions_data = db.load_json(SESSIONS_FILE, [])
    session = db.find_by_id(sessions_data, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Workout session not found")
    
    # Find the exercise in the session
    session_obj = WorkoutSession(**session)
    exercise_found = False
    
    for exercise in session_obj.exercises:
        if exercise.exercise_id == exercise_id:
            exercise_found = True
            exercise.completed_count = 0
            exercise.is_archived = False
            break
    
    if not exercise_found:
        raise HTTPException(status_code=404, detail="Exercise not found in session")
    
    # Update the session in the data
    for i, s in enumerate(sessions_data):
        if s.get('id') == session_id:
            sessions_data[i] = session_obj.dict()
            break
    
    db.save_json(SESSIONS_FILE, sessions_data)
    
    return {
        "message": "Exercise completion reset successfully",
        "exercise_id": exercise_id,
        "completed_count": 0,
        "is_archived": False
    }

# Template routes for common workout splits
@api_router.get("/templates")
async def get_workout_templates():
    templates = {
        "push_pull_legs": {
            "name": "Push/Pull/Legs (3-Day)",
            "days_per_week": 3,
            "days": [
                {
                    "day_number": 1,
                    "day_name": "Push Day",
                    "muscle_groups": ["Chest", "Shoulders", "Arms"],
                    "exercises": []
                },
                {
                    "day_number": 2,
                    "day_name": "Pull Day", 
                    "muscle_groups": ["Back", "Arms"],
                    "exercises": []
                },
                {
                    "day_number": 3,
                    "day_name": "Leg Day",
                    "muscle_groups": ["Legs", "Core"],
                    "exercises": []
                }
            ]
        },
        "upper_lower": {
            "name": "Upper/Lower (4-Day)",
            "days_per_week": 4,
            "days": [
                {
                    "day_number": 1,
                    "day_name": "Upper Body 1",
                    "muscle_groups": ["Chest", "Back", "Shoulders", "Arms"],
                    "exercises": []
                },
                {
                    "day_number": 2,
                    "day_name": "Lower Body 1",
                    "muscle_groups": ["Legs", "Core"],
                    "exercises": []
                },
                {
                    "day_number": 3,
                    "day_name": "Upper Body 2",
                    "muscle_groups": ["Chest", "Back", "Shoulders", "Arms"],
                    "exercises": []
                },
                {
                    "day_number": 4,
                    "day_name": "Lower Body 2",
                    "muscle_groups": ["Legs", "Core"],
                    "exercises": []
                }
            ]
        },
        "full_body": {
            "name": "Full Body (3-Day)",
            "days_per_week": 3,
            "days": [
                {
                    "day_number": 1,
                    "day_name": "Full Body 1",
                    "muscle_groups": ["Chest", "Back", "Legs"],
                    "exercises": []
                },
                {
                    "day_number": 2,
                    "day_name": "Full Body 2",
                    "muscle_groups": ["Shoulders", "Arms", "Core"],
                    "exercises": []
                },
                {
                    "day_number": 3,
                    "day_name": "Full Body 3",
                    "muscle_groups": ["Chest", "Back", "Legs"],
                    "exercises": []
                }
            ]
        }
    }
    return templates

# Health check
@api_router.get("/")
async def root():
    return {"message": "Workout Tracker API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
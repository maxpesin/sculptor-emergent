from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


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
    existing_exercises = await db.exercises.count_documents({})
    if existing_exercises == 0:
        # Insert predefined exercises
        exercises_to_insert = []
        for exercise_data in PREDEFINED_EXERCISES:
            exercise = Exercise(**exercise_data)
            exercises_to_insert.append(exercise.dict())
        await db.exercises.insert_many(exercises_to_insert)
        logger.info(f"Inserted {len(exercises_to_insert)} exercises into database")

# Exercise routes
@api_router.get("/exercises", response_model=List[Exercise])
async def get_exercises(muscle_group: Optional[str] = None):
    query = {}
    if muscle_group:
        query["muscle_group"] = muscle_group
    exercises = await db.exercises.find(query).to_list(1000)
    return [Exercise(**exercise) for exercise in exercises]

@api_router.post("/exercises", response_model=Exercise)
async def create_exercise(exercise: ExerciseCreate):
    exercise_obj = Exercise(**exercise.dict())
    await db.exercises.insert_one(exercise_obj.dict())
    return exercise_obj

@api_router.get("/exercises/{exercise_id}", response_model=Exercise)
async def get_exercise(exercise_id: str):
    exercise = await db.exercises.find_one({"id": exercise_id})
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return Exercise(**exercise)

@api_router.get("/muscle-groups")
async def get_muscle_groups():
    # Get unique muscle groups from exercises
    pipeline = [
        {"$group": {"_id": "$muscle_group"}},
        {"$sort": {"_id": 1}}
    ]
    muscle_groups = await db.exercises.aggregate(pipeline).to_list(1000)
    return [group["_id"] for group in muscle_groups]

# Workout Split routes
@api_router.get("/splits", response_model=List[WorkoutSplit])
async def get_workout_splits():
    splits = await db.workout_splits.find().sort("created_at", -1).to_list(1000)
    return [WorkoutSplit(**split) for split in splits]

@api_router.post("/splits", response_model=WorkoutSplit)
async def create_workout_split(split: WorkoutSplitCreate):
    split_obj = WorkoutSplit(**split.dict())
    await db.workout_splits.insert_one(split_obj.dict())
    return split_obj

@api_router.get("/splits/{split_id}", response_model=WorkoutSplit)
async def get_workout_split(split_id: str):
    split = await db.workout_splits.find_one({"id": split_id})
    if not split:
        raise HTTPException(status_code=404, detail="Workout split not found")
    return WorkoutSplit(**split)

@api_router.put("/splits/{split_id}", response_model=WorkoutSplit)
async def update_workout_split(split_id: str, split_update: WorkoutSplitCreate):
    existing_split = await db.workout_splits.find_one({"id": split_id})
    if not existing_split:
        raise HTTPException(status_code=404, detail="Workout split not found")
    
    updated_split = WorkoutSplit(id=split_id, **split_update.dict())
    await db.workout_splits.replace_one({"id": split_id}, updated_split.dict())
    return updated_split

@api_router.delete("/splits/{split_id}")
async def delete_workout_split(split_id: str):
    result = await db.workout_splits.delete_one({"id": split_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Workout split not found")
    return {"message": "Workout split deleted successfully"}

# Workout Session routes
@api_router.get("/sessions", response_model=List[WorkoutSession])
async def get_workout_sessions():
    sessions = await db.workout_sessions.find().sort("completed_at", -1).to_list(1000)
    return [WorkoutSession(**session) for session in sessions]

@api_router.post("/sessions", response_model=WorkoutSession)
async def create_workout_session(session: WorkoutSessionCreate):
    session_obj = WorkoutSession(**session.dict())
    await db.workout_sessions.insert_one(session_obj.dict())
    return session_obj

@api_router.get("/sessions/{session_id}", response_model=WorkoutSession)
async def get_workout_session(session_id: str):
    session = await db.workout_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Workout session not found")
    return WorkoutSession(**session)

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
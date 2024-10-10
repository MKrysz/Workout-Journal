from fastapi import FastAPI, Depends, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date

from . import crud, models, schemas
from .database import SessionLocal, engine

# In a very simplistic way create the database tables:
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# For better performance? or smth, didn't wach full video

# origins = ['https://localhost:3000']

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins = origins,
#     allow_credentials = True,
#     allow_methods = ["*"],
#     allow_headers = ["*"]
# )

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#region Weight

# Create

@app.post("/weight/", response_model=schemas.Weight)
def create_weight(weight: schemas.WeightCreate, db: Session = Depends(get_db)):
    try:
        db_weight = crud.create_weight(db, weight=weight)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return db_weight

# Read

@app.get("/weight/", response_model=list[schemas.Weight])
def read_weights(skip: int = 0,limit: int = 100, db: Session = Depends(get_db)):
    weights = crud.get_weights(db, skip=skip, limit=limit)
    return weights

@app.get("/weight/{weight_id}", response_model=schemas.Weight)
def read_weight(weight_id: int, db: Session = Depends(get_db)):
    db_weight = crud.get_weight(db, weight_id=weight_id)
    if (db_weight is None):
        raise HTTPException(status_code=404, detail="Weight not found")
    return db_weight

@app.get("/weight/range/", response_model=list[schemas.Weight])
def read_weight_by_range(start: date, end: date|None = None, db: Session = Depends(get_db)):
    result = crud.get_weight_by_daterange(db, start, end)
    if result is None:
        raise HTTPException(status_code=404, detail="Weight not found")
    return result

# Update

# Delete

#endregion Weight


#region Workout

# Create

@app.post("/workout/", response_model=schemas.Workout)
def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    db_workout = crud.create_workout(db, workout=workout)
    return db_workout

# Read

@app.get("/workout/", response_model=list[schemas.Workout])
def read_workouts(skip: int = 0,limit: int = 100, db: Session = Depends(get_db)):
    workouts = crud.get_workouts(db, skip=skip, limit=limit)
    return workouts

@app.get("/workout/{workout_id}", response_model=schemas.Workout)
def read_workout(workout_id: int, db: Session = Depends(get_db)):
    db_workout = crud.get_workout(db, workout_id=workout_id)
    if (db_workout is None):
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout

@app.get("/workout/range/", response_model=list[schemas.Workout])
def read_workout_by_range(start: date, end: date|None = None, db: Session = Depends(get_db)):
    result = crud.get_workout_by_daterange(db, start, end)
    if result is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return result

# Update

# Delete

#endregion Workout


#region Exercise

# Create

@app.post("/exercise/", response_model=schemas.Exercise)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    try:
        db_exercise = crud.create_exercise(db, exercise=exercise)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return db_exercise

# Read

@app.get("/exercise/", response_model=list[schemas.Exercise])
def read_weights(skip: int = 0,limit: int = 100, db: Session = Depends(get_db)):
    exercises = crud.get_exercises(db, skip=skip, limit=limit)
    return exercises

@app.get("/exercise/{exercise_id}", response_model=schemas.Exercise)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if (db_exercise is None):
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise

@app.get("/exercise/range/", response_model=list[schemas.Exercise])
def read_exercise_by_range(start: date, end: date|None = None, db: Session = Depends(get_db)):
    result = crud.get_exercise_by_daterange(db, start, end)
    if result is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return result

# Update

# Delete

#endregion Exercise


#region Set

# Create

# Read

# Update

# Delete

#endregion Set


#region EquipmentWeight

# Create

# Read

# Update

# Delete

#endregion EquipmentWeight

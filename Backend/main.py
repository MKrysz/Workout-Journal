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

@app.post("/weight/", response_model=schemas.Weight)
def create_weight(weight: schemas.WeightCreate, db: Session = Depends(get_db)):
    db_weight = crud.create_weight(db, weight=weight)
    if(db_weight == "Date-already-exists"):
        raise HTTPException(status_code=400, detail="This date's weight log already exists")
    return db_weight

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
        raise HTTPException(status_code=404, detail="Weights not found")
    return result

@app.post("/workout/", response_model=schemas.Workout)
def create_weight(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    db_workout = crud.create_workout(db, workout=workout)
    return db_workout
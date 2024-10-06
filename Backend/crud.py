from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date

from . import models, schemas

# Utility functions
def Timedelta2Minutes(duration):
    return int(duration.total_seconds()/60)

# WEIGHT

## Create
def create_weight(db: Session, weight: schemas.WeightCreate):
    if (weight.timestamp is None):
        weight.timestamp = date.today()
    db_weight = get_weight_by_daterange(db, start=weight.timestamp)
    if(db_weight):
        return "Date-already-exists"
    db_weight = models.Weight(weight=weight.weight, timestamp=weight.timestamp)
    db.add(db_weight)
    db.commit()
    db.refresh(db_weight)
    return db_weight

## Read

def get_weight(db: Session, weight_id: int):
    return db.query(models.Weight).filter(models.Weight.id == weight_id).first()

def get_weights(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Weight).offset(skip).limit(limit).all()

def get_weight_by_daterange(db: Session, start: date, end: date|None = None):
    if end is None:
        end = start
    return db.query(models.Weight).filter(
        and_(
            (start <= models.Weight.timestamp),
            (models.Weight.timestamp <= end)
        )).all()

## Update

## Delete


# Workout

## Create

def create_workout(db: Session, workout: schemas.WorkoutCreate):
    if (workout.duration_in_minutes is None):
        if (workout.end_time is None):
            workout.end_time = datetime.now()
        workout.duration_in_minutes = Timedelta2Minutes(workout.end_time - workout.timestamp)
    if (workout.comment is None):
        workout.comment = ""
    db_workout = models.Workout(
        timestamp           = workout.timestamp,
        duration_in_minutes = workout.duration_in_minutes,
        workout_type        = workout.workout_type,
        comment             = workout.comment,
        rating              = workout.rating
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

## Read

def get_workout(db: Session, workout_id: int):
    return db.query(models.Workout).filter(models.Workout.id == workout_id).first()

def get_workouts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Workout).offset(skip).limit(limit).all()

def get_workout_by_daterange(db: Session, start: date, end: date|None = None):
    if end is None:
        end = start
    return db.query(models.Workout).filter(
        and_(
            (start <= models.Workout.timestamp),
            (models.Workout.timestamp <= end)
        )).all()


## Update

## Delete


# Exercise

## Create

## Read

## Update

## Delete


# Set

## Create

## Read

## Update

## Delete


# EquipmentWeight

## Create

## Read

## Update

## Delete
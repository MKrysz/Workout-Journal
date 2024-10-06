from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date

from . import models, schemas


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

## Read

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
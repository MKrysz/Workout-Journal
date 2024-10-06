from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import relationship

from .database import Base

class Weight(Base):
    __tablename__ = "weights"
    id = Column(Integer, primary_key=True)

    weight = Column(Float)
    timestamp = Column(Date)

class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True)

    timestamp = Column(DateTime)
    duration_in_minutes = Column(Integer)
    workout_type = Column(String)
    comment = Column(String)
    rating = Column(Integer)

    sets = relationship("Set", back_populates="workout")

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True)

    name = Column(String)
    short_name = Column(String)
    weight_calc_method = Column(String)
    comment = Column(String)

    sets = relationship("Set", back_populates="exercise")

class Set(Base):
    __tablename__ = "sets"
    id = Column(Integer, primary_key=True)

    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    reps = Column(Integer)
    additional_weight = Column(Float)

    exercise = relationship("Exercise", back_populates="sets")
    workout = relationship("Workout", back_populates="sets")

class EquipmentWeight(Base):
    __tablename__ = "equipment_weights"
    id = Column(Integer, primary_key=True)

    timestamp = Column(Date)
    weight = Column(Float)
    name = Column(String)
    short_name = Column(String)

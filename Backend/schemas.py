from pydantic import BaseModel, ConfigDict
from datetime import datetime, date



class WeightBase(BaseModel):
    weight: float

class WeightCreate(WeightBase):
    timestamp: date | None = None

class Weight(WeightBase):
    id: int
    timestamp: date
    ConfigDict(from_attributes=True)



class WorkoutBase(BaseModel):
    timestamp: datetime
    workout_type: str | None = None
    comment: str
    duration_in_minutes: int
    rating: int | None = None

class WorkoutCreate(WorkoutBase):
    duration_in_minutes: int | None = None
    end_time: datetime | None = None
    comment: str | None = None

class Workout(WorkoutBase):
    id: int
    # sets: list[Set]

    ConfigDict(from_attributes=True)


class ExerciseBase(BaseModel):
    name: str
    weight_calc_method: str | None = None
    comment: str | None = None
    short_name : str

class ExerciseCreate(ExerciseBase):
    short_name : str | None = None

class Exercise(ExerciseBase):
    id: int
    # sets: list[Set]

    ConfigDict(from_attributes=True)



class SetBase(BaseModel):
    exercise_id: int
    workout_id: int
    reps: int
    additional_weight: float


class SetCreate(SetBase):
    reps: int | str

class Set(SetBase):
    id: int
    # sets: list[Set]

    ConfigDict(from_attributes=True)



class EquipmentWeightBase(BaseModel):
    timestamp: date
    weight: float
    name: str
    short_name: str


class EquipmentWeightCreate(EquipmentWeightBase):
    pass

class EquipmentWeight(EquipmentWeightBase):
    id: int
    # sets: list[Set]

    ConfigDict(from_attributes=True)
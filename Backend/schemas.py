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


# class WorkoutBase(BaseModel):
#     timestamp: datetime
#     wtype: str | None = None
#     comment: str | None = None

# class WorkoutCreate(WorkoutBase):
#     duration: int | None = None
#     end_time: datetime | None = None


# class Workout(WorkoutBase):
#     id: int
#     duration: int

#     class Config:
#         orm_mode = True
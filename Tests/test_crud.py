from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, datetime, timedelta
import pytest

from Backend.main import *
from Backend import models, schemas
from Backend.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="function", name="client")
def fixture_client():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


    Base.metadata.create_all(bind=engine)


    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client



#region Weight

# Create

def test__weight_write_return_200(client):
    w1 = schemas.WeightCreate(weight = 70, timestamp=date(2024, 10, 2))
    response = client.post("/weight", json=jsonable_encoder(w1))
    assert response.status_code == 200

def test__weight_write_check_database_reset(client):
    w1 = schemas.WeightCreate(weight = 70, timestamp=date(2024, 10, 2))
    response = client.post("/weight", json=jsonable_encoder(w1))
    assert response.status_code == 200

def test__weight_write(client):
    w1 = schemas.WeightCreate(weight = 70, timestamp=date(2024, 10, 2))
    response = client.post("/weight", json=jsonable_encoder(w1))
    assert response.status_code == 200
    result = schemas.Weight.model_validate(response.json())
    assert result.weight == w1.weight
    assert result.timestamp == w1.timestamp
    assert result.id == 1


def test__weight_write_same_date(client):
    w1 = schemas.WeightCreate(weight = 70, timestamp=date(2024, 10, 2))
    response = client.post("/weight", json=jsonable_encoder(w1))
    assert response.status_code == 200
    w1 = schemas.WeightCreate(weight = 71, timestamp=date(2024, 10, 2))
    response = client.post("/weight", json=jsonable_encoder(w1))
    assert response.status_code == 400 # timestamp must be unique

# Read

def test__weight_read_return_200(client):
    response = client.get("/weight")
    assert response.status_code == 200

def test__weight_read_by_range_only_start_return_200(client):
    response = client.get("/weight/?start=2020-07-17")
    assert response.status_code == 200

def test__weight_read_by_range_start_end_return_200(client):
    response = client.get("/weight/?start=2020-07-17&end=2034-01-09")
    assert response.status_code == 200


def test__weight_read_all(client):
    startW = 20
    for i in range(20):
        w1 = schemas.WeightCreate(weight = startW+i, timestamp=date(2024, 10, i+1))
        response = client.post("/weight", json=jsonable_encoder(w1))
        assert response.status_code == 200 # make sure weight_write worked
    response = client.get("/weight", params = {"limit":20})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 20
    results = [schemas.Weight.model_validate(x) for x in results]
    for i in range(20):
        result = results[i]
        assert result.weight == startW+i
        assert result.timestamp == date(2024, 10, i+1)
        assert result.id == i+1

def test__weight_read_by_id(client):
    weight_id = 2
    startW = 20
    for i in range(20):
        w1 = schemas.WeightCreate(weight = startW+i, timestamp=date(2024, 10, i+1))
        response = client.post("/weight", json=jsonable_encoder(w1))
        assert response.status_code == 200 # make sure weight_write worked
    response = client.get(f"/weight/{weight_id}")
    assert response.status_code == 200
    result = schemas.Weight.model_validate(response.json())
    assert result.weight == 21
    assert result.timestamp == date(2024, 10, 2)
    assert result.id == weight_id

def test__weight_read_by_date_single(client):
    startW = 20
    for i in range(20):
        w1 = schemas.WeightCreate(weight = startW+i, timestamp=date(2024, 10, i+1))
        response = client.post("/weight", json=jsonable_encoder(w1))
        assert response.status_code == 200 # make sure weight_write worked
    response = client.get(f"/weight/range/?start=2024-10-03")
    assert response.status_code == 200
    result = schemas.Weight.model_validate(response.json()[0])
    assert result.weight == 22
    assert result.timestamp == date(2024, 10, 3)
    assert result.id == 3

def test__weight_read_by_date_multiple(client):
    startW = 20
    for i in range(20):
        w1 = schemas.WeightCreate(weight = startW+i, timestamp=date(2024, 10, i+1))
        response = client.post("/weight", json=jsonable_encoder(w1))
        assert response.status_code == 200 # make sure weight_write worked
    response = client.get(f"/weight/range/?start=2024-10-02&end=2024-10-07")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 6
    results = [schemas.Weight.model_validate(x) for x in results]
    i = 1
    for result in results:
        assert result.id == i+1
        assert result.weight == startW+i
        assert result.timestamp == date(2024, 10, i+1)
        i +=1

# Update

# Delete

#endregion


#region Workout

# Create

def test__workout_write_return_200(client):
    w1 = schemas.WorkoutCreate(
        timestamp=datetime(2024, 10, 2, 16, 4),
        workout_type="Strength",
        comment="Feeling great",
        duration_in_minutes=119,
        rating=5
        )
    
    response = client.post("/workout", json=jsonable_encoder(w1))
    assert response.status_code == 200

def test__workout_write(client):
    w1 = schemas.WorkoutCreate(
        timestamp=datetime(2024, 10, 2, 16, 4),
        workout_type="Strength",
        comment="Feeling great",
        duration_in_minutes=119,
        rating=5
        )
    
    response = client.post("/workout", json=jsonable_encoder(w1))
    assert response.status_code == 200
    result = schemas.Workout.model_validate(response.json())
    assert result.id == 1
    assert result.workout_type == w1.workout_type
    assert result.comment == w1.comment
    assert result.duration_in_minutes == w1.duration_in_minutes
    assert result.timestamp == w1.timestamp
    assert result.rating == w1.rating


def test__workout_write_end_time_provided(client):
    w1 = schemas.WorkoutCreate(
        timestamp=datetime(2024, 10, 2, 16, 4),
        workout_type="Strenght",
        comment="Feeling great",
        end_time=datetime(2024, 10, 2, 18, 14),
        rating=5
        )
    response = client.post("/workout", json=jsonable_encoder(w1))
    assert response.status_code == 200
    result = schemas.Workout.model_validate(response.json())
    assert result.id == 1
    assert result.workout_type == w1.workout_type
    assert result.comment == w1.comment
    assert result.duration_in_minutes == 130
    assert result.timestamp == w1.timestamp
    assert result.rating == w1.rating

def test__workout_write_end_time_not_provided(client):
    w1 = schemas.WorkoutCreate(
        timestamp=datetime.now()-timedelta(minutes=145),
        workout_type="Strenght",
        comment="Feeling great",
        rating=5
        )
    response = client.post("/workout", json=jsonable_encoder(w1))
    assert response.status_code == 200
    result = schemas.Workout.model_validate(response.json())
    assert result.id == 1
    assert result.workout_type == w1.workout_type
    assert result.comment == w1.comment
    assert 146 >= result.duration_in_minutes >= 144 # to take into account api delay
    assert result.timestamp == w1.timestamp
    assert result.rating == w1.rating

def test__workout_write_comment_not_provided(client):
    w1 = schemas.WorkoutCreate(
        timestamp=datetime(2024, 10, 2, 16, 4),
        workout_type="Strenght",
        duration_in_minutes=119,
        rating=5
        )
    response = client.post("/workout", json=jsonable_encoder(w1))
    assert response.status_code == 200
    result = schemas.Workout.model_validate(response.json())
    assert result.id == 1
    assert result.workout_type == w1.workout_type
    assert result.comment == ""
    assert result.duration_in_minutes == w1.duration_in_minutes
    assert result.timestamp == w1.timestamp
    assert result.rating == w1.rating

def test__workout_write_rating_not_provided(client):
    w1 = schemas.WorkoutCreate(
        timestamp=datetime(2024, 10, 2, 16, 4),
        workout_type="Strenght",
        comment="Feeling great",
        duration_in_minutes=119
        )
    response = client.post("/workout", json=jsonable_encoder(w1))
    assert response.status_code == 200
    result = schemas.Workout.model_validate(response.json())
    assert result.id == 1
    assert result.workout_type == w1.workout_type
    assert result.comment == w1.comment
    assert result.duration_in_minutes == w1.duration_in_minutes
    assert result.timestamp == w1.timestamp
    assert result.rating is None

# Read

def test__workout_read_return_200(client):
    response = client.get("/workout")
    assert response.status_code == 200

def test__workout_read_by_range_only_start_return_200(client):
    response = client.get("/workout/?start=2020-07-17")
    assert response.status_code == 200

def test__workout_read_by_range_start_end_return_200(client):
    response = client.get("/workout/?start=2020-07-17&end=2034-01-09")
    assert response.status_code == 200

def test__workout_read_all(client):
    ws = []
    for i in range(20):
        w1 = schemas.WorkoutCreate(
            timestamp=datetime(2024, 10, i+1, 16, 5+i),
            workout_type = "Strength",
            comment="Feeling great",
            duration_in_minutes = 115+i,
            rating=4
        )
        response = client.post("/workout", json=jsonable_encoder(w1))
        assert response.status_code == 200
        ws.append(w1)
    response = client.get("/workout", params = {"limit":20})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 20
    results = [schemas.Workout.model_validate(x) for x in results]
    for i in range(20):
        result = results[i]
        w = ws[i]
        assert result.id == i+1
        assert result.workout_type == w.workout_type
        assert result.comment == w.comment
        assert result.duration_in_minutes == w.duration_in_minutes
        assert result.timestamp == w.timestamp
        assert result.rating == w.rating

# TODO: write actual response tests

# Update

# Delete

#endregion


#region Exercise

# Create

def test__exercise_write_return_200(client):
    w1 = schemas.ExerciseCreate(
        name="Pull-up",
        short_name="pullup",
        comment="Classical Pull-up exercise",
        weight_calc_method="uw" #user weight
        )
    
    response = client.post("/exercise", json=jsonable_encoder(w1))
    assert response.status_code == 200

def test__exercise_write(client):
    w1 = schemas.ExerciseCreate(
        name="Pull-up",
        short_name="pullup",
        comment="Classical Pull-up exercise",
        weight_calc_method="uw" #user weight
        )
    
    response = client.post("/exercise", json=jsonable_encoder(w1))
    assert response.status_code == 200

    result = schemas.Exercise.model_validate(response.json())
    assert result.id == 1
    assert result.name == w1.name
    assert result.short_name == w1.short_name
    assert result.weight_calc_method == w1.weight_calc_method

# error name not unique
# error short name not unique

# Read

def test__exercise_read(client):
    w1 = schemas.ExerciseCreate(
        name="Pull-up",
        short_name="pullup",
        comment="Classical Pull-up exercise",
        weight_calc_method="uw" #user weight
        )
    
    response = client.post("/exercise", json=jsonable_encoder(w1))
    assert response.status_code == 200

    response = client.get("/exercise/1")
    assert response.status_code == 200

    result = schemas.Exercise.model_validate(response.json())
    assert result.id == 1
    assert result.name == w1.name
    assert result.short_name == w1.short_name
    assert result.weight_calc_method == w1.weight_calc_method

# read exercises
# read by name
# read by shortname

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


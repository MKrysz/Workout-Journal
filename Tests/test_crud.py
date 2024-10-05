from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, datetime
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

def test__weight_write_return_200(client):
    w1 = schemas.WeightCreate(weight = 70, timestamp=date(2024, 10, 2))
    response = client.post("/weight", json=jsonable_encoder(w1))
    assert response.status_code == 200

def test__weight_write_check_database_reset(client):
    w1 = schemas.WeightCreate(weight = 70, timestamp=date(2024, 10, 2))
    response = client.post("/weight", json=jsonable_encoder(w1))
    assert response.status_code == 200

def test__weight_read_return_200(client):
    response = client.get("/weight")
    assert response.status_code == 200

def test__weight_write(client):
    w1 = schemas.WeightCreate(weight = 70, timestamp=date(2024, 10, 2))
    response = client.post("/weight", json=jsonable_encoder(w1))
    assert response.status_code == 200
    result = schemas.Weight.parse_obj(response.json())
    assert result.weight == w1.weight
    assert result.timestamp == w1.timestamp
    assert result.id == 1

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
    results = [schemas.Weight.parse_obj(x) for x in results]
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
    result = schemas.Weight.parse_obj(response.json())
    assert result.weight == 21
    assert result.timestamp == date(2024, 10, 2)
    assert result.id == weight_id

def test__weight_read_by_date_single(client):
    startW = 20
    for i in range(20):
        w1 = schemas.WeightCreate(weight = startW+i, timestamp=date(2024, 10, i+1))
        response = client.post("/weight", json=jsonable_encoder(w1))
        assert response.status_code == 200 # make sure weight_write worked
    response = client.get(f"/weight/range/?start=2024-10-3")
    assert response.status_code == 200
    result = schemas.Weight.parse_obj(response.json()[0])
    assert result.weight == 22
    assert result.timestamp == date(2024, 10, 3)
    assert result.id == 3

def test__weight_read_by_date_multiple(client):
    startW = 20
    for i in range(20):
        w1 = schemas.WeightCreate(weight = startW+i, timestamp=date(2024, 10, i+1))
        response = client.post("/weight", json=jsonable_encoder(w1))
        assert response.status_code == 200 # make sure weight_write worked
    response = client.get(f"/weight/range/?start=2024-10-2&end=2024-10-7")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 6
    results = [schemas.Weight.parse_obj(x) for x in results]
    i = 1
    for result in results:
        assert result.id == i+1
        assert result.weight == startW+i
        assert result.timestamp == date(2024, 10, i+1)
        i +=1

import pytest
from datetime import datetime, timedelta
from random import randint
from Database.dbm import *

def test_Timedelta2Minutes_less_than_minute():
    x = timedelta(seconds=50)
    y = 0
    assert Timedelta2Minutes(x) == y

def test_Timedelta2Minutes_less_exactly_one_minute():
    x = timedelta(minutes=1)
    y = 1
    assert Timedelta2Minutes(x) == y

def test_Timedelta2Minutes_a_little_more_than_one_minute():
    x = timedelta(minutes=1, seconds=2)
    y = 1
    assert Timedelta2Minutes(x) == y

    x = timedelta(seconds=119)
    y = 1
    assert Timedelta2Minutes(x) == y

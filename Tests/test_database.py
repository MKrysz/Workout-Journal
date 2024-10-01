import pytest
import os
from datetime import datetime, timedelta
from random import randint
from Database.dbm import *

class TestDatabase:

    def setup_method(self, method):
        self.db = Database("Tests/test_db.db", False)
        self.db.create()
    
    def teardown_method(self, method):
        self.db.__del__()
        os.remove("Tests/test_db.db")
    

    def test_weight_insert_read_normal(self):
        assert True

    
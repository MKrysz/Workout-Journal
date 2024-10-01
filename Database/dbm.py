#!/bin/env python

import sqlite3
import argparse
import os
from datetime import datetime, timedelta

# Utility functions
def Timedelta2Minutes(duration):
    return int(duration.total_seconds()/60)


class Database:
    def __init__(self, filename=None, autoconnect=True):

        if(filename is None): # normal operation
            self.db_name = "Database/database.db"
        else: # for testing purposes
            self.db_name = filename

        if (not autoconnect): # for creating database
            return

        if(not os.path.isfile(self.db_name)):
            raise ValueError("Could not find database")

        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    # TODO: document weightCalcMethod syntax - python syntax with predifined variables
    def exercise_insert(self, name, weightCalcMethod=None, shortName=None, comments=None):
        insertQuery = """
            INSERT INTO Exercises (NAME, WEIGHTCALCMETHOD, SHORTNAME, COMMENTS)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(insertQuery, (name, weightCalcMethod, shortName, comments))


    def equipementWeight_insert(self, name, weigh, shortName, timestamp):

        if(isinstance(timestamp, str)):
            timestamp = datetime.strptime(timestamp, "%d/%m/%y")

        insertQuery = """
            INSERT INTO EquipementWeights (NAME, WEIGHT, SHORTNAME, TIMESTAMP)
            VALUES (?, ?, ?, ?)
        """

        self.cursor.execute(insertQuery, (name, weigh, shortName, timestamp))

    def weight_insert(self, weight, timestamp):

        if(isinstance(timestamp, str)):
            timestamp = datetime.strptime(timestamp, "%d/%m/%y")

        insertQuery = """
            INSERT INTO Weight (WEIGHT, TIMESTAMP)
            VALUES (?, ?)
        """
        self.cursor.execute(insertQuery, (weight, timestamp))

    def parse_weight_calc_function(self, function):
        result = ""
        state = "wait" # other = "var"
        for c in function:
            # ? means invalid function
            if c == "?":
                return "1" 
            if c not in (" +-/*().%0123456789"):
                if state == "wait":
                    state = "var"
                    result += "variables['"
            else:
                if state == "var":
                    state = "wait"
                    result += "']"
            result += c
        return result


    def workout_insert(self, timestamp=None, duration=None, comment=None, type=None):

        if(isinstance(timestamp, str)):
            if(':' in timestamp):
                timestamp = datetime.strptime(timestamp, "%d/%m/%y %H:%M")
            else:
                timestamp = datetime.strptime(timestamp, "%d/%m/%y")


        if(isinstance(duration, str)):
            duration = datetime.strptime(duration, "%H:%M")
            duration = duration.minute + 60*duration.hour
        
        if(isinstance(duration, timedelta)):
            print("works")
            duration = Timedelta2Minutes(duration)

        insertQuery = """
            INSERT INTO Workouts (TIMESTAMP, DURATION_MINUTES, COMMENT, TYPE)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(insertQuery, (timestamp, duration, comment, type))

    def get_exercise_id(self, name=None):
        queryName = """
            SELECT id FROM Exercises WHERE name = ?
        """
        querySName = """
            SELECT id FROM Exercises WHERE shortName = ?
        """

        self.cursor.execute(queryName, [name])

        result = self.cursor.fetchall()

        if(len(result) == 1):
            return result[0][0]
        elif(len(result) >= 1):
            print(result)
            raise ValueError("exercise name is not unique?")


        self.cursor.execute(querySName, [name])

        result = self.cursor.fetchall()

        if(len(result) == 1):
            return result[0][0]
        elif(len(result) >= 1):
            print(result)
            raise ValueError("exercise name is not unique?")

        
        raise ValueError("exercise name not found")

    def get_workout(self, workout_id):
        query = """
            SELECT * FROM Workouts WHERE id = ?
        """
        self.cursor.execute(query, [workout_id])
        result = self.cursor.fetchall()
        return result[0]

    def get_exercise(self, exercise_id):
        query = """
            SELECT * FROM Exercises WHERE id = ?
        """
        self.cursor.execute(query, [exercise_id])
        result = self.cursor.fetchall()
        return result[0]

    def get_latest_wid(self):
        query = """
            SELECT MAX(id) FROM Workouts
        """
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result[0][0]


    def load_variables(self, timestamp):
        query = """
            SELECT * FROM Weight 
            WHERE timestamp <= ?
            ORDER BY timestamp
        """

        variables = {
            "uw" : 0
        }

        self.cursor.execute(query, [timestamp])
        result = self.cursor.fetchall()

        variables["uw"] = (result[-1][1])

        # some evil SQL magic
        # https://stackoverflow.com/questions/64058351/return-the-most-recent-record-only-if-a-query-results-in-records-having-the-same
        query = """ 
            SELECT EW1.* FROM [EquipementWeights] AS EW1
            INNER JOIN (
                SELECT name, MAX(timestamp) AS NewestVals FROM [EquipementWeights] WHERE timestamp <= ? GROUP BY name
            ) AS EW2 ON (EW1.name = EW2.name AND EW1.timestamp = EW2.NewestVals)
        """

        self.cursor.execute(query, [timestamp])
        result = self.cursor.fetchall()

        for row in result:
            variables[row[4]] = row[1]

        return variables

    def calculate_volume(self, exercise_id, workout_id, nr_of_reps, addWeight):

        timestamp = self.get_workout(workout_id)[1]
        variables = self.load_variables(timestamp)
        variables["aw"] = addWeight
        function = self.parse_weight_calc_function(self.get_exercise(exercise_id)[3]+" ")
        return nr_of_reps * eval(function)
        


    def set_insert(self, exercise_id=None, workout_id=None, nr_of_reps=None, addWeight=None, exercise_name=None):

        if(exercise_id is None):
            exercise_id = self.get_exercise_id(exercise_name)

        # TODO: add volume calculation after whole workout is finished

        insertQuery = """
            INSERT INTO Sets (exercise_id, workout_id, nr_of_reps, addWeight)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(insertQuery, (exercise_id, workout_id, nr_of_reps, addWeight))


    def create(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Create tables

        self.cursor.execute("""
            CREATE TABLE Sets (
                id INTEGER PRIMARY KEY,
                
                exercise_id INTEGER,
                workout_id INTEGER,

                nr_of_reps INTEGER,
                addWeight REAL,
                volume REAL

            );""")

        self.cursor.execute("""
            CREATE TABLE Workouts (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME,
                duration_minutes INTEGER,
                type CHAR(32),
                comment VARCHAR
            );""")

        self.cursor.execute("""
            CREATE TABLE Exercises (
                id INTEGER PRIMARY KEY,
                name CHAR(64),
                shortName CHAR(32),
                weightCalcMethod CHAR(128),
                comments VARCHAR
            );""")
        
        self.cursor.execute("""
            CREATE TABLE Weight (
                id INTEGER PRIMARY KEY,
                weight REAL,
                timestamp DATETIME
            );""")

        self.cursor.execute("""
            CREATE TABLE EquipementWeights (
                id INTEGER PRIMARY KEY,
                weight REAL,
                timestamp DATETIME,
                name CHAR(64),
                shortName CHAR(32)
        );""")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")

    args = parser.parse_args()

    db = Database()

    match args.command:
        case init:
            pass
    print("Exiting...")


if __name__ == "__main__":
    main()

# used only while MVP is being developed
# TODO: Delete me after
def populate_default_data(db: Database):
    # Populate default data

    db.equipementWeight_insert("EZ Barbell",       3.0, "ezBar", "28/05/24")
    db.equipementWeight_insert("One Hand Barbell", 0.7, "OHBar", "01/05/24")

    db.weight_insert(70.2, "10/09/23")
    db.weight_insert(70.8, "24/09/23")
    db.weight_insert(70.8, "15/10/23")
    db.weight_insert(70.2, "22/10/23")
    db.weight_insert(72.8, "29/10/23")
    db.weight_insert(71.0, "12/11/23")
    db.weight_insert(71.3, "19/11/23")
    db.weight_insert(72.3, "26/11/23")
    db.weight_insert(70.6, "14/01/24")
    db.weight_insert(72.3, "21/01/24")
    db.weight_insert(72.0, "28/01/24")
    db.weight_insert(72.0, "04/02/24")
    db.weight_insert(72.0, "11/02/24")
    db.weight_insert(72.7, "18/02/24")
    db.weight_insert(70.6, "03/03/24")
    db.weight_insert(73.1, "19/05/24")
    db.weight_insert(72.7, "26/05/24")
    db.weight_insert(71.6, "02/06/24")
    db.weight_insert(73.1, "19/05/24")
    db.weight_insert(72.7, "26/05/24")
    db.weight_insert(71.6, "02/06/24")
    db.weight_insert(72.1, "10/09/24")
    db.weight_insert(72.1, "11/09/24")
    db.weight_insert(72.1, "13/09/24")
    db.weight_insert(72.2, "14/09/24")
    db.weight_insert(72.2, "28/09/24")
    db.weight_insert(72.6, "29/09/24")

    db.exercise_insert("pullup",                   weightCalcMethod="uw + aw")
    db.exercise_insert("pushup",                   weightCalcMethod="0.7*uw+0.9*aw",  comments="Volume calculation measured empirically")
    db.exercise_insert("plank",                    weightCalcMethod="0.7*uw+0.9*aw",   comments="Reps measure duration in seconds\n" )
    db.exercise_insert("dip",                      weightCalcMethod="uw + aw")
    db.exercise_insert("ez bicep curl",            weightCalcMethod="aw+ezBar",       shortName="ez curl")
    db.exercise_insert("bicep curl both",          weightCalcMethod="aw+2*OHBar",     shortName="curl b")
    db.exercise_insert("pullup biceps",            weightCalcMethod="uw+aw",          shortName="pullup b")

    db.exercise_insert("single calf raise",        weightCalcMethod="2*(uw+aw+OHBar)",shortName="s calf r")
    db.exercise_insert("calf raise",               weightCalcMethod="uw+aw+2*OHBar",  shortName="calf r")
    db.exercise_insert("inverted row",             weightCalcMethod="0",              shortName="inv row")
    db.exercise_insert("squat",                    weightCalcMethod="0")
    db.exercise_insert("lying leg raise",          weightCalcMethod="0",              shortName="l leg r")
    db.exercise_insert("leg raise",                weightCalcMethod="0",              shortName="leg r")
    db.exercise_insert("knee raise",               weightCalcMethod="0",              shortName="knee r")
    db.exercise_insert("step up",                  weightCalcMethod="0")


    db.workout_insert(timestamp="6/5/24", comment="Testing new barbells for home gym", type="Strenght")
    db.set_insert(exercise_name="bicep curl both", workout_id=1, nr_of_reps=12, addWeight=12.0)

    db.workout_insert(timestamp="10/5/24", comment="Testing new pullup bar in home gym", type="Strenght")
    db.set_insert(exercise_name="pullup", workout_id=2, nr_of_reps=5, addWeight=0.0)

    db.workout_insert(timestamp="11/5/24", comment="First workout in home gym", type="Strenght")
    db.set_insert(exercise_name="pullup",   workout_id=3, nr_of_reps=9,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=3, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=3, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=3, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=3, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="curl b", workout_id=3, nr_of_reps=4,  addWeight=12.0)
    db.set_insert(exercise_name="curl b", workout_id=3, nr_of_reps=3,  addWeight=12.0)
    db.set_insert(exercise_name="plank",    workout_id=3, nr_of_reps=70, addWeight=0.0 )
    db.set_insert(exercise_name="pullup b", workout_id=3, nr_of_reps=3,  addWeight=0.0 )

    db.workout_insert(timestamp="15/5/24", type="Strenght")
    db.set_insert(exercise_name="pullup",   workout_id=4, nr_of_reps=7,  addWeight=0.0 )

    db.workout_insert(timestamp="18/5/24", type="Strenght")
    db.set_insert(exercise_name="pullup",   workout_id=5, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=5, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=5, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=5, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=5, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="leg r",    workout_id=5, nr_of_reps=1,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup b", workout_id=5, nr_of_reps=1,  addWeight=0.0 )

    db.workout_insert(timestamp="20/5/24", type="Strenght")
    db.set_insert(exercise_name="pullup",   workout_id=6, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=6, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=6, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=6, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=6, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=6, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=6, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=6, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=6, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=6, nr_of_reps=2,  addWeight=0.0 )

    db.workout_insert(timestamp="22/5/24", type="Strenght")
    db.set_insert(exercise_name="pullup",   workout_id=7, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=7, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=7, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=7, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=7, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=7, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=7, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=7, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=7, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=7, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=7, nr_of_reps=20, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=7, nr_of_reps=20, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=7, nr_of_reps=20, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=7, nr_of_reps=20, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=7, nr_of_reps=20, addWeight=0.0 )

    db.workout_insert(timestamp="24/5/24", type="Strenght")
    db.set_insert(exercise_name="pullup",   workout_id=8, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=8, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=8, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=8, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=8, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=8, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=8, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=8, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=8, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=8, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=8, nr_of_reps=22, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=8, nr_of_reps=22, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=8, nr_of_reps=22, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=8, nr_of_reps=22, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=8, nr_of_reps=22, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=8, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=8, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=8, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=8, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=8, nr_of_reps=10, addWeight=0.0 )


    db.workout_insert(timestamp="27/5/24", type="Strenght")
    db.set_insert(exercise_name="pullup",   workout_id=9, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=9, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=9, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=9, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=9, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=9, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=9, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=9, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=9, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=9, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=9, nr_of_reps=23, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=9, nr_of_reps=23, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=9, nr_of_reps=23, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=9, nr_of_reps=23, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=9, nr_of_reps=23, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=9, nr_of_reps=15, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=9, nr_of_reps=15, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=9, nr_of_reps=15, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=9, nr_of_reps=15, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=9, nr_of_reps=15, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=9, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=9, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=9, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=9, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=9, nr_of_reps=60, addWeight=0.0 )
    
    db.workout_insert(timestamp="29/5/24", type="Strenght", comment="A little stressed out")
    db.set_insert(exercise_name="pullup",   workout_id=10, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=10, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=10, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pushup",   workout_id=10, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="pushup",   workout_id=10, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="pushup",   workout_id=10, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=10, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=10, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=10, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=10, nr_of_reps=24, addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=10, nr_of_reps=24, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=10, nr_of_reps=15, addWeight=5.0 )
    db.set_insert(exercise_name="s calf r", workout_id=10, nr_of_reps=15, addWeight=5.0 )
    db.set_insert(exercise_name="plank",    workout_id=10, nr_of_reps=70, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=10, nr_of_reps=70, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=10, nr_of_reps=70, addWeight=0.0 )
    db.set_insert(exercise_name="ez curl",  workout_id=10, nr_of_reps=8,  addWeight=20.0 )
    db.set_insert(exercise_name="ez curl",  workout_id=10, nr_of_reps=8,  addWeight=20.0 )
    db.set_insert(exercise_name="ez curl",  workout_id=10, nr_of_reps=8,  addWeight=20.0 )
    
    db.workout_insert(timestamp="31/5/24", type="Strenght", comment="Didn't finish last workout - no new exercises\nNo squats after all-day bike trip\nAlmost sprang my ankle during knee raises\nPlank hurts")
    db.set_insert(exercise_name="pullup",   workout_id=11, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=11, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=11, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=11, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pullup",   workout_id=11, nr_of_reps=6,  addWeight=0.0 )
    db.set_insert(exercise_name="pushup",   workout_id=11, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="pushup",   workout_id=11, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="pushup",   workout_id=11, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="pushup",   workout_id=11, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="pushup",   workout_id=11, nr_of_reps=10, addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=11, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=11, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=11, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=11, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=11, nr_of_reps=3,  addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=11, nr_of_reps=15, addWeight=7.0 )
    db.set_insert(exercise_name="s calf r", workout_id=11, nr_of_reps=15, addWeight=7.0 )
    db.set_insert(exercise_name="s calf r", workout_id=11, nr_of_reps=15, addWeight=7.0 )
    db.set_insert(exercise_name="s calf r", workout_id=11, nr_of_reps=15, addWeight=7.0 )
    db.set_insert(exercise_name="plank",    workout_id=11, nr_of_reps=70, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=11, nr_of_reps=70, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=11, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=11, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=11, nr_of_reps=42, addWeight=0.0 )
    db.set_insert(exercise_name="ez curl",  workout_id=11, nr_of_reps=8,  addWeight=20.0 )
    db.set_insert(exercise_name="ez curl",  workout_id=11, nr_of_reps=8,  addWeight=20.0 )
    db.set_insert(exercise_name="ez curl",  workout_id=11, nr_of_reps=8,  addWeight=20.0 )
    db.set_insert(exercise_name="ez curl",  workout_id=11, nr_of_reps=8,  addWeight=20.0 )
    db.set_insert(exercise_name="ez curl",  workout_id=11, nr_of_reps=8,  addWeight=20.0 )

    db.workout_insert(timestamp="10/6/24", type="Strenght", comment="Didn't feel like doing plank today\nNeed to check proper inv row technique")
    for i in range(5):
        db.set_insert(exercise_name="pullup",   workout_id=12, nr_of_reps=6,  addWeight=0.0 )
        db.set_insert(exercise_name="pushup",   workout_id=12, nr_of_reps=10, addWeight=0.0 )
        db.set_insert(exercise_name="ez curl",  workout_id=12, nr_of_reps=8,  addWeight=20.0)
        db.set_insert(exercise_name="s calf r", workout_id=12, nr_of_reps=12, addWeight=9.0 )
        db.set_insert(exercise_name="dip",      workout_id=12, nr_of_reps=4,  addWeight=0.0 )
        db.set_insert(exercise_name="squat",    workout_id=12, nr_of_reps=12, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=12, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=12, nr_of_reps=15, addWeight=0.0 )

    db.workout_insert(timestamp="12/6/24 17:09", type="Strenght", comment="In a hurry - dropping some exercises")
    for i in range(5):
        db.set_insert(exercise_name="pullup",   workout_id=13, nr_of_reps=6,  addWeight=0.0 )
        db.set_insert(exercise_name="ez curl",  workout_id=13, nr_of_reps=8,  addWeight=20.0)
        db.set_insert(exercise_name="dip",      workout_id=13, nr_of_reps=4,  addWeight=0.0 )
    for i in range(3):
        db.set_insert(exercise_name="pushup",   workout_id=13, nr_of_reps=11, addWeight=0.0 )
        db.set_insert(exercise_name="l leg r",  workout_id=13, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=13, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=13, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=13, nr_of_reps=30, addWeight=0.0 )
    db.set_insert(exercise_name="s calf r", workout_id=13, nr_of_reps=12, addWeight=11.0)
    db.set_insert(exercise_name="inv row",  workout_id=13, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="inv row",  workout_id=13, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="inv row",  workout_id=13, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="squat",    workout_id=13, nr_of_reps=12, addWeight=0.0 )

    db.workout_insert(timestamp="14/6/24 16:06", duration="1:22", type="Strenght")
    for i in range(5):
        db.set_insert(exercise_name="pullup",   workout_id=14, nr_of_reps=7,  addWeight=0.0 )
        db.set_insert(exercise_name="pushup",   workout_id=14, nr_of_reps=11, addWeight=0.0 )
        db.set_insert(exercise_name="l leg r",  workout_id=14, nr_of_reps=6,  addWeight=0.0 )
        db.set_insert(exercise_name="ez curl",  workout_id=14, nr_of_reps=8,  addWeight=20.0)
        db.set_insert(exercise_name="calf r",   workout_id=14, nr_of_reps=12, addWeight=18.0)
        db.set_insert(exercise_name="step up",  workout_id=14, nr_of_reps=12, addWeight=0.0 )
        db.set_insert(exercise_name="dip",      workout_id=14, nr_of_reps=5,  addWeight=0.0 )
        db.set_insert(exercise_name="inv row",  workout_id=14, nr_of_reps=6,  addWeight=0.0 )
        db.set_insert(exercise_name="squat",    workout_id=14, nr_of_reps=12, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=14, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=14, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=14, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=14, nr_of_reps=45, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=14, nr_of_reps=35, addWeight=0.0 )

    db.workout_insert(timestamp="15/6/24",type="Test")
    db.set_insert(exercise_name="pullup",    workout_id=15, nr_of_reps=12, addWeight=0.0 )

    db.workout_insert(timestamp="17/6/24 18:39", duration="1:11",type="Strenght", comment="In a hurry, meeting at work")
    wid = 16
    for i in range(5):
        db.set_insert(exercise_name="pullup",   workout_id=wid, nr_of_reps=7,  addWeight=0.0 )
        db.set_insert(exercise_name="l leg r",  workout_id=wid, nr_of_reps=7,  addWeight=0.0 )
        db.set_insert(exercise_name="ez curl",  workout_id=wid, nr_of_reps=9,  addWeight=20.0)
    for i in range(4):
        db.set_insert(exercise_name="pushup",   workout_id=wid, nr_of_reps=12, addWeight=0.0 )
        db.set_insert(exercise_name="inv row",  workout_id=wid, nr_of_reps=7,  addWeight=0.0 )
        db.set_insert(exercise_name="calf r",   workout_id=wid, nr_of_reps=12, addWeight=18.0)
        db.set_insert(exercise_name="step up",  workout_id=wid, nr_of_reps=12, addWeight=9.0 )
        db.set_insert(exercise_name="dip",      workout_id=wid, nr_of_reps=5,  addWeight=0.0 )
    db.set_insert(exercise_name="dip",      workout_id=wid, nr_of_reps=4,  addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=wid, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=wid, nr_of_reps=60, addWeight=0.0 )
    db.set_insert(exercise_name="plank",    workout_id=wid, nr_of_reps=50, addWeight=0.0 )

    db.workout_insert(timestamp="24/6/24 16:00", duration="1:40",type="Strenght", comment="Training with Jas")
    wid = 17
    for i in range(5):
        db.set_insert(exercise_name="pullup",   workout_id=wid, nr_of_reps=7,  addWeight=0.0 )
        db.set_insert(exercise_name="pushup",   workout_id=wid, nr_of_reps=12, addWeight=0.0 )
        db.set_insert(exercise_name="l leg r",  workout_id=wid, nr_of_reps=7,  addWeight=0.0 )
        db.set_insert(exercise_name="ez curl",  workout_id=wid, nr_of_reps=9,  addWeight=20.0)
        db.set_insert(exercise_name="dip",      workout_id=wid, nr_of_reps=5,  addWeight=0.0 )
        db.set_insert(exercise_name="inv row",  workout_id=wid, nr_of_reps=7,  addWeight=0.0 )
    for i in range(4):
        db.set_insert(exercise_name="plank",    workout_id=wid, nr_of_reps=60, addWeight=0.0 )
        db.set_insert(exercise_name="step up",  workout_id=wid, nr_of_reps=12, addWeight=9.0 )
        db.set_insert(exercise_name="dip",      workout_id=wid, nr_of_reps=5,  addWeight=0.0 )
        db.set_insert(exercise_name="squat",    workout_id=wid, nr_of_reps=12,  addWeight=0.0 )
    for i in range(3):
        db.set_insert(exercise_name="calf r",   workout_id=wid, nr_of_reps=12, addWeight=18.0)


    print("Database initialized!")

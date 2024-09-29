from flask import Flask, render_template, request

from datetime import datetime

from Database.dbm import *

app = Flask(__name__)


# allows for use of comma (,) as decimal separator
def str2float(x:str):
    return float(x.replace(',', '.'))

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/add-weight')
def addWeight():
    weight = request.args.get('weight')
    if(weight is not None):
        weight = str2float(weight)
        db = Database()
        db.weight_insert(weight, datetime.now())
    return render_template('add-weight.html', weight=weight)

@app.route('/routine')
def routine():
    step = request.args.get('step')
    if(step is None):
        db = Database()
        routine.wid = db.get_latest_wid()+1
        return render_template('routine-start.html')
    if(step == "last"):
        comment = request.args.get('comment')
        db = Database()
        db.workout_insert(timestamp=routine.start_time, duration=datetime.now()-routine.start_time, comment=comment, type="Strengh")
        return render_template('routine-end.html')
    step = int(step)
    if(step == 0):
        routine.start_time = datetime.now()
    if(step != 0):
        exercise = request.args.get('exercise')
        reps = int(request.args.get('reps'))
        addWeight = str2float(request.args.get('addWeight'))
        db = Database()
        db.set_insert(workout_id=routine.wid, nr_of_reps=reps, addWeight=addWeight, exercise_name=exercise)
    
    return render_routine(step)

def render_routine(step):
    nr_of_sets = 5
    exercises = ["pullup", "pushup", "lying leg raise", "ez curl", 
                 "calf raise", "step up", "dip", "inverted row", "squat"]
    nr_of_exercises = len(exercises)

    if(step >= nr_of_exercises*nr_of_sets):
        return render_template('routine-last.html')
    exercise = exercises[step%nr_of_exercises]
    return render_template('routine-step.html', step=step, exercise=exercise)
    

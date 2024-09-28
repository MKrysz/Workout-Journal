from flask import Flask, render_template, request
app = Flask(__name__)

# allows for use of comma (,) as decimal separator
def str2float(x:str):
    return float(x.replace(',', '.'))

@app.route('/')
def index():
    return 'Index Page'

@app.route('/add-weight')
def addWeight():
    weight = request.args.get('weight')
    if(weight is not None):
        weight = str2float(weight)
    return render_template('add-weight.html', weight=weight)
from soarspy import app
from flask import render_template, redirect

@app.route('/')
def index():
    return redirect("/airplanes")


@app.route('/airplanes')
def airplanes():
    return render_template("airplanes.html")
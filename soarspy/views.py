import re

from soarspy import app, glidernet_db
from flask import render_template, redirect, request


@app.route('/')
def index():
    return redirect("/flight-days")


@app.route('/flight-days')
def airplanes():
    template_vars = {"flight_days": glidernet_db.list_flight_days()}

    date = request.args.get('date')

    if date is not None and re.match('^(\\d\\d\\d\\d)-(\\d\\d)-(\\d\\d)$', date) is not None:
        db = glidernet_db.load_flight_day(date)
        template_vars['airplanes'] = db.get_airplanes()
        print(type(template_vars['airplanes'][0]['last_seen'].tzinfo))

    return render_template("flight_days.html", **template_vars)

from flask import render_template, request, redirect, url_for, g, session, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload
from model.base_solidary import get_base_solidary_items, calculate_base_solidary, get_pivot_table, make_document
import time


@app.route('/show_solidary')
@login_required
def view_show_solidary():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']

    log.info(f"SHOW SOLIDARY. SCENARIO: {scenario}")
    if scenario=='':
        return redirect(url_for('view_root'))

    rows = get_base_solidary_items(scenario)
    log.debug(f"------->\n\tSHOW BASE_SOLIDARY\n\tROWS:\n\t{rows}\n<-------")
    return render_template('calc_base_solidary.html', rows=rows)


@app.route('/calculate_base_solidary', methods=['GET','POST'])
@login_required
def view_calc_solidary():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
        calculate_base_solidary(session['scenario'])

    rows = get_base_solidary_items(scenario)

    log.debug(f"------->CALC PENS. START\nROWS: {rows}\n<-------")
    return render_template("partials/_base_solidary_fragment.html", rows=rows)


@app.route('/print_base_solidary', methods=['GET','POST'])
@login_required
def view_print_solidary():
    format_type = request.args.get("format", "excel")

    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']

    return make_document(scenario, format_type)


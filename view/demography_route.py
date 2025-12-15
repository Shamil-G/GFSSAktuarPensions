from flask import render_template, request, redirect, url_for, g, session, jsonify
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload
from model.calc_pens import get_pens_items, calculate_in_db, get_pivot_table, make_document
import time


@app.route('/show_demography')
@login_required
def view_show_demography():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        log.info(f"SHOW DEMOGRAPHY. NOT FOUND SCENARIO: {scenario}")
        return redirect(url_for('view_root'))
    log.info(f'*** view_show_demography. scenario: {scenario}')

    # (grouped_columns, rows )=get_pens_items(scenario, filter)
    # log.debug(f"------->VIEW SHOW DEMOGRAPHY. \n{grouped_columns}\nROWS: {rows}\n<-------")
    return render_template('demography.html')
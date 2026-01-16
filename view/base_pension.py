from flask import render_template, request, redirect, url_for, g, session, jsonify, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload
from model.base_pension import get_base_items, get_base_pension_excel, calculate_base_pension_in_db
import time

@app.route('/show_base')
@login_required
def view_show_base_pension():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        return redirect(url_for('view_root'))

    log.info(f"VIEW SHOW BASE SOLIDARY. SCENARIO: {scenario}")

    rows, columns = get_base_items(scenario)
    log.debug(f"------->\n\tVIEW SHOW BASE SOLIDARY\n\tROWS:\n\t{rows}\n<-------")
    return render_template('base_pension.html', rows=rows, columns=columns)


@app.route('/show-base-pension-fragment', methods=['GET','POST'])
@login_required
def view_base_pension_fragment():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        return redirect(url_for('view_root'))

    log.info(f"VIEW SHOW BASE PENSION FRAGMENT. SCENARIO: {scenario}")

    rows, columns = get_base_items(scenario)
    return render_template('partials/_base_pension_fragment.html', rows=rows, columns=columns)


@app.route('/get_base_pension_excel')
@login_required
def view_get_base_pension_excel():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        return redirect(url_for('view_root'))

    params = {'user_top_control': g.user.top_control, 'user_dep_name': g.user.dep_name, 'user_rfbn': g.user.rfbn_id, 'scenario': scenario }
    log.info(f"--->\n\tVIEW GET EXCEL\n\tPARAMS: {params}\n<---")
    return get_base_pension_excel(params)


# в base_pension.html :
# data-work-url="/calculate_base_pension"
# /calculate_base_pension - указываем celery что надо вызвать 
# Сам CELERY вызывается JS через 
# data-action="/start_task_calculate_base_pension"
# Этот URL находится в view.celery_task_route.py
@app.route('/calculate_base_pension', methods=['POST'])
# @login_required
def view_calc_base_pension():
    data = extract_payload()

    scenario = data.get("scenario",'')

    if scenario=='':
        log.info(f"VIEW CALC PENS. NOT FOUND SCENARIO")
        return jsonify({'status': 'fail', 'message': 'SCENARIO is EMPTY'})

    log.info(f"CALCULATE_PENS. scenario: {scenario}")

    calculate_base_pension_in_db(scenario)

    return jsonify({'status': 'success'})

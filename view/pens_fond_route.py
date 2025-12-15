from flask import render_template, request, redirect, url_for, g, session, jsonify
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload
from model.calc_pens import get_pens_items, calculate_in_db, get_pivot_table, make_document
import time


@app.route('/show_pens')
@login_required
def view_show_pens():
    filter=session.get('pens_filter', '1=1')
    year_filter=session.get('year_filter','')
    ids_filter=session.get('ids_filter','')

    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        log.info(f"SHOW PENS. NOT FOUND SCENARIO: {scenario}")
        return redirect(url_for('view_root'))
    log.info(f'*** view_show_pens. scenario: {scenario}, ids_flter: {ids_filter}, year_filter: {year_filter}')

    (grouped_columns, rows )=get_pens_items(scenario, filter)
    log.debug(f"------->VIEW SHOW PENS FOND. \n{grouped_columns}\nROWS: {rows}\n<-------")
    return render_template('calc_pens.html', columns=grouped_columns, rows=rows, year_filter=year_filter, ids_filter=ids_filter)


@app.route('/show-pens-fragment', methods=['GET','POST'])
@login_required
def view_pens_by_filter():
    filter=session.get('pens_filter', '1=1')

    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        log.info(f"SHOW PENS. NOT FOUND SCENARIO: {scenario}")
        return redirect(url_for('view_root'))

    (grouped_columns, rows )=get_pens_items(scenario, filter)
    return render_template("partials/_calc_pens_fragment.html", columns=grouped_columns, rows=rows)

# /calculate_pens גûחûגאועסÿ CELERY (celery_taks.py) קונוח גûחמג
# def celery_calc_pens(taskName, scenario, value, work_url):
# ג ךמעמנמי  work_url=/calculate_pens
@app.route('/calculate_pens', methods=['POST'])
# @login_required
def view_calc_pens():
    data = extract_payload()

    scenario = data.get("scenario",'')
    filter = data.get("value",'')

    log.info(f'VIEW CALC PENS: {data}, filter: {filter}')

    if scenario=='':
        log.info(f"VIEW CALC PENS. NOT FOUND SCENARIO")
        return jsonify({'status': 'fail', 'message': 'SCENARIO is EMPTY'})

    if filter=='':
        log.info(f"SHOW PENS. NOT FOUND FILTER")
        return jsonify({'status': 'fail', 'message': 'FILTER is EMPTY'})

    log.info(f"CALCULATE_PENS. scenario: {scenario}, filter: {filter}")

    calculate_in_db(scenario, filter)

    return jsonify({'status': 'success'})


@app.route('/print_pens', methods=['GET','POST'])
@login_required
def view_print_pens():
    format_type = request.args.get("format", "excel")
    value = request.args.get("value")

    data = extract_payload()

    scenario = data.get("scenario",'')
    filter = data.get("value",'')

    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
        return jsonify({'status': 'fail', 'message': 'SCENARIO is EMPTY'})

    if filter=='':
        log.info(f"SHOW PENS. NOT FOUND FILTER")
        return jsonify({'status': 'fail', 'message': 'FILTER is EMPTY'})

    filter=''
    if value=='filter':
        filter=session.get('pens_filter', '1=2')    
        calculate_in_db(value, filter)
    if value=='all':
        filter=session.get('pens_filter', '1=2')    

    else:
        return redirect(url_for('view_root'))

    return make_document(scenario, filter, format_type)


@app.route('/filter-pens-year', methods=['GET','POST'])
@login_required
def view_pens_year():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        return redirect(url_for('view_root'))

    data = extract_payload()
    year = data.get('value', '')
    session['year_filter']=year

    filter='1=1'
    if not year:
        log.info(f"FILTER_PENS_YEAR. YEAR is EMPTY")
    else:
        filter = f"extract(year from birth_date)={year}"
    
    session['pens_filter']=filter

    log.debug(f"FILTER_PENS_ID\n\tMETHOD: {request.method}\n\tscenario: {scenario}\n\tIDS: {year}\n\tfilter:{filter}")

    (grouped_columns, rows)=get_pens_items(scenario, filter)
    return render_template("partials/_calc_pens_fragment.html", columns=grouped_columns, rows=rows)


@app.route('/filter-pens-id', methods=['GET','POST'])
@login_required
def view_pens_id():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        return redirect(url_for('view_root'))

    data = extract_payload()
    ids = data.get('value', '')
    session['ids_filter']=ids

    filter='1=1'
    if not ids:
        log.info(f"FILTER_PENS_ID. IDS is EMPTY")
    else:
        filter = f"ids like '{ids}%'"
    
    session['pens_filter']=filter

    log.debug(f"FILTER_PENS_ID\n\tMETHOD: {request.method}\n\tscenario: {scenario}\n\tIDS: {ids}\n\tfilter:{filter}")

    (grouped_columns, rows )=get_pens_items(scenario, filter)
    return render_template("partials/_calc_pens_fragment.html", columns=grouped_columns, rows=rows)

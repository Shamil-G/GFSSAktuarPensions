from flask import render_template, request, redirect, url_for, g, session, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload
from model.calc_pens import get_pens_items, calculate_in_db, get_pivot_table, make_document
import io


@app.route('/show_pens')
@login_required
def view_show_pens():
    filter=session.get('pens_filter', '1=1')
    (grouped_columns, rows )=get_pens_items(filter)
    log.debug(f"------->CALC PENS. START\n{grouped_columns}\nROWS: {rows}\n<-------")
    return render_template('calc_pens.html', columns=grouped_columns, rows=rows)


@app.route('/calculate_pens', methods=['GET','POST'])
@login_required
def view_calc_pens():
    data = extract_payload()
    value = data.get('value', '')

    filter=''
    if value=='filter':
        filter=session.get('pens_filter', '1=2')    
        calculate_in_db(value, filter)
    if value=='all':
        filter=session.get('pens_filter', '1=1')    
        # calculate_in_db(value, filter)

    log.info(f"CALCULATE_PENS. value: {value}, filter: {filter}")

    (grouped_columns, rows )=get_pens_items(filter)

    log.debug(f"------->CALC PENS. START\n{grouped_columns}\nROWS: {rows}\n<-------")
    return render_template("partials/_calc_pens_fragment.html", columns=grouped_columns, rows=rows)


@app.route('/print_pens', methods=['GET','POST'])
@login_required
def view_print_pens():
    format_type = request.args.get("format", "excel")
    value = request.args.get("value")

    filter=''
    if value=='filter':
        filter=session.get('pens_filter', '1=2')    
        calculate_in_db(value, filter)
    if value=='all':
        filter=session.get('pens_filter', '1=2')    

    return make_document(filter, format_type)


@app.route('/filter-pens-year', methods=['GET','POST'])
@login_required
def view_pens_year():
    data = extract_payload()
    year = data.get('value', '')
    if not year:
        log.info(f"FILTER_PENS_YEAR. YEAR is EMPTY")
        return '', 200

    filter = f"extract(year from birth_date)={year}"
    session['pens_filter']=filter

    log.info(f"FILTER_PENS_YEAR\n\tMETHOD: {request.method}\n\tEXTRACTED DATA: {data}")
    (grouped_columns, rows)=get_pens_items(filter)
    return render_template("partials/_calc_pens_fragment.html", columns=grouped_columns, rows=rows)


@app.route('/filter-pens-id', methods=['GET','POST'])
@login_required
def view_pens_id():
    data = extract_payload()
    ids = data.get('value', '')
    if not ids:
        log.info(f"FILTER_PENS_ID. IDS is EMPTY")
        return '', 200

    log.info(f"FILTER_PENS_ID\n\tMETHOD: {request.method}\n\tEXTRACTED DATA: {data}")
    filter = f"ids like '{ids}%'"
    session['pens_filter']=filter

    (grouped_columns, rows )=get_pens_items(filter)
    return render_template("partials/_calc_pens_fragment.html", columns=grouped_columns, rows=rows)


@app.route('/filter-pens-period', methods=['GET','POST'])
@login_required
def view_pens_period():
    data = extract_payload()
    ref_year = data.get('value', '')
    log.info(f"FILTER_PENS_PERIOD\n\tMETHOD: {request.method}\n\tEXTRACTED DATA: {data}")

    (grouped_columns, rows )=get_pens_items(ref_year)
    return render_template("partials/_calc_pens_fragment.html", columns=grouped_columns, rows=rows)

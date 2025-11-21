from flask import render_template, request, redirect, url_for, g, session
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload

from model.big_ref import get_big_ref_items, get_unique_big_ref_name, save_ref_value

@app.route('/big_ref')
def view_big_ref():
    list_val=get_big_ref_items('')
    list_name=get_unique_big_ref_name()
    log.debug(f"BIG_REF. START\n{list_val}")
    return render_template(f'big_ref.html', list_val=list_val, list_name=list_name)


@app.route('/filter-ref-name', methods=['GET','POST'])
@login_required
def view_pretrial_fragment():
    data = extract_payload()
    ref_name = data.get('value', '')
    log.info(f"FILTER-REF-NAME FIRST HIT\n\tMETHOD: {request.method}\n\tEXTRACTED DATA: {data}")

    list_items=get_big_ref_items(ref_name) if ref_name else []
    return render_template("partials/_big_ref_fragment.html", list_val=list_items)


@app.route('/save-ref-value', methods=['GET','POST'])
@login_required
def view_save_ref_value():
    data = extract_payload()
    ref_name = data.get('id', '')
    ref_year = data.get('year', '')
    ref_value = data.get('value', '')
    log.info(f"FILTER-REF-NAME FIRST HIT\n\tMETHOD: {request.method}\n\tEXTRACTED DATA: {data}")

    save_ref_value(ref_name, ref_year, ref_value)
    return {'status': 200}


@app.route('/help_fragment')
def help_fragment():
    topic = request.args.get('topic')
    log.info(f"HELP. TOPIC: {topic}")
    return render_template(f'helper/_help_{topic}.html')
from flask import render_template, request, redirect, url_for, g, session, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload
from model.base import get_base_items
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
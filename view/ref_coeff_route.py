from flask import render_template, request,  redirect, url_for, g, session
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload

from model.coeff_ref import get_coeff_items, save_coeff_value

@app.route('/coeff_ref')
@login_required
def view_ref_coeff():
    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        return redirect(url_for('view_root'))
    
    list_val=get_coeff_items(scenario)
    log.debug(f"COEFF_REF. START\n{list_val}")
    return render_template('coefficients.html', list_val=list_val)


@app.route('/save-coeff-value', methods=['GET','POST'])
@login_required
def view_save_coeff_value():
    data = extract_payload()
    ref_name = data.get('id', '')
    ref_value = data.get('value', '')
    log.info(f"VIEW SAVE COEFF VALUE\n\tMETHOD: {request.method}\n\tEXTRACTED DATA: {data}")

    scenario=''
    if 'scenario' in session:
        scenario=session['scenario']
    else:
        return redirect(url_for('view_root'))

    save_coeff_value(scenario, ref_name, ref_value)
    return {'status': 200}

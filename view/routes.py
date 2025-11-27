from flask import render_template, request, redirect, url_for, g, session
from flask_login import login_user
import requests

from main_app import app, log
from util.i18n import get_i18n_value
from app_config import styles, sso_server
from sso.sso_login import SSO_User
from util.ip_addr import ip_addr

# from view.routes_overpayments import *
from view.ref_route import *
from view.ref_coeff_route import *
from view.calc_pens_route import *

from reports.get_summary_01 import  make_report_summary_01

log.info("Routes стартовал...")


@app.context_processor
def utility_processor():
    if 'style' not in session:
        session['style']=styles[0]    
        log.debug(f'------- CP\n\tSET SESSION STYLE: {session['style']}\n------')

    log.debug(f"CONTEXT PROCESSOR. APP_NAME {get_i18n_value('APP_NAME')}")
    return dict(res_value=get_i18n_value)


@app.route('/about')
def about():
    return render_template("about.html")


def try_auto_login():
    req_json = {'ip_addr': f'{ip_addr()}'}
    resp = requests.post(url=f'{sso_server}/check', json=req_json)
    log.debug(f'LOGIN CHECK. \n\taddr: {sso_server}/check\n\tresp: {resp}')
    if resp.status_code == 200:
        resp_json=resp.json()
        log.debug(f'LOGIN GET. resp_json: {resp_json}')
        if 'status' in resp_json and resp_json['status'] == 200:
            json_user = resp_json['user']
            log.info(f'LOGIN GET. json_user: {json_user}')
            session['username'] = json_user['login_name']
            user = SSO_User().get_user_by_name(json_user)
            login_user(user)
        else:
            log.info(f'----------------\n\tUSER {ip_addr()} not Registred\n----------------')
            return render_template('login.html')


@app.route('/')
def view_root():
    if not g or g.user.is_anonymous:
        # LOGIN with session variable
        log.info(f'User is anonymous ...')
        try_auto_login()
        if 'to-do' not in session:
            session['to-do'] = 'active'
        log.info("--------> Now will go to LIST_OVERPAYMENTS")
        # return redirect(url_for('view_root'))
    return render_template("index.html")


@app.route('/change-style')
def change_style():
    if 'style' in session:
        for style in styles:
            if style!=session['style']:
                session['style']=style
                break
    else: 
        session['style']=styles[0]
    # Получим предыдущую страницу, чтобы на неё вернуться
    current_page = request.referrer
    log.debug(f"Set style {session['style']}. Next page: {current_page}")
    if current_page is not None:
        return redirect(current_page)
    else:
        return redirect(url_for('view_root'))


@app.route('/language/<string:lang>')
def set_language(lang):
    log.debug(f"Set language. LANG: {lang}, предыдущий язык: {session['language']}")
    session['language'] = lang
    # Получим предыдущую страницу, чтобы на неё вернуться
    current_page = request.referrer
    log.debug(f"Set LANGUAGE. {current_page}")
    if current_page is not None:
        return redirect(current_page)
    else:
        return redirect(url_for('view_root'))


@app.route('/reports', methods=['GET'])
@app.route('/reports/<report_name>', methods=['GET'])
@login_required
def view_reports(report_name=None):

    log.info(f'VIEW REPORTS. START {report_name}')
    match report_name:
        case 'summary_01':  
            return make_report_summary_01()
        case _: 
            log.info(f'VIEW REPORTS. CASE DEFAULT')

    log.info(f'VIEW REPORTS. FINISH')
    # return render_template("index.html")
    return render_template("reports.html")

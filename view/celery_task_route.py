from __init__ import app, log
from celery_app import celery
from flask import jsonify, session
from model.celery_tasks import celery_calc_pens 
from util.functions import extract_payload


@app.route('/start_task_calculate_pens', methods=['POST'])
def start_task():
    payload = extract_payload()
    taskName = payload.get("taskName",'')
    value = payload.get("value",'')
    work_url = payload.get("work_url",'')
    scenario = payload.get("scenario",'')

    filter=''
    pens_filter=session.get('pens_filter','1=1')
    ids_filter=session.get('ids_filter','')
    if value=='all': filter='1=1'
    else: 
        if 'extract' in pens_filter:
            filter=pens_filter
        if 'like' in pens_filter and ids_filter!='':
            filter=f'ids = {ids_filter}'
    if filter=='':
        filter='1=1'

    log.info(f'START_TASK. scenario: {session['scenario']}, value: {value}, filter: {filter}, work_url: {work_url}')

    log.info(f'START_TASK. PAYLOAD: {payload}')
    log.info(f'START_TASK. TASK_NAME: {taskName}, scenario: {scenario}, value: {value}, work_url: {work_url}')
    i = celery.control.inspect()
    i_list = i.active()
    i_reg = i.registered()


    log.info(f"Активные воркеры: {i_list}")       # список активных задач
    log.info(f"Зарегистрированные воркеры: {i_reg}")  # список известных задач

    if(scenario!='' and filter!=''):
        task = celery_calc_pens.apply_async(args=[taskName, scenario, filter, work_url])
        log.info(f"TASK: {task} started")  
        return jsonify({"taskName": taskName, "status": "started"})
    return jsonify({"task_id": taskName, "status": "fail"})




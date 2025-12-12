from __init__ import socketio
from main_app import log, host, port
from flask import jsonify
from celery_app import celery
import requests


@celery.task
def celery_calc_pens(taskName, scenario, value, work_url):
    base_url=f'http://{host}:{port}{work_url}'
    log.info(f'*** CELERY_CALC_PENS. TASK_NAME: {taskName}, scenario: {scenario}, value: {value}, work_url: {work_url}')
    resp = requests.post(base_url, json={'scenario': scenario, "value": value})
    
    log.info(f"*** CELERY_CALC_PENSю Response status: {resp.status_code}, headers: {resp.headers}, body: {resp.text}")
    
    try:
        result = resp.json()
    except:
        log.error("Ответ не JSON, raw: %s", resp.text)
        result = {"status": "error", "raw": resp.text}

    socketio.emit('task_finished', {
        'task_id': celery_calc_pens.request.id,
        'taskName': taskName,
        'result': result
    })
    return result

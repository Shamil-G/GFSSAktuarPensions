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
    
    log.info(f"*** CELERY_CALC_PENS. Response status: {resp.status_code}, headers: {resp.headers}, body: {resp.text}")
    
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

# Регистрирует функцию как Celery‑задачу
@celery.task
def celery_calc_base_pension(taskName, scenario, work_url):
    base_url=f'http://{host}:{port}{work_url}'
    log.info(f'*** CELERY_CALC_BASE_PENSION. TASK_NAME: {taskName}, scenario: {scenario}, work_url: {work_url}')
    # Делаем POST запрос
    resp = requests.post(base_url, json={'scenario': scenario})
    
    log.info(f"*** CELERY_CALC_BASE_PENSION. Response status: {resp.status_code}, headers: {resp.headers}, body: {resp.text}")
    
    try:
        result = resp.json()
    except:
        log.error("Ответ не JSON, raw: %s", resp.text)
        result = {"status": "error", "raw": resp.text}

    log.info(f"*** CELERY_CALC_BASE_PENSION. REQUEST: {celery_calc_base_pension.request}")
    # отправляем событие 'task_finished'
    # task_id	ID Celery‑задачи
    # celery_calc_base_pension - сама celery задача
    # .request - контекст выполнения задачи
    # внутри request есть:
    #   id - ид задачи
    #   args - аргументы
    #   kwargs - именованный аргументы
    #   retries - сколько раз перезапускалась
    #   hostname - какой worker выполняет
    socketio.emit('task_finished', {
        'task_id': celery_calc_base_pension.request.id,
        'taskName': taskName,
        'result': result
    })
    return result


# Регистрирует функцию как Celery‑задачу
@celery.task
def celery_calc_solidary_pension(taskName, scenario, work_url):
    base_url=f'http://{host}:{port}{work_url}'
    log.info(f'*** CELERY_CALC_SOLIDARY_PENSION. TASK_NAME: {taskName}, scenario: {scenario}, work_url: {work_url}')
    # Делаем POST запрос
    resp = requests.post(base_url, json={'scenario': scenario})
    
    log.info(f"*** CELERY_CALC_BASE_PENSION. Response status: {resp.status_code}, headers: {resp.headers}, body: {resp.text}")
    
    try:
        result = resp.json()
    except:
        log.error("Ответ не JSON, raw: %s", resp.text)
        result = {"status": "error", "raw": resp.text}

    log.info(f"*** CELERY_CALC_SOLIDARY_PENSION. REQUEST: {celery_calc_base_pension.request}")
    # отправляем событие 'task_finished'
    # task_id	ID Celery‑задачи
    # celery_calc_base_pension - сама celery задача
    # .request - контекст выполнения задачи
    # внутри request есть:
    #   id - ид задачи
    #   args - аргументы
    #   kwargs - именованный аргументы
    #   retries - сколько раз перезапускалась
    #   hostname - какой worker выполняет
    socketio.emit('task_finished', {
        'task_id': celery_calc_solidary_pension.request.id,
        'taskName': taskName,
        'result': result
    })
    return result
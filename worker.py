from gfss_parameter import platform
from celery_app import celery
from view.celery_task_route import celery_calc_pens

if __name__ == "__main__":
    if platform!='unix':
        celery.worker_main(argv=['worker', '--loglevel=INFO', '--pool=solo'])
    else:
        celery.worker_main(argv=['worker', '--loglevel=INFO'])

import multiprocessing
from gfss_parameter import app_home, app_name
from app_config import port

bind = f"localhost:{port}"
workers = multiprocessing.cpu_count()*2+1
worker_class = "sync"
chdir = f"{app_home}/{app_name}"
wsgi_app = "main_app:app"
loglevel = 'info'

access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"  "%(a)s"'
accesslog = "logs/court-gunicorn-access.log"
error_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"  "%(a)s"'
errorlog = "logs/court-gunicorn-error.log"
<<<<<<< HEAD
proc_name = 'PENS-GFSS'
=======
proc_name = 'GFSS-AKTUAR-PENSION'
>>>>>>> 2f92b950ce37c53aebb27ca598b1d0cd6764c100
# Перезапуск после N кол-во запросов
max_requests = 10000
# Перезапуск, если ответа не было более 60 сек
timeout = 180
# umask or -m 007
umask = 0x007
# Проверка IP адресов, с которых разрешено обрабатывать набор безопасных заголовков
#preload увеличивает производительность - хуже uwsgi!
preload_app = True

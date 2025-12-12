from celery import Celery
from configparser import ConfigParser

config = ConfigParser()
config.read('db_config.ini')
redis_config = config['db_redis']
redis_host=redis_config['host']
redis_url=f'{redis_host}/0'

celery = Celery(__name__, broker='redis_url', backend='redis_url')

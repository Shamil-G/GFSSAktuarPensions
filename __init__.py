from gfss_parameter import app_name, platform
from configparser import ConfigParser
from flask_login import LoginManager
from flask import Flask
from flask_socketio import SocketIO
from redis import from_url
from util.logger import log
from os import getenv
from secrets import token_hex
from celery_app import celery, redis_url

app = Flask(__name__, template_folder='templates', static_folder='static')

# Для куки нужен криптографический ключ
app.secret_key = getenv('SECRET_KEY', default=token_hex())

login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message = "Необходимо зарегистрироваться в системе"
login_manager.login_message_category = "warning"

print('START __INIT__.py')

socketio = SocketIO(app, cors_allowed_origins="*", message_queue=redis_url)

app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 36000

app.config['broker_url'] = redis_url
app.config['result_backend'] = redis_url

# socketio = SocketIO(app, cors_allowed_origins="*", message_queue=redis_url)

app.config.update(
    broker_url=redis_url,
    result_backend=redis_url,
    SESSION_PERMANENT=False,
    PERMANENT_SESSION_LIFETIME=36000,
    SESSION_TYPE="redis",
    SESSION_REDIS=from_url(redis_url),
)

celery.conf.update(app.config)

# if platform!='unix' and redis_url:
#     # app.config['SESSION_TYPE']  = 'filesystem'
#     app.config['SESSION_TYPE'] = 'redis'
#     app.config['SESSION_REDIS'] = from_url(redis_url)
# else:
#     # app.config['SESSION_TYPE']  = 'filesystem'
#     app.config['SESSION_TYPE'] = 'redis'
#     app.config['SESSION_REDIS'] = from_url(redis_url)

# Автоматическая регистрация точки входа
# app.add_url_rule('/login', 'login', ldap.login, methods=['GET', 'POST'])

log.info(f"__INIT__ for {app_name} started")

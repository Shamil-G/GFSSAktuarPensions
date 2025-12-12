# python -m venv venv

<<<<<<< HEAD
#call C:\Projects\GFSSAktuarPensions\venv\Scripts\activate.bat
. /home/pens/GFSSAktuarPensions/venv/bin/activate

python -m pip install --upgrade pip
pip install --upgrade pip
#pip install ldap3

gunicorn
#python main_app.py
#gunicorn -w 2 -b 0.0.0.0:5081 main_app:app
#gunicorn -w 2 --preload main_app:app
#gunicorn -w 2 -k sync main_app:app
=======
call C:\Projects\GFSSAktuarPensions\venv\Scripts\activate.bat
rem . /home/pens/GFSSAktuarPensions/venv/bin/activate

rem python -m pip install --upgrade pip
rem pip install --upgrade pip
rem pip3 install celery
rem # python main_app.py
celery -A main_app.celery worker --loglevel=INFO --logfile=celery.log
>>>>>>> 8f186bbcc887653a4095dcc3d4128f54d19fa765

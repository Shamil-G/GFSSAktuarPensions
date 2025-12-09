# python -m venv venv

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
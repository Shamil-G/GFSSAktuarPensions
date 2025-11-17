# python -m venv venv

#call C:\Projects\Aktuar_2021\venv\Scripts\activate.bat
. /home/aktuar/Aktuar_2021/venv/bin/activate

python -m pip install --upgrade pip
pip install --upgrade pip
pip install ldap3

# gunicorn
python main_app.py

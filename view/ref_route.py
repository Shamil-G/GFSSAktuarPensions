from flask import render_template, request, redirect, url_for, g, session
from flask_login import login_required
from main_app import app, log
import json

from model.big_ref import get_big_ref_items

@app.route('/big_ref')
def view_big_ref():
    list_val=get_big_ref_items('')
    log.info(f"BIG_REF. START\n{list_val}")
    return render_template(f'big_ref.html', list_val=list_val)


def extract_payload():
    content_type = request.headers.get('Content-Type', '')
    print("📥 Content-Type:", content_type)

    if 'application/json' in content_type:
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            return data
        else:
            print("⚠️ JSON не распарсен, пробуем вручную")
            try:
                return json.loads(request.data.decode('utf-8'))
            except Exception as e:
                print("❌ Ошибка при ручном JSON-декодировании:", e)
                return {}
    elif 'application/x-www-form-urlencoded' in content_type:
        return request.form.to_dict()
    else:
        print("⚠️ Неизвестный Content-Type, пробуем как JSON")
        try:
            return json.loads(request.data.decode('utf-8'))
        except Exception:
            return {}


@app.route('/big_ref_fragment', methods=['GET','POST'])
@login_required
def view_pretrial_fragment():
    if request.method=='POST':
        data = extract_payload()
        order_num = data.get('order_num', '')
    else:
        order_num = request.args.get('order_num','')

    pretrial_items = get_pretrial_items(order_num) if order_num else []
    log.debug(f"PRETRIAL_FRAGMENT\n\tORDER_NUM: {order_num}\n\tPRETRIAL_ITEMS: {pretrial_items}")
    return render_template("partials/_pretrial_fragment.html", pretrial_items=pretrial_items, selected_order=order_num)



@app.route('/help_fragment')
def help_fragment():
    topic = request.args.get('topic')
    log.info(f"HELP. TOPIC: {topic}")
    return render_template(f'helper/_help_{topic}.html')
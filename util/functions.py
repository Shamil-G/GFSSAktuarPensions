from flask import request
import json
from util.logger import log


def extract_payload():
    if request.method == 'GET':
        return request.args.to_dict()

    content_type = request.headers.get('Content-Type', '')
    log.info(f"📥 Content-Type: {content_type}")

    if 'application/json' in content_type:
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            return data
        else:
            log("⚠️ JSON не распарсен, пробуем вручную")
            try:
                return json.loads(request.data.decode('utf-8'))
            except Exception as e:
                log(f"❌ Ошибка при ручном JSON-декодировании: {e}" )
                return {}
    elif 'application/x-www-form-urlencoded' in content_type:
        return request.form.to_dict()
    else:
        log.info(f"⚠️ Неизвестный Content-Type: {content_type}, пробуем как JSON")
        try:
            return json.loads(request.data.decode('utf-8'))
        except Exception:
            return {}
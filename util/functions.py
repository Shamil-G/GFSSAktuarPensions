from flask import request
import json

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
        print(f"⚠️ Неизвестный Content-Type: {content_type}, пробуем как JSON")
        try:
            return json.loads(request.data.decode('utf-8'))
        except Exception:
            return {}
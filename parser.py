import requests
import base64
import urllib.parse
import os
from datetime import datetime

# Твои источники
SOURCES = [
    "https://sub.obbhod.online/premium",
    "https://gitverse.ru/api/repos/bezlista/bezlista_mirror/raw/branch/master/conf1g.txt",
    "https://raw.githubusercontent.com/Temnuk/naabuzil/refs/heads/main/whitelist",
    "https://gist.githubusercontent.com/pythoneer-dev-q/49c33dd8d4e279611e30a8c6fd938230/raw/mobile.txt",
    "https://mygala.ru/vpn/premium.php"
]

def clean_vless(key):
    """Оставляет только основу ключа vless://... для удаления дублей"""
    key = key.strip()
    if '#' in key:
        return key.split('#')[0]
    return key

def get_keys():
    raw_keys = []
    for url in SOURCES:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                raw_data = resp.text.strip()
                try:
                    # Исправляем padding и декодируем Base64 подписки
                    missing_padding = len(raw_data) % 4
                    if missing_padding:
                        raw_data += '=' * (4 - missing_padding)
                    content = base64.b64decode(raw_data).decode('utf-8')
                except:
                    content = raw_data
                
                raw_keys.extend(content.strip().split('\n'))
        except Exception as e:
            print(f"Ошибка на {url}: {e}")

    unique_keys = set()
    for k in raw_keys:
        cleaned = clean_vless(k)
        if cleaned.startswith('vless://'):
            unique_keys.add(cleaned)
            
    return sorted(list(unique_keys))

def update_file():
    new_keys = get_keys()
    if not new_keys:
        print("Ключи не найдены. Обновление отменено.")
        return

    timestamp = datetime.now().strftime("%d.%m %H:%M")

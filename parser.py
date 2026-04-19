import requests
import base64
import urllib.parse
import os
from datetime import datetime

# Твои источники
SOURCES = [
    "http://sub.obbhod.online/premium",
    "https://gitverse.ru/api/repos/bezlista/bezlista_mirror/raw/branch/master/conf1g.txt",
    "https://gist.githubusercontent.com/pythoneer-dev-q/49c33dd8d4e279611e30a8c6fd938230/raw/mobile.txt",
    "https://raw.githubusercontent.com/btsk161/Freeinternet_byMygalaru.github.io/refs/heads/main/premium.txt",
    "https://raw.githubusercontent.com/prominbro/sub/refs/heads/main/212.txt"
]

def clean_vless(key):
    """Оставляет только основу ключа для удаления дублей"""
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
                    # Декодируем, если это Base64 подписка
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

    # Формируем заголовок по твоему запросу
    header = (
        "#profile-title: ⚪WHITELIST ⚪\n"
        "#announce: Данная подписка собрана из других подписок(подробнее в readme),просьба не путать с авторскими!\n"
        "#profile-update-interval: 1\n"
        "\n"  # Отступ
    )
    
    numbered_keys = []
    for i, key in enumerate(new_keys, 1):
        try:
            parsed_url = urllib.parse.urlparse(key)
            params = urllib.parse.parse_qs(parsed_url.query)
            sni_value = params.get('sni', ['Sni отсутствует!'])[0]
        except:
            sni_value = "Ошибка парсинга"
            
        numbered_keys.append(f"{key}#[{i}] {sni_value}")
    
    output_content = header + "\n".join(numbered_keys)

    # Проверка на изменения
    if os.path.exists("results.txt"):
        with open("results.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Пропускаем заголовок (первые 4 строки) при сравнении ключей
            old_keys = [l.strip().split('#')[0] for l in lines[4:] if l.strip()]
            
        if old_keys == new_keys:
            print("Изменений в ключах нет. Пропускаем коммит.")
            return

    with open("results.txt", "w", encoding="utf-8") as f:
        f.write(output_content)
    print(f"Обновлено! Собрано ключей: {len(new_keys)}")

if __name__ == "__main__":
    update_file()

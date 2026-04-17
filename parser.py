import requests
import base64
from datetime import datetime
import os

# Твои актуальные источники
SOURCES = [
    "https://sub.obbhod.online/premium",
    "https://gitverse.ru/api/repos/bezlista/bezlista_mirror/raw/branch/master/conf1g.txt",
    "https://raw.githubusercontent.com/Temnuk/naabuzil/refs/heads/main/whitelist",
    "https://gist.githubusercontent.com/pythoneer-dev-q/49c33dd8d4e279611e30a8c6fd938230/raw/mobile.txt",
    "https://mygala.ru/vpn/premium.php"
]

def clean_vless(key):
    """Убирает всё после # и лишние пробелы"""
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
                    # Фикс padding для base64
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
        print("Ключи не найдены.")
        return

    timestamp = datetime.now().strftime("%d.%m %H:%M")
    
    # Делаем описание подписки через #
    # В клиентах это отобразится как имя профиля
    subscription_name = f"# Sub Update: {timestamp} | Total: {len(new_keys)}"
    
    output_content = f"{subscription_name}\n" + "\n".join(new_keys)

    if os.path.exists("results.txt"):
        with open("results.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Пропускаем первую строку (описание) при сравнении ключей
            old_keys = [l.strip() for l in lines[1:] if l.strip()]
            
        if old_keys == new_keys:
            print("База ключей не изменилась. Пропускаем.")
            return

    with open("results.txt", "w", encoding="utf-8") as f:
        f.write(output_content)
    print(f"Обновлено! Ключей: {len(new_keys)}")

if __name__ == "__main__":
    update_file()

import requests
import base64
from datetime import datetime
import os

SOURCES = [
    "https://example.com/subscribe1",
    "https://raw.githubusercontent.com/user/repo/main/sub"
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

    # Основная магия: чистим каждый ключ от комментариев и удаляем дубликаты
    unique_keys = set()
    for k in raw_keys:
        cleaned = clean_vless(k)
        if cleaned.startswith('vless://'): # Можно добавить vmess:// и т.д.
            unique_keys.add(cleaned)
            
    return sorted(list(unique_keys))

def update_file():
    new_keys = get_keys()
    if not new_keys:
        print("Ключи не найдены. Выходим.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Добавляем в комментарий время и количество для инфы
    header = f"// Last Update: {timestamp} | Unique keys: {len(new_keys)}\n"
    output_content = header + "\n".join(new_keys)

    # Сравнение со старым файлом
    if os.path.exists("results.txt"):
        with open("results.txt", "r", encoding="utf-8") as f:
            old_lines = f.readlines()
            old_keys = [l.strip() for l in old_lines[1:] if l.strip()]
            
        if old_keys == new_keys:
            print("Ничего нового. Скипаем коммит.")
            return

    with open("results.txt", "w", encoding="utf-8") as f:
        f.write(output_content)
    print(f"Готово! Сохранено {len(new_keys)} чистых ключей.")

if __name__ == "__main__":
    update_file()

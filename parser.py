import requests
import base64
import urllib.parse
import os
import ipaddress
import socket

# Твои источники
SOURCES = [
    "http://sub.obbhod.online/premium",
    "https://gist.githubusercontent.com/pythoneer-dev-q/49c33dd8d4e279611e30a8c6fd938230/raw/mobile.txt",
    "https://raw.githubusercontent.com/btsk161/Freeinternet_byMygalaru.github.io/refs/heads/main/premium.txt",
    "https://accargame.cfd/sub/vvyXOgJw_dbFCJgn"
    ]

def get_flag(code):
    """Генерирует эмодзи флага из кода страны (например, RU -> 🇷🇺)"""
    if not code or code == "??" or len(code) != 2: 
        return "🏳️"
    # Магия Unicode: превращаем буквы в символы региональных индикаторов
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)

def get_geo_info(address):
    """Резолвит IP, фильтрует локальный мусор и тянет страну"""
    try:
        # Пытаемся получить IP из домена
        ip = socket.gethostbyname(address)
        ip_obj = ipaddress.ip_address(ip)
        
        # Полная защита от 0.0.0.0, 127.0.0.1 и приватных подсетей (192.168.x.x)
        if not ip_obj.is_global or ip_obj.is_unspecified:
            return None, None

        # Запрос к API (лимит 45/мин, для 500 конфигов хватит за глаза)
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success':
                code = data.get('countryCode', '??')
                return code, get_flag(code)
    except:
        pass
    return "??", "🏳️"

def get_keys():
    raw_keys = []
    # Мобильный User-Agent, чтобы не палиться перед Cloudflare
    headers = {'User-Agent': 'Mozilla/5.0 (Android 14; Mobile; rv:128.0) Gecko/128.0 Firefox/128.0'}
    
    for url in SOURCES:
        try:
            resp = requests.get(url, timeout=15, headers=headers)
            if resp.status_code == 200:
                data = resp.text.strip()
                try:
                    # Чиним Base64 если нужно
                    pad = len(data) % 4
                    if pad: data += '=' * (4 - pad)
                    content = base64.b64decode(data).decode('utf-8')
                except:
                    content = data
                raw_keys.extend(content.strip().split('\n'))
        except:
            continue

    unique = set()
    for k in raw_keys:
        k = k.strip()
        if k.startswith('vless://'):
            # Отрезаем всё после #, чтобы убрать старые названия из источников
            clean_link = k.split('#')[0]
            unique.add(clean_link)
    return sorted(list(unique))

def update_file():
    keys = get_keys()
    if not keys:
        print("Ключи не найдены.")
        return

    header = (
        "#profile-title: ⚪WHITELIST ⚪\n"
        "#announce: Данная подписка собирается из других, просьба не путать с авторскими!!\n"
        "#profile-update-interval: 1\n\n"
    )
    
    final_configs = []
    print(f"Парсим гео для {len(keys)} конфигов...")

    for i, key in enumerate(keys, 1):
        try:
            parsed = urllib.parse.urlparse(key)
            code, flag = get_geo_info(parsed.hostname)
            
            # Если это 0.0.0.0 — просто выкидываем этот ключ
            if code is None:
                continue
            
            params = urllib.parse.parse_qs(parsed.query)
            sni = params.get('sni', ['no-sni'])[0]
            
            # Тот самый формат: [33] RU🇷🇺 | SNI: pornhub.com
            name = f"[{i}] {code}{flag} | SNI: {sni}"
            final_configs.append(f"{key}#{name}")
        except:
            continue

    with open("results.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n".join(final_configs))
    
    print(f"Готово! Сохранено: {len(final_configs)}")

if __name__ == "__main__":
    update_file()

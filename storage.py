import json
import os

DATA_FILE = "userdata.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(user_id):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "lang": "uz",
            "downloads": 0,
            "favorites": [],
            "daily_reminder": False,
        }
        save_data(data)
    return data[uid]

def update_user(user_id, updates):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "lang": "uz",
            "downloads": 0,
            "favorites": [],
            "daily_reminder": False,
        }
    data[uid].update(updates)
    save_data(data)

def increment_downloads(user_id):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "lang": "uz",
            "downloads": 0,
            "favorites": [],
            "daily_reminder": False,
        }
    data[uid]["downloads"] = data[uid].get("downloads", 0) + 1
    save_data(data)

def add_favorite(user_id, title, url):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "lang": "uz",
            "downloads": 0,
            "favorites": [],
            "daily_reminder": False,
        }
    data[uid]["favorites"].append({"title": title, "url": url})
    save_data(data)

def get_all_reminder_users():
    data = load_data()
    result = []
    for uid, info in data.items():
        if info.get("daily_reminder"):
            result.append(uid)
    return result

TRANSLATIONS = {
    "uz": {
        "choose_section": "Bolimni tanlang",
        "instagram": "Instagram",
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "music": "Musiqa",
        "stats": "Statistika",
        "favorites": "Sevimlilar",
        "settings": "Sozlamalar",
        "back": "Bosh menyu",
        "language": "Til",
        "downloads_count": "Yuklab olingan",
        "reminder_on": "Kunlik eslatma: Yoniq",
        "reminder_off": "Kunlik eslatma: Ochiq",
    },
    "ru": {
        "choose_section": "Vyberite razdel",
        "instagram": "Instagram",
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "music": "Muzyka",
        "stats": "Statistika",
        "favorites": "Izbrannoe",
        "settings": "Nastroyki",
        "back": "Glavnoe menyu",
        "language": "Yazyk",
        "downloads_count": "Skachano",
        "reminder_on": "Ejednevnoe napominanie: Vkl",
        "reminder_off": "Ejednevnoe napominanie: Vykl",
    },
    "en": {
        "choose_section": "Choose a section",
        "instagram": "Instagram",
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "music": "Music",
        "stats": "Statistics",
        "favorites": "Favorites",
        "settings": "Settings",
        "back": "Main menu",
        "language": "Language",
        "downloads_count": "Downloaded",
        "reminder_on": "Daily reminder: On",
        "reminder_off": "Daily reminder: Off",
    },
}

def t(key, lang="uz"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["uz"]).get(key, key)

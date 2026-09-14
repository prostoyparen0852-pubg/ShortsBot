import logging
import os
import random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from storage import get_user, update_user, increment_downloads, add_favorite, get_all_reminder_users, t

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8616128150:AAE2FyBjEgBCMlhOOBt9wENPwyxPtHVgJt4"

BOLD_MAP = {}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    BOLD_MAP[c] = chr(0x1D400 + i)
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
    BOLD_MAP[c] = chr(0x1D41A + i)

ITALIC_MAP = {}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    ITALIC_MAP[c] = chr(0x1D434 + i)
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
    ITALIC_MAP[c] = chr(0x1D44E + i)

DS_MAP = {}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    DS_MAP[c] = chr(0x1D538 + i)
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
    DS_MAP[c] = chr(0x1D552 + i)
DS_MAP.update({"C": "ℂ", "H": "ℍ", "N": "ℕ", "P": "ℙ", "Q": "ℚ", "R": "ℝ", "Z": "ℤ"})

FRAKTUR_MAP = {}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    FRAKTUR_MAP[c] = chr(0x1D504 + i)
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
    FRAKTUR_MAP[c] = chr(0x1D51E + i)
FRAKTUR_MAP.update({"C": "ℭ", "H": "ℌ", "I": "ℑ", "R": "ℜ", "Z": "ℨ"})

SCRIPT_MAP = {}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    SCRIPT_MAP[c] = chr(0x1D49C + i)
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
    SCRIPT_MAP[c] = chr(0x1D4B6 + i)
SCRIPT_MAP.update({"B": "ℬ", "E": "ℰ", "F": "ℱ", "H": "ℋ", "I": "ℐ", "L": "ℒ", "M": "ℳ", "R": "ℛ", "e": "ℯ", "g": "ℊ", "o": "ℴ"})

ALL_STYLES = [BOLD_MAP, ITALIC_MAP, DS_MAP, FRAKTUR_MAP, SCRIPT_MAP]

def stylize(text, sm):
    return "".join(sm.get(ch, ch) for ch in text)

def rs():
    return random.choice(ALL_STYLES)

INSTAGRAM_TOPICS = {
    "ig_moda": ("👗 Moda", "instagram fashion reels"),
    "ig_ovqat": ("🍔 Ovqat", "instagram food reels"),
    "ig_sayohat": ("✈️ Sayohat", "instagram travel reels"),
    "ig_gaming": ("🎮 Gaming", "instagram gaming reels"),
    "ig_sport": ("🏋️ Sport/Fitness", "instagram fitness reels"),
}

TIKTOK_TOPICS = {
    "tt_raqs": ("💃 Raqs", "tiktok dance"),
    "tt_kulgi": ("😂 Kulgi", "tiktok funny"),
    "tt_prank": ("🎭 Prank", "tiktok prank"),
    "tt_futbol": ("⚽ Futbol", "tiktok football"),
    "tt_hayvon": ("🐶 Hayvonlar", "tiktok animals"),
}

YOUTUBE_TOPICS = {
    "yt_sport": ("⚡ Sport", "youtube shorts sport"),
    "yt_kulgi": ("😂 Kulgi", "youtube shorts funny"),
    "yt_yangilik": ("📰 Yangiliklar", "youtube shorts news"),
    "yt_pubg": ("🔥 PUBG Mobile", "youtube shorts pubg mobile"),
}

MUSIC_LANGS = {
    "ml_uz": ("🇺🇿 O'zbek", "uzbek top hits 2026"),
    "ml_ru": ("🇷🇺 Rus", "russian top hits 2026"),
    "ml_tj": ("🇹🇯 Tojik", "tajik top hits 2026"),
    "ml_en": ("🇺🇸 Ingliz", "english top hits 2026"),
    "ml_tr": ("🇹🇷 Turk", "turkish top hits 2026"),
    "ml_hi": ("🇮🇳 Hind", "hindi top hits 2026"),
    "ml_ko": ("🇰🇷 Koreys", "korean top hits 2026"),
    "ml_es": ("🇪🇸 Ispan", "spanish top hits 2026"),
    "ml_ar": ("🇸🇦 Arab", "arabic top hits 2026"),
    "ml_fa": ("🇮🇷 Fors", "persian top hits 2026"),
}

LANGUAGES = {
    "lang_uz": ("🇺🇿 O'zbek", "uz"),
    "lang_ru": ("🇷🇺 Русский", "ru"),
    "lang_en": ("🇺🇸 English", "en"),
}

def main_menu_kb(sm, lang):
    kb = [
        [InlineKeyboardButton("📷 " + stylize(t("instagram", lang), sm) + " 📷", callback_data="main_instagram")],
        [InlineKeyboardButton("🎵 " + stylize(t("tiktok", lang), sm) + " 🎵", callback_data="main_tiktok")],
        [InlineKeyboardButton("▶️ " + stylize(t("youtube", lang), sm) + " ▶️", callback_data="main_youtube")],
        [InlineKeyboardButton("🎶 " + stylize(t("music", lang), sm) + " 🎶", callback_data="main_music")],
        [InlineKeyboardButton("📊 " + t("stats", lang), callback_data="main_stats"),
         InlineKeyboardButton("⭐ " + t("favorites", lang), callback_data="main_favorites")],
        [InlineKeyboardButton("⚙️ " + t("settings", lang), callback_data="main_settings")],
    ]
    return InlineKeyboardMarkup(kb)

def topics_kb(topics_dict, back_target="backmain"):
    kb = []
    for key, (label, _) in topics_dict.items():
        kb.append([InlineKeyboardButton(label, callback_data=key)])
    kb.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data=back_target)])
    return InlineKeyboardMarkup(kb)

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bosh menyu", callback_data="backmain")]])

async def show_main_menu(obj, user_id, edit=False):
    user = get_user(user_id)
    lang = user.get("lang", "uz")
    sm = rs()
    text = "🎬 " + stylize(t("choose_section", lang), sm) + ":"
    if edit:
        await obj.edit_message_text(text, reply_markup=main_menu_kb(sm, lang))
    else:
        await obj.reply_text(text, reply_markup=main_menu_kb(sm, lang))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = None
    user_id = update.effective_user.id
    get_user(user_id)
    await show_main_menu(update.message, user_id, edit=False)

async def download_and_send_video(query, url):
    output_path = f"downloads/{random.randint(100000,999999)}.mp4"
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {"outtmpl": output_path, "format": "best[ext=mp4]/best", "quiet": True, "extractor_args": {"youtube": {"player_client": ["android"]}}}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(output_path, "rb") as f:
            await query.message.reply_video(f)
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

async def search_and_show(query, search_term, count, prefix, context):
    sm = rs()
    await query.edit_message_text("🔎 " + stylize("Qidirilmoqda", sm) + "...")
    try:
        ydl_opts = {"quiet": True, "extract_flat": True, "extractor_args": {"youtube": {"player_client": ["android"]}}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{count}:{search_term}", download=False)
        entries = info.get("entries", [])
        results = []
        for e in entries:
            title = (e.get("title") or "Nomsiz")[:60]
            vid = e.get("id")
            url = f"https://www.youtube.com/watch?v={vid}"
            results.append((title, url))
        context.user_data[f"{prefix}_results"] = results
        context.user_data[f"{prefix}_index"] = 0
        if not results:
            await query.edit_message_text("Hech narsa topilmadi.", reply_markup=back_button())
            return
        await show_result_item(query, context, prefix, sm)
    except Exception as e:
        await query.edit_message_text("❌ Xatolik: " + str(e), reply_markup=back_button())

async def show_result_item(query, context, prefix, sm):
    results = context.user_data.get(f"{prefix}_results", [])
    idx = context.user_data.get(f"{prefix}_index", 0)
    if not results:
        await query.edit_message_text("Natija yoq.", reply_markup=back_button())
        return
    title, url = results[idx]
    kb = []
    nav = []
    if idx > 0:
        nav.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"{prefix}_prev"))
    nav.append(InlineKeyboardButton(f"{idx+1}/{len(results)}", callback_data="noop"))
    if idx < len(results) - 1:
        nav.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"{prefix}_next"))
    kb.append(nav)
    kb.append([InlineKeyboardButton("⬇️ Yuklab olish", callback_data=f"{prefix}_dl_{idx}"),
               InlineKeyboardButton("⭐ Saqlash", callback_data=f"{prefix}_fav_{idx}")])
    kb.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="backmain")])
    text = stylize(title, sm)
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user = get_user(user_id)
    lang = user.get("lang", "uz")
    sm = rs()

    if data == "noop":
        return

    if data == "backmain":
        context.user_data["mode"] = None
        await show_main_menu(query, user_id, edit=True)
        return

    if data == "main_instagram":
        text = "📷 " + stylize("Instagram bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(INSTAGRAM_TOPICS))
        return

    if data == "main_tiktok":
        text = "🎵 " + stylize("TikTok bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(TIKTOK_TOPICS))
        return

    if data == "main_youtube":
        text = "▶️ " + stylize("YouTube bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(YOUTUBE_TOPICS))
        return

    if data == "main_music":
        text = "🎶 " + stylize("Musiqa bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(MUSIC_LANGS))
        return

    if data == "main_stats":
        downloads = user.get("downloads", 0)
        favs = len(user.get("favorites", []))
        text = f"📊 Statistika\n\nYuklab olingan: {downloads}\nSevimlilar soni: {favs}"
        await query.edit_message_text(text, reply_markup=back_button())
        return

    if data == "main_favorites":
        favs = user.get("favorites", [])
        if not favs:
            await query.edit_message_text("⭐ Sevimlilar bosh.", reply_markup=back_button())
            return
        kb = []
        for i, f in enumerate(favs[-10:]):
            kb.append([InlineKeyboardButton(f["title"][:40], callback_data=f"favopen_{i}")])
        kb.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="backmain")])
        await query.edit_message_text("⭐ Sevimlilaringiz:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "main_settings":
        reminder = user.get("daily_reminder", False)
        reminder_text = "🔔 Kunlik eslatma: Yoniq" if reminder else "🔕 Kunlik eslatma: Ochiq"
        kb = [
            [InlineKeyboardButton("🌐 Til / Language", callback_data="settings_lang")],
            [InlineKeyboardButton(reminder_text, callback_data="toggle_reminder")],
            [InlineKeyboardButton("🔙 Bosh menyu", callback_data="backmain")],
        ]
        await query.edit_message_text("⚙️ Sozlamalar:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "settings_lang":
        kb = []
        for key, (label, code) in LANGUAGES.items():
            kb.append([InlineKeyboardButton(label, callback_data=key)])
        kb.append([InlineKeyboardButton("🔙", callback_data="main_settings")])
        await query.edit_message_text("🌐 Tilni tanlang:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data in LANGUAGES:
        _, code = LANGUAGES[data]
        update_user(user_id, {"lang": code})
        await query.edit_message_text("✅ Til ozgartirildi!", reply_markup=back_button())
        return

    if data == "toggle_reminder":
        new_val = not user.get("daily_reminder", False)
        update_user(user_id, {"daily_reminder": new_val})
        status = "yoqildi ✅" if new_val else "ochirildi ❌"
        await query.edit_message_text(f"🔔 Kunlik eslatma {status}", reply_markup=back_button())
        return

    if data in INSTAGRAM_TOPICS:
        _, term = INSTAGRAM_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in TIKTOK_TOPICS:
        _, term = TIKTOK_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in YOUTUBE_TOPICS:
        _, term = YOUTUBE_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in MUSIC_LANGS:
        _, term = MUSIC_LANGS[data]
        await search_and_show(query, term, 100, "mus", context)
        return

    if data in ("vid_next", "vid_prev", "mus_next", "mus_prev"):
        prefix = "vid" if data.startswith("vid") else "mus"
        direction = 1 if data.endswith("next") else -1
        context.user_data[f"{prefix}_index"] = context.user_data.get(f"{prefix}_index", 0) + direction
        await show_result_item(query, context, prefix, sm)
        return

    if data.startswith("vid_dl_"):
        idx = int(data.replace("vid_dl_", ""))
        results = context.user_data.get("vid_results", [])
        if idx >= len(results):
            return
        title, url = results[idx]
        await query.edit_message_text("⏳ Yuklanmoqda...")
        ok, err = await download_and_send_video(query, url)
        if ok:
            increment_downloads(user_id)
        else:
            await query.message.reply_text("❌ Xatolik: " + err)
        return

    if data.startswith("vid_fav_"):
        idx = int(data.replace("vid_fav_", ""))
        results = context.user_data.get("vid_results", [])
        if idx >= len(results):
            return
        title, url = results[idx]
        add_favorite(user_id, title, url)
        await query.answer("⭐ Saqlandi!", show_alert=True)
        return

    if data.startswith("mus_dl_"):
        idx = int(data.replace("mus_dl_", ""))
        results = context.user_data.get("mus_results", [])
        if idx >= len(results):
            return
        title, url = results[idx]
        await query.edit_message_text("⏳ Yuklanmoqda...")
        base_path = f"downloads/mus_{random.randint(100000,999999)}"
        os.makedirs("downloads", exist_ok=True)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": base_path + ".%(ext)s",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            "quiet": True, "extractor_args": {"youtube": {"player_client": ["android"]}},
        }
        final_path = base_path + ".mp3"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open(final_path, "rb") as f:
                await query.message.reply_audio(f, title=title)
            increment_downloads(user_id)
        except Exception as e:
            await query.message.reply_text("❌ Xatolik: " + str(e))
        finally:
            if os.path.exists(final_path):
                os.remove(final_path)
        return

    if data.startswith("mus_fav_"):
        idx = int(data.replace("mus_fav_", ""))
        results = context.user_data.get("mus_results", [])
        if idx >= len(results):
            return
        title, url = results[idx]
        add_favorite(user_id, title, url)
        await query.answer("⭐ Saqlandi!", show_alert=True)
        return

    if data.startswith("favopen_"):
        idx = int(data.replace("favopen_", ""))
        favs = user.get("favorites", [])
        if idx >= len(favs):
            return
        fav = favs[-10:][idx]
        kb = [
            [InlineKeyboardButton("⬇️ Yuklab olish", callback_data=f"favdl_{idx}")],
            [InlineKeyboardButton("🔙 Bosh menyu", callback_data="backmain")],
        ]
        await query.edit_message_text(fav["title"], reply_markup=InlineKeyboardMarkup(kb))
        return

    if data.startswith("favdl_"):
        idx = int(data.replace("favdl_", ""))
        favs = user.get("favorites", [])
        if idx >= len(favs):
            return
        fav = favs[-10:][idx]
        await query.edit_message_text("⏳ Yuklanmoqda...")
        ok, err = await download_and_send_video(query, fav["url"])
        if not ok:
            await query.message.reply_text("❌ Xatolik: " + err)
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iltimos, /start bosing va menyudan tanlang.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()

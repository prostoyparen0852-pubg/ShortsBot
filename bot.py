import logging
import os
import random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

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

def main_menu_kb(sm):
    kb = [
        [InlineKeyboardButton("📷 " + stylize("Instagram", sm) + " 📷", callback_data="main_instagram")],
        [InlineKeyboardButton("🎵 " + stylize("TikTok", sm) + " 🎵", callback_data="main_tiktok")],
        [InlineKeyboardButton("▶️ " + stylize("YouTube", sm) + " ▶️", callback_data="main_youtube")],
        [InlineKeyboardButton("🎶 " + stylize("Musiqa", sm) + " 🎶", callback_data="main_music")],
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

async def show_main_menu(obj, edit=False):
    sm = rs()
    text = "🎬 " + stylize("Bolimni tanlang", sm) + ":"
    if edit:
        await obj.edit_message_text(text, reply_markup=main_menu_kb(sm))
    else:
        await obj.reply_text(text, reply_markup=main_menu_kb(sm))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = None
    await show_main_menu(update.message, edit=False)

async def download_and_send_video(query_or_msg, url, is_query=False):
    output_path = f"downloads/{random.randint(100000,999999)}.mp4"
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {"outtmpl": output_path, "format": "best[ext=mp4]/best", "quiet": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(output_path, "rb") as f:
            if is_query:
                await query_or_msg.message.reply_video(f)
            else:
                await query_or_msg.reply_video(f)
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
        ydl_opts = {"quiet": True, "extract_flat": True}
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
    kb.append([InlineKeyboardButton("⬇️ Yuklab olish", callback_data=f"{prefix}_dl_{idx}")])
    kb.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="backmain")])
    text = stylize(title, sm)
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    sm = rs()

    if data == "noop":
        return

    if data == "backmain":
        context.user_data["mode"] = None
        await show_main_menu(query, edit=True)
        return

    if data == "main_instagram":
        context.user_data["mode"] = "instagram_topics"
        text = "📷 " + stylize("Instagram bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(INSTAGRAM_TOPICS))
        return

    if data == "main_tiktok":
        context.user_data["mode"] = "tiktok_topics"
        text = "🎵 " + stylize("TikTok bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(TIKTOK_TOPICS))
        return

    if data == "main_youtube":
        context.user_data["mode"] = "youtube_topics"
        text = "▶️ " + stylize("YouTube bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(YOUTUBE_TOPICS))
        return

    if data == "main_music":
        context.user_data["mode"] = "music_langs"
        text = "🎶 " + stylize("Musiqa bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(MUSIC_LANGS))
        return

    if data in INSTAGRAM_TOPICS:
        label, term = INSTAGRAM_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in TIKTOK_TOPICS:
        label, term = TIKTOK_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in YOUTUBE_TOPICS:
        label, term = YOUTUBE_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in MUSIC_LANGS:
        label, term = MUSIC_LANGS[data]
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
        await query.edit_message_text("⏳ " + stylize("Yuklanmoqda", sm) + "...")
        ok, err = await download_and_send_video(query, url, is_query=True)
        if not ok:
            await query.message.reply_text("❌ Xatolik: " + err)
        return

    if data.startswith("mus_dl_"):
        idx = int(data.replace("mus_dl_", ""))
        results = context.user_data.get("mus_results", [])
        if idx >= len(results):
            return
        title, url = results[idx]
        await query.edit_message_text("⏳ " + stylize("Yuklanmoqda", sm) + "...")
        base_path = f"downloads/mus_{random.randint(100000,999999)}"
        os.makedirs("downloads", exist_ok=True)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": base_path + ".%(ext)s",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            "quiet": True,
        }
        final_path = base_path + ".mp3"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open(final_path, "rb") as f:
                await query.message.reply_audio(f, title=title)
        except Exception as e:
            await query.message.reply_text("❌ Xatolik: " + str(e))
        finally:
            if os.path.exists(final_path):
                os.remove(final_path)
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

async def download_and_send_video(query_or_msg, url, is_query=False):
    output_path = f"downloads/{random.randint(100000,999999)}.mp4"
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {"outtmpl": output_path, "format": "best[ext=mp4]/best", "quiet": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(output_path, "rb") as f:
            if is_query:
                await query_or_msg.message.reply_video(f)
            else:
                await query_or_msg.reply_video(f)
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
        ydl_opts = {"quiet": True, "extract_flat": True}
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
    kb.append([InlineKeyboardButton("⬇️ Yuklab olish", callback_data=f"{prefix}_dl_{idx}")])
    kb.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="backmain")])
    text = stylize(title, sm)
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    sm = rs()

    if data == "noop":
        return

    if data == "backmain":
        context.user_data["mode"] = None
        await show_main_menu(query, edit=True)
        return

    if data == "main_instagram":
        context.user_data["mode"] = "instagram_topics"
        text = "📷 " + stylize("Instagram bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(INSTAGRAM_TOPICS))
        return

    if data == "main_tiktok":
        context.user_data["mode"] = "tiktok_topics"
        text = "🎵 " + stylize("TikTok bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(TIKTOK_TOPICS))
        return

    if data == "main_youtube":
        context.user_data["mode"] = "youtube_topics"
        text = "▶️ " + stylize("YouTube bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(YOUTUBE_TOPICS))
        return

    if data == "main_music":
        context.user_data["mode"] = "music_langs"
        text = "🎶 " + stylize("Musiqa bolimi", sm)
        await query.edit_message_text(text, reply_markup=topics_kb(MUSIC_LANGS))
        return

    if data in INSTAGRAM_TOPICS:
        label, term = INSTAGRAM_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in TIKTOK_TOPICS:
        label, term = TIKTOK_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in YOUTUBE_TOPICS:
        label, term = YOUTUBE_TOPICS[data]
        await search_and_show(query, term, 15, "vid", context)
        return

    if data in MUSIC_LANGS:
        label, term = MUSIC_LANGS[data]
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
        await query.edit_message_text("⏳ " + stylize("Yuklanmoqda", sm) + "...")
        ok, err = await download_and_send_video(query, url, is_query=True)
        if not ok:
            await query.message.reply_text("❌ Xatolik: " + err)
        return

    if data.startswith("mus_dl_"):
        idx = int(data.replace("mus_dl_", ""))
        results = context.user_data.get("mus_results", [])
        if idx >= len(results):
            return
        title, url = results[idx]
        await query.edit_message_text("⏳ " + stylize("Yuklanmoqda", sm) + "...")
        base_path = f"downloads/mus_{random.randint(100000,999999)}"
        os.makedirs("downloads", exist_ok=True)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": base_path + ".%(ext)s",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            "quiet": True,
        }
        final_path = base_path + ".mp3"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open(final_path, "rb") as f:
                await query.message.reply_audio(f, title=title)
        except Exception as e:
            await query.message.reply_text("❌ Xatolik: " + str(e))
        finally:
            if os.path.exists(final_path):
                os.remove(final_path)
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

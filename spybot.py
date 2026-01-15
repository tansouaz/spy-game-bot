import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

# ================= WORD PAIRS =================
FAKE_PAIRS = {
    "fa": [
        ("فرودگاه", "ایستگاه"), ("بیمارستان", "درمانگاه"), ("مدرسه", "دانشگاه"),
        ("بازار", "مغازه"), ("ساحل", "دریا"), ("جنگل", "پارک"),
        ("استخر", "باشگاه"), ("سینما", "تئاتر"), ("کتابخانه", "کتابفروشی"),
        ("هتل", "مهمانسرا"), ("بانک", "صرافی"), ("پل", "تونل"),
        ("خیابان", "کوچه"), ("دفتر", "اداره"),
    ],
    "en": [
        ("Airport", "Station"), ("Hospital", "Clinic"), ("School", "University"),
        ("Market", "Shop"), ("Beach", "Sea"), ("Forest", "Park"),
        ("Pool", "Gym"), ("Cinema", "Theater"), ("Library", "Bookstore"),
        ("Hotel", "Hostel"), ("Bank", "Exchange"), ("Bridge", "Tunnel"),
        ("Street", "Alley"), ("Office", "Department"),
    ],
    "tr": [
        ("Havalimanı", "İstasyon"), ("Hastane", "Klinik"), ("Okul", "Üniversite"),
        ("Pazar", "Mağaza"), ("Plaj", "Deniz"), ("Orman", "Park"),
        ("Havuz", "Spor Salonu"), ("Sinema", "Tiyatro"),
        ("Kütüphane", "Kitapçı"), ("Otel", "Pansiyon"),
    ],
    "ru": [
        ("Аэропорт", "Станция"), ("Больница", "Клиника"),
        ("Школа", "Университет"), ("Рынок", "Магазин"),
        ("Пляж", "Море"), ("Лес", "Парк"),
        ("Кино", "Театр"), ("Библиотека", "Книжный"),
    ],
}

TEXT = {
    "fa": {
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟ (حداقل 3)",
        "player": "📱 بازیکن",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "end": "🏁 پایان بازی",
        "result": "📌 نتیجه بازی",
        "real": "🔑 کلمه اصلی:",
        "fake": "🎭 کلمه متفاوت:",
        "new": "🔁 شروع بازی جدید",
    },
    "en": {
        "players": "👥 Number of players? (min 3)",
        "player": "📱 Player",
        "show": "👁 Show word",
        "seen": "👁 Seen",
        "end": "🏁 End game",
        "result": "📌 Game result",
        "real": "🔑 Real word:",
        "fake": "🎭 Fake word:",
        "new": "🔁 New game",
    },
    "tr": {
        "players": "👥 Kaç oyuncu var? (min 3)",
        "player": "📱 Oyuncu",
        "show": "👁 Kelimeyi gör",
        "seen": "👁 Gördüm",
        "end": "🏁 Oyunu bitir",
        "result": "📌 Oyun sonucu",
        "real": "🔑 Asıl kelime:",
        "fake": "🎭 Farklı kelime:",
        "new": "🔁 Yeni oyun",
    },
    "ru": {
        "players": "👥 Сколько игроков? (мин 3)",
        "player": "📱 Игрок",
        "show": "👁 Показать слово",
        "seen": "👁 Видел",
        "end": "🏁 Конец игры",
        "result": "📌 Результат игры",
        "real": "🔑 Основное слово:",
        "fake": "🎭 Другое слово:",
        "new": "🔁 Новая игра",
    },
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    games[uid] = {"state": "lang"}

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    await update.effective_message.reply_text(
        "🌍 Choose language",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    lang = q.data.split("_")[1]

    games[uid] = {
        "lang": lang,
        "state": "players",
    }

    await q.message.reply_text(TEXT[lang]["players"])

# ================= PLAYER COUNT =================
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    game = games.get(uid)

    if not game or game["state"] != "players":
        return

    try:
        n = int(update.message.text)
    except:
        return

    if n < 3:
        await update.message.reply_text(TEXT[game["lang"]]["players"])
        return

    real, fake = random.choice(FAKE_PAIRS[game["lang"]])

    fake_count = random.randint(1, n // 2)

    words = [real] * (n - fake_count) + [fake] * fake_count
    random.shuffle(words)

    game.update({
        "state": "play",
        "words": words,
        "real": real,
        "fake": fake,
        "index": 0,
    })

    await show_player(update, uid)

# ================= SHOW PLAYER =================
async def show_player(update, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["index"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show")]]
    await update.effective_message.reply_text(
        f"{TEXT[lang]['player']} {i+1}",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    word = game["words"][game["index"]]

    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    await q.message.reply_text(
        f"🔑 {word}",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    game["index"] += 1

    if game["index"] >= len(game["words"]):
        kb = [[InlineKeyboardButton(TEXT[game["lang"]]["end"], callback_data="end")]]
        await q.message.reply_text("🏁 All players checked", reply_markup=InlineKeyboardMarkup(kb))
        return

    await show_player(q.message, uid)

# ================= END =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games.pop(uid)

    lang = game["lang"]
    text = (
        f"{TEXT[lang]['result']}\n\n"
        f"{TEXT[lang]['real']} {game['real']}\n"
        f"{TEXT[lang]['fake']} {game['fake']}"
    )

    kb = [[InlineKeyboardButton(TEXT[lang]["new"], callback_data="restart")]]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

# ================= RESTART =================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await start(q, context)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))
    app.add_handler(CallbackQueryHandler(show_word, pattern="show"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(end_game, pattern="end"))
    app.add_handler(CallbackQueryHandler(restart, pattern="restart"))

    app.run_polling()

if __name__ == "__main__":
    main()

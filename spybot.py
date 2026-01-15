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

# ================= DATA =================
games = {}

FAKE_PAIRS = {
    "fa": [("سینما","تئاتر"),("بیمارستان","درمانگاه"),("کتابخانه","کتابفروشی"),("بازار","مغازه")],
    "en": [("Cinema","Theater"),("Hospital","Clinic"),("Library","Bookstore"),("Market","Shop")],
    "tr": [("Sinema","Tiyatro"),("Hastane","Klinik"),("Kütüphane","Kitapçı"),("Pazar","Mağaza")],
    "ru": [("Кино","Театр"),("Больница","Клиника"),("Библиотека","Книжный"),("Рынок","Магазин")],
}

TEXT = {
    "fa": {
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟ (حداقل 3)",
        "player": "📱 بازیکن",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "checked": "🏁 همه دیدند",
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
        "checked": "🏁 All players checked",
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
        "checked": "🏁 Herkes baktı",
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
        "checked": "🏁 Все посмотрели",
        "end": "🏁 Завершить игру",
        "result": "📌 Результат игры",
        "real": "🔑 Основное слово:",
        "fake": "🎭 Другое слово:",
        "new": "🔁 Новая игра",
    },
}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    games[chat_id] = {"state": "lang"}

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    await update.message.reply_text("🌍 Choose language", reply_markup=InlineKeyboardMarkup(kb))

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    lang = q.data.split("_")[1]

    games[chat_id] = {
        "lang": lang,
        "state": "players",
    }
    await q.message.reply_text(TEXT[lang]["players"])

# ================= PLAYER COUNT =================
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    game = games.get(chat_id)
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
    words = [real]*(n-fake_count) + [fake]*fake_count
    random.shuffle(words)

    game.update({
        "state": "play",
        "words": words,
        "real": real,
        "fake": fake,
        "i": 0
    })

    await show_player(update.message, chat_id)

# ================= SHOW PLAYER =================
async def show_player(message, chat_id):
    game = games[chat_id]
    lang = game["lang"]
    i = game["i"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show")]]
    await message.reply_text(
        f"{TEXT[lang]['player']} {i+1}",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games[chat_id]
    lang = game["lang"]

    word = game["words"][game["i"]]
    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    await q.message.reply_text(f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games[chat_id]
    lang = game["lang"]

    game["i"] += 1
    if game["i"] >= len(game["words"]):
        kb = [[InlineKeyboardButton(TEXT[lang]["end"], callback_data="end")]]
        await q.message.reply_text(TEXT[lang]["checked"], reply_markup=InlineKeyboardMarkup(kb))
    else:
        await show_player(q.message, chat_id)

# ================= END =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games[chat_id]
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

    chat_id = q.message.chat_id

    # پاک‌سازی کامل بازی قبلی
    games[chat_id] = {"state": "lang"}

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]

    await q.message.reply_text(
        "🌍 Choose language",
        reply_markup=InlineKeyboardMarkup(kb)
    )


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

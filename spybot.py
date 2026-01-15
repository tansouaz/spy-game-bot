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
        ("بازار", "مغازه"), ("سینما", "تئاتر"), ("کتابخانه", "کتابفروشی"),
        ("بیمارستان", "درمانگاه"), ("فرودگاه", "ایستگاه"),
    ],
    "en": [
        ("Market", "Shop"), ("Cinema", "Theater"),
        ("Library", "Bookstore"), ("Hospital", "Clinic"),
        ("Airport", "Station"),
    ],
    "tr": [
        ("Pazar", "Mağaza"), ("Sinema", "Tiyatro"),
        ("Kütüphane", "Kitapçı"), ("Hastane", "Klinik"),
        ("Havalimanı", "İstasyon"),
    ],
    "ru": [
        ("Рынок", "Магазин"), ("Кино", "Театр"),
        ("Библиотека", "Книжный"), ("Больница", "Клиника"),
        ("Аэропорт", "Станция"),
    ],
}

TEXT = {
    "fa": {
        "choose": "🌍 انتخاب زبان",
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟ (حداقل 3)",
        "player": "📱 بازیکن",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "end_players": "🏁 همه بازیکن‌ها دیدند",
        "result": "📌 نتیجه بازی",
        "real": "🔑 کلمه اصلی:",
        "fake": "🎭 کلمه متفاوت:",
        "new": "🔁 شروع بازی جدید",
    },
    "en": {
        "choose": "🌍 Choose language",
        "players": "👥 Number of players? (min 3)",
        "player": "📱 Player",
        "show": "👁 Show word",
        "seen": "👁 Seen",
        "end_players": "🏁 All players checked",
        "result": "📌 Game result",
        "real": "🔑 Real word:",
        "fake": "🎭 Fake word:",
        "new": "🔁 New game",
    },
    "tr": {
        "choose": "🌍 Dil seç",
        "players": "👥 Kaç oyuncu var? (min 3)",
        "player": "📱 Oyuncu",
        "show": "👁 Kelimeyi gör",
        "seen": "👁 Gördüm",
        "end_players": "🏁 Herkes baktı",
        "result": "📌 Oyun sonucu",
        "real": "🔑 Asıl kelime:",
        "fake": "🎭 Farklı kelime:",
        "new": "🔁 Yeni oyun",
    },
    "ru": {
        "choose": "🌍 Выберите язык",
        "players": "👥 Сколько игроков? (мин 3)",
        "player": "📱 Игрок",
        "show": "👁 Показать слово",
        "seen": "👁 Видел",
        "end_players": "🏁 Все посмотрели",
        "result": "📌 Результат игры",
        "real": "🔑 Основное слово:",
        "fake": "🎭 Другое слово:",
        "new": "🔁 Новая игра",
    },
}

games = {}

# ================= UTILS =================
async def clear_messages(context, chat_id, game):
    for mid in game["msgs"]:
        try:
            await context.bot.delete_message(chat_id, mid)
        except:
            pass
    game["msgs"].clear()

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    games[uid] = {"state": "lang", "msgs": []}

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]

    msg = await update.effective_message.reply_text(
        "🌍 Choose language",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    games[uid]["msgs"].append(msg.message_id)

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    lang = q.data.split("_")[1]

    games[uid] = {
        "lang": lang,
        "state": "players",
        "msgs": [],
    }

    await q.message.delete()
    msg = await q.message.reply_text(TEXT[lang]["players"])
    games[uid]["msgs"].append(msg.message_id)

# ================= PLAYER COUNT =================
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    game = games.get(uid)

    if not game or game["state"] != "players":
        return

    try:
        n = int(update.message.text)
    except:
        return

    if n < 3:
        return

    real, fake = random.choice(FAKE_PAIRS[game["lang"]])
    fake_count = random.randint(1, n // 2)

    words = [real] * (n - fake_count) + [fake] * fake_count
    random.shuffle(words)

    game.update({
        "words": words,
        "real": real,
        "fake": fake,
        "i": 0,
        "state": "play",
        "msgs": [],
    })

    await show_player(update.message, uid, context)

# ================= SHOW PLAYER =================
async def show_player(message, uid, context):
    game = games[uid]
    lang = game["lang"]

    msg = await message.reply_text(
        f"{TEXT[lang]['player']} {game['i'] + 1}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXT[lang]["show"], callback_data="show")]
        ])
    )
    game["msgs"].append(msg.message_id)

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    msg = await q.message.reply_text(
        f"🔑 {game['words'][game['i']]}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]
        ])
    )
    game["msgs"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    chat_id = q.message.chat_id
    lang = game["lang"]

    await clear_messages(context, chat_id, game)

    game["i"] += 1

    if game["i"] >= len(game["words"]):
        msg = await q.message.reply_text(
            TEXT[lang]["end_players"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏁 End game", callback_data="end")]
            ])
        )
        game["msgs"].append(msg.message_id)
        return

    await show_player(q.message, uid, context)

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    text = (
        f"{TEXT[lang]['result']}\n\n"
        f"{TEXT[lang]['real']} {game['real']}\n"
        f"{TEXT[lang]['fake']} {game['fake']}"
    )

    games.pop(uid, None)

    await q.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXT[lang]["new"], callback_data="restart")]
        ])
    )

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

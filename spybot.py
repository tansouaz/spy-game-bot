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

# ---------------- DATA ----------------
WORDS = {
    "fa": ["فرودگاه", "بیمارستان", "مدرسه", "رستوران", "پارک", "بازار"],
    "en": ["Airport", "Hospital", "School", "Restaurant", "Park", "Market"],
    "tr": ["Havalimanı", "Hastane", "Okul", "Restoran", "Park", "Pazar"],
    "ru": ["Аэропорт", "Больница", "Школа", "Ресторан", "Парк", "Рынок"],
}

TEXT = {
    "fa": {
        "choose_lang": "🌍 زبان را انتخاب کنید",
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟",
        "ready": "📱 همه آماده‌اید؟ گوشی دست نفر اول",
        "start": "🎮 شروع بازی",
        "show": "👁 دیدن نقش",
        "seen": "👁 دیدم",
        "next": "➡️ نفر بعد",
        "spy": "😈 تو جاسوسی\n❌ کلمه‌ای نداری",
        "word": "🔑 کلمه: ",
        "end": "✅ همه نقش‌ها دیده شد\n🕵️ بازی شروع شد!",
        "summary": "🏁 پایان بازی",
        "restart": "🔁 شروع بازی جدید",
        "end_btn": "🏁 پایان بازی",
        "player": "📱 بازیکن",
    },
    "en": {
        "choose_lang": "🌍 Choose language",
        "players": "👥 How many players?",
        "ready": "📱 Everyone ready? Phone to Player 1",
        "start": "🎮 Start Game",
        "show": "👁 Show role",
        "seen": "👁 Seen",
        "next": "➡️ Next player",
        "spy": "😈 You are the SPY\n❌ No word",
        "word": "🔑 Word: ",
        "end": "✅ All roles seen\n🕵️ Game started!",
        "summary": "🏁 Game Over",
        "restart": "🔁 New Game",
        "end_btn": "🏁 End Game",
        "player": "📱 Player",
    },
    "tr": {
        "choose_lang": "🌍 Dil seçin",
        "players": "👥 Kaç oyuncu var?",
        "ready": "📱 Herkes hazır mı? Telefon 1. oyuncuda",
        "start": "🎮 Oyunu Başlat",
        "show": "👁 Rolü Gör",
        "seen": "👁 Gördüm",
        "next": "➡️ Sıradaki",
        "spy": "😈 Sen CASUSSUN\n❌ Kelimen yok",
        "word": "🔑 Kelime: ",
        "end": "✅ Herkes rolünü gördü\n🕵️ Oyun başladı!",
        "summary": "🏁 Oyun Bitti",
        "restart": "🔁 Yeni Oyun",
        "end_btn": "🏁 Oyunu Bitir",
        "player": "📱 Oyuncu",
    },
    "ru": {
        "choose_lang": "🌍 Выберите язык",
        "players": "👥 Сколько игроков?",
        "ready": "📱 Все готовы? Телефон у игрока 1",
        "start": "🎮 Начать игру",
        "show": "👁 Показать роль",
        "seen": "👁 Видел",
        "next": "➡️ Следующий",
        "spy": "😈 Ты ШПИОН\n❌ У тебя нет слова",
        "word": "🔑 Слово: ",
        "end": "✅ Все роли просмотрены\n🕵️ Игра началась!",
        "summary": "🏁 Игра окончена",
        "restart": "🔁 Новая игра",
        "end_btn": "🏁 Завершить игру",
        "player": "📱 Игрок",
    },
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    intro_text = (
        "🕵️ **Spy Game**\n"
        "One phone. One secret word.\n"
        "Some players know it… **one (or more) is the spy 😈**\n"
        "Pass the phone, see your role, and don’t get caught.\n\n"
        "Choose your language to start 👇"
    )

    kb = [
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ],
    ]

    await update.message.reply_text(
        intro_text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = q.data.split("_")[1]
    uid = q.from_user.id

    # اگر زبان اشتباه بود
    if lang not in TEXT:
        return

    games[uid] = {
        "lang": lang,
        "state": "players",
        "control_messages": [],
    }

    await q.message.reply_text(TEXT[lang]["players"])

# ================= PLAYER COUNT =================
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    game = games.get(uid)

    if not game or game["state"] != "players":
        return

    try:
        players = int(update.message.text)
        if players < 3:
            return
    except:
        return

    game["players"] = players
    game["state"] = "ready"

    kb = [[InlineKeyboardButton(TEXT[game["lang"]]["start"], callback_data="start_game")]]

    msg = await update.message.reply_text(
        TEXT[game["lang"]]["ready"],
        reply_markup=InlineKeyboardMarkup(kb),
    )
    game["control_messages"].append(msg.message_id)

# ================= START GAME =================
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]

    if game["state"] != "ready":
        return

    # پاک کردن دکمه Start Game
    try:
        await q.message.delete()
    except:
        pass

    lang = game["lang"]
    players = game["players"]

    if players <= 4:
        spy_count = 1
    else:
        spy_count = random.randint(1, players // 2)

    roles = ["spy"] * spy_count + ["player"] * (players - spy_count)
    random.shuffle(roles)

    game.update({
        "roles": roles,
        "spy_count": spy_count,
        "word": random.choice(WORDS[lang]),
        "current": 0,
        "temp_messages": [],
        "state": "playing",
    })

    await show_player(q.message, uid)

# ================= SHOW PLAYER =================
async def show_player(message, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show_role")]]
    msg = await message.reply_text(
        f"{TEXT[lang]['player']} {i + 1}",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    game["temp_messages"].append(msg.message_id)

# ================= SHOW ROLE =================
async def show_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    text = TEXT[lang]["spy"] if game["roles"][i] == "spy" else TEXT[lang]["word"] + game["word"]

    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    msg = await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    game["temp_messages"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    for mid in game["temp_messages"]:
        try:
            await context.bot.delete_message(q.message.chat_id, mid)
        except:
            pass

    game["temp_messages"] = []
    game["current"] += 1

    if game["current"] >= game["players"]:
        msg = await q.message.reply_text(TEXT[lang]["end"])
        game["control_messages"].append(msg.message_id)

        kb = [[InlineKeyboardButton(TEXT[lang]["end_btn"], callback_data="end_game")]]
        btn = await q.message.reply_text(
            TEXT[lang]["end_btn"],
            reply_markup=InlineKeyboardMarkup(kb),
        )
        game["control_messages"].append(btn.message_id)
        return

    await show_player(q.message, uid)

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    # خلاصه نهایی (برای همه زبان‌ها)
    summary = (
        f"{TEXT[lang]['summary']}\n\n"
        f"👥 Players: {game['players']}\n"
        f"🕵️ Spies: {game['spy_count']}\n"
        f"🔑 Word: {game['word']}"
    )

    kb = [[InlineKeyboardButton(TEXT[lang]["restart"], callback_data="restart")]]

    msg = await q.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(kb))
    game["control_messages"].append(msg.message_id)

# ================= RESTART =================
async def restart_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    # پاک کردن پیام‌های کنترلی
    for mid in game["control_messages"]:
        try:
            await context.bot.delete_message(q.message.chat_id, mid)
        except:
            pass

    games[uid] = {
        "lang": lang,
        "state": "players",
        "control_messages": [],
    }

    await q.message.reply_text(TEXT[lang]["players"])

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
    app.add_handler(CallbackQueryHandler(start_game, pattern="start_game"))
    app.add_handler(CallbackQueryHandler(show_role, pattern="show_role"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(end_game, pattern="end_game"))
    app.add_handler(CallbackQueryHandler(restart_game, pattern="restart"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))

    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()

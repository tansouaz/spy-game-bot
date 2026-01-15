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

# ================= FAKE WORD PAIRS =================
FAKE_PAIRS = {
    "fa": [
        ("گیلاس", "آلبالو"),
        ("سیب", "گلابی"),
        ("پرتقال", "نارنگی"),
        ("دریا", "اقیانوس"),
        ("مدرسه", "دانشگاه"),
        ("کلاس", "آمفی‌تئاتر"),
        ("بیمارستان", "کلینیک"),
        ("فرودگاه", "ایستگاه"),
        ("رستوران", "کافه"),
        ("ساحل", "دریا"),
    ]
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    games[uid] = {"state": "players"}

    await update.message.reply_text(
        "👥 تعداد بازیکن‌ها چند نفر است؟\n(حداقل 3 نفر)"
    )

# ================= SET PLAYERS =================
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    game = games.get(uid)

    if not game or game["state"] != "players":
        return

    try:
        players = int(update.message.text)
    except:
        return

    if players < 3:
        return

    roles = ["spy"] + ["player"] * (players - 1)
    random.shuffle(roles)

    real_word, fake_word = random.choice(FAKE_PAIRS["fa"])

    games[uid] = {
        "state": "playing",
        "players": players,
        "roles": roles,
        "real_word": real_word,
        "fake_word": fake_word,
        "current": 0,
        "ui_message_id": None,
    }

    kb = [[InlineKeyboardButton("🎮 شروع بازی", callback_data="start_game")]]
    await update.message.reply_text(
        "📱 همه آماده‌اید؟ گوشی دست نفر اول",
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ================= START GAME =================
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    games[uid]["ui_message_id"] = q.message.message_id

    await show_player(context, q.message.chat_id, uid)

# ================= SHOW PLAYER =================
async def show_player(context, chat_id, uid):
    game = games[uid]
    i = game["current"]

    kb = [[InlineKeyboardButton("👁 دیدن کلمه", callback_data="show_word")]]

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=game["ui_message_id"],
        text=f"📱 بازیکن {i + 1}\nگوشی دست این نفر",
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]

    word = (
        game["fake_word"]
        if game["roles"][game["current"]] == "spy"
        else game["real_word"]
    )

    kb = [[InlineKeyboardButton("👁 دیدم", callback_data="seen")]]

    await q.message.edit_text(
        f"🔑 کلمه:\n\n{word}",
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]

    game["current"] += 1

    # 👇 اگر آخرین نفر بود
    if game["current"] >= game["players"]:
        kb = [[InlineKeyboardButton("🏁 نمایش نتیجه", callback_data="show_result")]]

        # ❗ پیام جدید فقط اینجا
        await context.bot.send_message(
            chat_id=q.message.chat_id,
            text="📱 همه بازیکن‌ها کلمه رو دیدن\n👇 وقتی آماده‌اید نتیجه رو ببینید",
            reply_markup=InlineKeyboardMarkup(kb),
        )
        return

    await show_player(context, q.message.chat_id, uid)


# ================= SHOW RESULT =================
async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]

    kb = [[InlineKeyboardButton("🔁 شروع بازی جدید", callback_data="restart")]]

    await q.message.edit_text(
        f"🏁 پایان بازی\n\n"
        f"🔑 کلمه اصلی: {game['real_word']}\n"
        f"🎭 کلمه متفاوت: {game['fake_word']}",
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ================= RESTART =================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    games[uid] = {"state": "players"}

    await q.message.edit_text(
        "👥 تعداد بازیکن‌ها چند نفر است؟\n(حداقل 3 نفر)"
    )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_game, pattern="^start_game$"))
    app.add_handler(CallbackQueryHandler(show_word, pattern="^show_word$"))
    app.add_handler(CallbackQueryHandler(seen, pattern="^seen$"))
    app.add_handler(CallbackQueryHandler(show_result, pattern="^show_result$"))
    app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))

    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()

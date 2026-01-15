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

# ================= FAKE PAIRS =================
FAKE_PAIRS = {
    "fa": [
        ("گیلاس", "آلبالو"), ("رستوران", "کافه"), ("مدرسه", "دانشگاه"),
        ("فرودگاه", "ایستگاه"), ("ساحل", "دریا"), ("پلیس", "سرباز"),
        ("بیمارستان", "کلینیک"), ("قطار", "مترو"), ("بازار", "مغازه"),
        ("کلاس", "آمفی‌تئاتر"),
    ],
    "en": [
        ("Cherry", "Sour Cherry"), ("Restaurant", "Cafe"),
        ("School", "University"), ("Airport", "Station"),
        ("Beach", "Sea"), ("Police", "Soldier"),
    ],
    "tr": [
        ("Kiraz", "Vişne"), ("Restoran", "Kafe"),
        ("Okul", "Üniversite"), ("Havalimanı", "İstasyon"),
    ],
    "ru": [
        ("Вишня", "Черешня"), ("Ресторан", "Кафе"),
    ],
}

TEXT = {
    "fa": {
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟ (حداقل ۳)",
        "start": "🎮 شروع بازی",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "player": "📱 بازیکن",
        "end_btn": "🏁 پایان بازی",
        "summary": "🏁 پایان بازی\n\n🔑 کلمه اصلی: {real}\n🎭 کلمه متفاوت: {fake}",
    }
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    # اگر قبلاً پیام start داشتیم، پاکش کن
    if uid in START_MESSAGE_ID:
        try:
            await context.bot.delete_message(chat_id, START_MESSAGE_ID[uid])
        except:
            pass

    games.pop(uid, None)  # ریست کامل بازی

    intro_text = (
        "🕵️ Spy Game\n"
        "One phone. One secret word.\n"
        "Some players know it… one is the spy 😈\n\n"
        "Choose language 👇"
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

    msg = await update.message.reply_text(
        intro_text,
        reply_markup=InlineKeyboardMarkup(kb),
    )

    START_MESSAGE_ID[uid] = msg.message_id


# ================= START GAME =================
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.delete()
    await show_player(q.message, q.from_user.id)

# ================= SHOW PLAYER =================
async def show_player(message, uid):
    game = games[uid]
    i = game["current"]
    kb = [[InlineKeyboardButton(TEXT["fa"]["show"], callback_data="show")]]
    msg = await message.reply_text(f"{TEXT['fa']['player']} {i+1}", reply_markup=InlineKeyboardMarkup(kb))
    game["temp"].append(msg.message_id)

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    i = game["current"]
    word = game["fake"] if game["roles"][i] == "spy" else game["real"]

    kb = [[InlineKeyboardButton(TEXT["fa"]["seen"], callback_data="seen")]]
    msg = await q.message.reply_text(f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))
    game["temp"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    for mid in game["temp"]:
        try:
            await context.bot.delete_message(q.message.chat_id, mid)
        except:
            pass
    game["temp"].clear()

    game["current"] += 1

    if game["current"] >= game["players"]:
        kb = [[InlineKeyboardButton(TEXT["fa"]["end_btn"], callback_data="end_game")]]
        await q.message.reply_text("همه بازیکن‌ها کلمه رو دیدن ✅", reply_markup=InlineKeyboardMarkup(kb))
        return

    await show_player(q.message, uid)

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games.pop(uid)

    text = TEXT["fa"]["summary"].format(real=game["real"], fake=game["fake"])
    await q.message.reply_text(text)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))
    app.add_handler(CallbackQueryHandler(start_game, pattern="start_game"))
    app.add_handler(CallbackQueryHandler(show_word, pattern="show"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(end_game, pattern="end_game"))
    app.run_polling()

if __name__ == "__main__":
    main()

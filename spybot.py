import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TOKEN")

# ================= FAKE PAIRS =================
FAKE_PAIRS = {
    "fa": [
        ("فرودگاه", "ایستگاه"),
        ("بیمارستان", "درمانگاه"),
        ("مدرسه", "دانشگاه"),
        ("دادگاه", "کلانتری"),
        ("بازار", "مغازه"),
        ("ساحل", "دریا"),
        ("جنگل", "پارک"),
        ("استخر", "باشگاه"),
        ("سینما", "تئاتر"),
        ("کتابخانه", "کتابفروشی"),
        ("هتل", "مهمانسرا"),
        ("بانک", "صرافی"),
        ("کافه", "رستوران"),
        ("موزه", "گالری"),
        ("پلیس", "نگهبان"),
        ("قطار", "مترو"),
        ("اتوبوس", "تاکسی"),
        ("کارخانه", "کارگاه"),
        ("فرود", "پرواز"),
        ("آشپزخانه", "رستوران"),
        ("کلاس", "جلسه"),
        ("پزشک", "پرستار"),
        ("داروخانه", "درمانگاه"),
        ("ورزشگاه", "باشگاه"),
        ("ساحل", "اسکله"),
        ("خیابان", "کوچه"),
        ("پل", "تونل"),
        ("پارکینگ", "گاراژ"),
        ("دفتر", "اداره"),
        ("کارمند", "مدیر"),
    ],
    "en": [
        ("Airport", "Station"), ("Hospital", "Clinic"), ("School", "University"),
        ("Court", "Police Station"), ("Market", "Shop"), ("Beach", "Sea"),
        ("Forest", "Park"), ("Pool", "Gym"), ("Cinema", "Theater"),
        ("Library", "Bookstore"), ("Hotel", "Hostel"), ("Bank", "Exchange"),
        ("Cafe", "Restaurant"), ("Museum", "Gallery"), ("Police", "Guard"),
        ("Train", "Metro"), ("Bus", "Taxi"), ("Factory", "Workshop"),
        ("Flight", "Landing"), ("Kitchen", "Restaurant"),
        ("Class", "Meeting"), ("Doctor", "Nurse"),
        ("Pharmacy", "Clinic"), ("Stadium", "Gym"),
        ("Beach", "Pier"), ("Street", "Alley"),
        ("Bridge", "Tunnel"), ("Parking", "Garage"),
        ("Office", "Department"), ("Employee", "Manager"),
    ],
    "tr": [
        ("Havalimanı", "İstasyon"), ("Hastane", "Klinik"), ("Okul", "Üniversite"),
        ("Mahkeme", "Karakol"), ("Pazar", "Mağaza"), ("Plaj", "Deniz"),
        ("Orman", "Park"), ("Havuz", "Spor Salonu"),
        ("Sinema", "Tiyatro"), ("Kütüphane", "Kitapçı"),
        ("Otel", "Pansiyon"), ("Banka", "Dövizci"),
        ("Kafe", "Restoran"), ("Müze", "Galeri"),
        ("Polis", "Güvenlik"), ("Tren", "Metro"),
        ("Otobüs", "Taksi"), ("Fabrika", "Atölye"),
        ("Uçuş", "İniş"), ("Mutfak", "Restoran"),
        ("Sınıf", "Toplantı"), ("Doktor", "Hemşire"),
        ("Eczane", "Klinik"), ("Stadyum", "Salon"),
        ("Sahil", "İskele"), ("Cadde", "Sokak"),
        ("Köprü", "Tünel"), ("Otopark", "Garaj"),
        ("Ofis", "Departman"), ("Çalışan", "Müdür"),
    ],
    "ru": [
        ("Аэропорт", "Станция"), ("Больница", "Клиника"),
        ("Школа", "Университет"), ("Суд", "Полиция"),
        ("Рынок", "Магазин"), ("Пляж", "Море"),
        ("Лес", "Парк"), ("Бассейн", "Спортзал"),
        ("Кино", "Театр"), ("Библиотека", "Книжный"),
        ("Отель", "Хостел"), ("Банк", "Обмен"),
        ("Кафе", "Ресторан"), ("Музей", "Галерея"),
        ("Полиция", "Охрана"), ("Поезд", "Метро"),
        ("Автобус", "Такси"), ("Фабрика", "Мастерская"),
        ("Рейс", "Посадка"), ("Кухня", "Ресторан"),
        ("Класс", "Встреча"), ("Врач", "Медсестра"),
        ("Аптека", "Клиника"), ("Стадион", "Зал"),
        ("Берег", "Причал"), ("Улица", "Переулок"),
        ("Мост", "Тоннель"), ("Парковка", "Гараж"),
        ("Офис", "Отдел"), ("Работник", "Менеджер"),
    ],
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    await update.message.reply_text(
        "🌍 Choose language",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    games[q.from_user.id] = {
        "lang": lang,
        "state": "players",
        "msgs": []
    }
    await q.message.delete()
    await q.message.reply_text("👥 Number of players? (min 3)")

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
        await update.message.reply_text("❌ Minimum 3 players")
        return

    pair = random.choice(FAKE_PAIRS[game["lang"]])
    words = [pair[0]] * (n - 1) + [pair[1]]
    random.shuffle(words)

    game.update({
        "words": words,
        "real": pair[0],
        "fake": pair[1],
        "i": 0,
        "state": "playing"
    })
    await show_player(update, uid)

# ================= SHOW PLAYER =================
async def show_player(update, uid):
    game = games[uid]
    i = game["i"]
    kb = [[InlineKeyboardButton("👁 Show word", callback_data="show")]]
    msg = await update.message.reply_text(
        f"📱 Player {i+1}",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    game["msgs"].append(msg.message_id)

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    word = game["words"][game["i"]]

    kb = [[InlineKeyboardButton("👁 Seen", callback_data="seen")]]
    msg = await q.message.reply_text(f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))
    game["msgs"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    for mid in game["msgs"]:
        try:
            await context.bot.delete_message(q.message.chat_id, mid)
        except:
            pass
    game["msgs"].clear()

    game["i"] += 1
    if game["i"] >= len(game["words"]):
        kb = [[InlineKeyboardButton("🏁 End game", callback_data="end")]]
        await q.message.reply_text("🏁 End of players", reply_markup=InlineKeyboardMarkup(kb))
        return

    await show_player(q.message, uid)

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games.pop(uid)

    text = (
        "📌 Game result\n\n"
        f"🔑 Real word: {game['real']}\n"
        f"🎭 Fake word: {game['fake']}"
    )
    kb = [[InlineKeyboardButton("🔁 New game", callback_data="restart")]]
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
    app.add_handler(CallbackQueryHandler(show_word, pattern="show"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(end_game, pattern="end"))
    app.add_handler(CallbackQueryHandler(restart, pattern="restart"))
    app.add_handler(CommandHandler("text", set_players))
    app.add_handler(CommandHandler("players", set_players))
    app.add_handler(CommandHandler("set", set_players))
    app.add_handler(CommandHandler("count", set_players))
    app.add_handler(CommandHandler("number", set_players))
    app.add_handler(CommandHandler("n", set_players))
    app.add_handler(CommandHandler("p", set_players))
    app.add_handler(CommandHandler("num", set_players))
    app.add_handler(CommandHandler("players", set_players))
    app.add_handler(CommandHandler("startgame", set_players))
    app.add_handler(CommandHandler("go", set_players))
    app.add_handler(CommandHandler("begin", set_players))
    app.add_handler(CommandHandler("play", set_players))
    app.add_handler(CommandHandler("run", set_players))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", start))
    app.add_handler(CommandHandler("new", start))
    app.add_handler(CommandHandler("again", start))
    app.add_handler(CommandHandler("reset", start))
    app.add_handler(CommandHandler("lang", start))
    app.add_handler(CommandHandler("language", start))
    app.add_handler(CommandHandler("l", start))
    app.add_handler(CommandHandler("choose", start))
    app.add_handler(CommandHandler("select", start))
    app.add_handler(CommandHandler("pick", start))
    app.add_handler(CommandHandler("choose_lang", start))
    app.add_handler(CommandHandler("select_lang", start))
    app.add_handler(CommandHandler("pick_lang", start))
    app.add_handler(CommandHandler("choose_language", start))
    app.add_handler(CommandHandler("select_language", start))
    app.add_handler(CommandHandler("pick_language", start))
    app.add_handler(CommandHandler("language_choose", start))
    app.add_handler(CommandHandler("language_select", start))
    app.add_handler(CommandHandler("language_pick", start))
    app.add_handler(CommandHandler("lang_choose", start))
    app.add_handler(CommandHandler("lang_select", start))
    app.add_handler(CommandHandler("lang_pick", start))
    app.add_handler(CommandHandler("language_start", start))
    app.add_handler(CommandHandler("lang_start", start))
    app.add_handler(CommandHandler("language_begin", start))
    app.add_handler(CommandHandler("lang_begin", start))
    app.add_handler(CommandHandler("language_go", start))
    app.add_handler(CommandHandler("lang_go", start))
    app.add_handler(CommandHandler("language_run", start))
    app.add_handler(CommandHandler("lang_run", start))
    app.add_handler(CommandHandler("language_play", start))
    app.add_handler(CommandHandler("lang_play", start))
    app.add_handler(CommandHandler("language_reset", start))
    app.add_handler(CommandHandler("lang_reset", start))
    app.add_handler(CommandHandler("language_new", start))
    app.add_handler(CommandHandler("lang_new", start))
    app.add_handler(CommandHandler("language_again", start))
    app.add_handler(CommandHandler("lang_again", start))
    app.add_handler(CommandHandler("language_restart", start))
    app.add_handler(CommandHandler("lang_restart", start))
    app.add_handler(CommandHandler("language_startgame", start))
    app.add_handler(CommandHandler("lang_startgame", start))
    app.add_handler(CommandHandler("language_choosegame", start))
    app.add_handler(CommandHandler("lang_choosegame", start))
    app.add_handler(CommandHandler("language_selectgame", start))
    app.add_handler(CommandHandler("lang_selectgame", start))
    app.add_handler(CommandHandler("language_pickgame", start))
    app.add_handler(CommandHandler("lang_pickgame", start))
    app.add_handler(CommandHandler("language_choose_game", start))
    app.add_handler(CommandHandler("lang_choose_game", start))
    app.add_handler(CommandHandler("language_select_game", start))
    app.add_handler(CommandHandler("lang_select_game", start))
    app.add_handler(CommandHandler("language_pick_game", start))
    app.add_handler(CommandHandler("lang_pick_game", start))
    app.run_polling()

if __name__ == "__main__":
    main()

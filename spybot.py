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
        ("فرودگاه", "ایستگاه"), ("بیمارستان", "درمانگاه"), ("مدرسه", "دانشگاه"),
        ("دادگاه", "کلانتری"), ("بازار", "مغازه"), ("ساحل", "دریا"),
        ("جنگل", "پارک"), ("استخر", "باشگاه"), ("سینما", "تئاتر"),
        ("کتابخانه", "کتابفروشی"), ("هتل", "مهمانسرا"), ("بانک", "صرافی"),
        ("کافه", "رستوران"), ("موزه", "گالری"), ("قطار", "مترو"),
        ("اتوبوس", "تاکسی"), ("کارخانه", "کارگاه"), ("آشپزخانه", "رستوران"),
        ("پزشک", "پرستار"), ("داروخانه", "درمانگاه"), ("ورزشگاه", "باشگاه"),
        ("پل", "تونل"), ("خیابان", "کوچه"), ("پارکینگ", "گاراژ"),
        ("دفتر", "اداره"), ("کارمند", "مدیر"),
    ],
    "en": [
        ("Airport", "Station"), ("Hospital", "Clinic"), ("School", "University"),
        ("Court", "Police"), ("Market", "Shop"), ("Beach", "Sea"),
        ("Forest", "Park"), ("Pool", "Gym"), ("Cinema", "Theater"),
        ("Library", "Bookstore"), ("Hotel", "Hostel"), ("Bank", "Exchange"),
        ("Cafe", "Restaurant"), ("Museum", "Gallery"), ("Train", "Metro"),
        ("Bus", "Taxi"), ("Factory", "Workshop"), ("Kitchen", "Restaurant"),
        ("Doctor", "Nurse"), ("Pharmacy", "Clinic"), ("Stadium", "Gym"),
        ("Bridge", "Tunnel"), ("Street", "Alley"), ("Parking", "Garage"),
        ("Office", "Department"), ("Employee", "Manager"),
    ],
    "tr": [
        ("Havalimanı", "İstasyon"), ("Hastane", "Klinik"), ("Okul", "Üniversite"),
        ("Mahkeme", "Karakol"), ("Pazar", "Mağaza"), ("Plaj", "Deniz"),
        ("Orman", "Park"), ("Havuz", "Spor Salonu"), ("Sinema", "Tiyatro"),
        ("Kütüphane", "Kitapçı"), ("Otel", "Pansiyon"), ("Banka", "Dövizci"),
        ("Kafe", "Restoran"), ("Müze", "Galeri"), ("Tren", "Metro"),
        ("Otobüs", "Taksi"), ("Fabrika", "Atölye"), ("Mutfak", "Restoran"),
        ("Doktor", "Hemşire"), ("Eczane", "Klinik"), ("Stadyum", "Salon"),
        ("Köprü", "Tünel"), ("Cadde", "Sokak"), ("Otopark", "Garaj"),
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
        ("Поезд", "Метро"), ("Автобус", "Такси"),
        ("Фабрика", "Мастерская"), ("Кухня", "Ресторан"),
        ("Врач", "Медсестра"), ("Аптека", "Клиника"),
        ("Стадион", "Зал"), ("Мост", "Тоннель"),
        ("Улица", "Переулок"), ("Парковка", "Гараж"),
        ("Офис", "Отдел"), ("Работник", "Менеджер"),
    ],
}

TEXT = {
    "fa": {
        "choose": "🌍 Choose language",
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
        "choose": "🌍 Choose language",
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
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # پاک‌سازی هر چیزی که قبلاً بوده
    if uid in games:
        del games[uid]

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]

    await update.effective_chat.send_message(
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
        "msgs": [],
    }

    await q.message.delete()
    await q.message.reply_text(TEXT[lang]["players"])

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
        await update.message.reply_text(TEXT[game["lang"]]["players"])
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
    })

    await show_player(update.message, uid)

# ================= SHOW PLAYER =================
async def show_player_chat(context, chat_id, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["i"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show")]]
    msg = await context.bot.send_message(
        chat_id,
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

    word = game["words"][game["i"]]
    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    msg = await q.message.reply_text(f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))
    game["msgs"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]
    chat_id = q.message.chat_id

    # فقط پیام‌های موقت (کلمه) پاک می‌شن
    for mid in game["msgs"]:
        try:
            await context.bot.delete_message(chat_id, mid)
        except:
            pass
    game["msgs"].clear()

    # رفتن به نفر بعد
    game["i"] += 1

    if game["i"] >= len(game["words"]):
        kb = [[InlineKeyboardButton(TEXT[lang]["end"], callback_data="end")]]
        await context.bot.send_message(
            chat_id,
            TEXT[lang]["end"],
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    # 🔴 مهم: پیام جدید، نه q.message
    await show_player_chat(context, chat_id, uid)
# ================= END GAME =================
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
    await start(update, context)

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

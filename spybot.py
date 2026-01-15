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

# ================= FAKE PAIRS (30+ each) =================
FAKE_PAIRS = {
    "fa": [
        ("دریا", "ساحل"), ("گیلاس", "آلبالو"), ("سیب", "گلابی"), ("هلو", "شلیل"),
        ("پرتقال", "نارنگی"), ("قطار", "مترو"), ("فرودگاه", "ایستگاه"),
        ("رستوران", "کافه"), ("بازار", "مغازه"), ("دانشگاه", "مدرسه"),
        ("پزشک", "پرستار"), ("بیمارستان", "کلینیک"), ("هتل", "مسافرخانه"),
        ("کوه", "تپه"), ("جنگل", "پارک"), ("رودخانه", "نهر"),
        ("هواپیما", "هلیکوپتر"), ("سینما", "تئاتر"), ("کتابخانه", "کتابفروشی"),
        ("پلیس", "سرباز"), ("دادگاه", "کلانتری"), ("آشپز", "گارسون"),
        ("استخر", "ساحل"), ("باشگاه", "ورزشگاه"), ("بانک", "صرافی"),
        ("قهوه", "نسکافه"), ("چای", "دمنوش"), ("یخچال", "فریزر"),
        ("اتوبوس", "مینی‌بوس"), ("تاکسی", "اسنپ"),
    ],
    "en": [
        ("Sea", "Beach"), ("Cherry", "Sour Cherry"), ("Apple", "Pear"),
        ("Peach", "Nectarine"), ("Orange", "Mandarin"), ("Train", "Subway"),
        ("Airport", "Station"), ("Restaurant", "Cafe"), ("Market", "Shop"),
        ("University", "School"), ("Doctor", "Nurse"), ("Hospital", "Clinic"),
        ("Hotel", "Motel"), ("Mountain", "Hill"), ("Forest", "Park"),
        ("River", "Stream"), ("Airplane", "Helicopter"), ("Cinema", "Theater"),
        ("Library", "Bookstore"), ("Police", "Soldier"), ("Court", "Station"),
        ("Chef", "Waiter"), ("Pool", "Beach"), ("Gym", "Stadium"),
        ("Bank", "Exchange"), ("Coffee", "Latte"), ("Tea", "Herbal Tea"),
        ("Fridge", "Freezer"), ("Bus", "Minibus"), ("Taxi", "Uber"),
    ],
    "tr": [
        ("Deniz", "Sahil"), ("Kiraz", "Vişne"), ("Elma", "Armut"),
        ("Şeftali", "Nektarin"), ("Portakal", "Mandalina"), ("Tren", "Metro"),
        ("Havalimanı", "İstasyon"), ("Restoran", "Kafe"), ("Pazar", "Mağaza"),
        ("Üniversite", "Okul"), ("Doktor", "Hemşire"), ("Hastane", "Klinik"),
        ("Otel", "Pansiyon"), ("Dağ", "Tepe"), ("Orman", "Park"),
        ("Nehir", "Dere"), ("Uçak", "Helikopter"), ("Sinema", "Tiyatro"),
        ("Kütüphane", "Kitapçı"), ("Polis", "Asker"), ("Mahkeme", "Karakol"),
        ("Aşçı", "Garson"), ("Havuz", "Sahil"), ("Spor Salonu", "Stadyum"),
        ("Banka", "Dövizci"), ("Kahve", "Latte"), ("Çay", "Bitki Çayı"),
        ("Buzdolabı", "Derin Dondurucu"), ("Otobüs", "Minibüs"), ("Taksi", "Uber"),
    ],
    "ru": [
        ("Море", "Пляж"), ("Вишня", "Черешня"), ("Яблоко", "Груша"),
        ("Персик", "Нектарин"), ("Апельсин", "Мандарин"), ("Поезд", "Метро"),
        ("Аэропорт", "Станция"), ("Ресторан", "Кафе"), ("Рынок", "Магазин"),
        ("Университет", "Школа"), ("Врач", "Медсестра"), ("Больница", "Клиника"),
        ("Отель", "Хостел"), ("Гора", "Холм"), ("Лес", "Парк"),
        ("Река", "Ручей"), ("Самолёт", "Вертолёт"), ("Кинотеатр", "Театр"),
        ("Библиотека", "Книжный"), ("Полиция", "Солдат"), ("Суд", "Участок"),
        ("Повар", "Официант"), ("Бассейн", "Пляж"), ("Спортзал", "Стадион"),
        ("Банк", "Обменник"), ("Кофе", "Латте"), ("Чай", "Травяной чай"),
        ("Холодильник", "Морозилка"), ("Автобус", "Маршрутка"), ("Такси", "Uber"),
    ],
}

# ================= TEXT =================
TEXT = {
    "fa": {
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟ (حداقل ۳)",
        "start": "🎮 شروع بازی",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "player": "📱 بازیکن",
        "end": "🏁 پایان بازی",
        "restart": "🔁 شروع بازی جدید",
        "result": "📌 نتیجه بازی:\n\n🔑 کلمه اصلی: {real}\n🎭 کلمه متفاوت: {fake}",
    },
    "en": {
        "players": "👥 How many players? (min 3)",
        "start": "🎮 Start Game",
        "show": "👁 Show word",
        "seen": "👁 Seen",
        "player": "📱 Player",
        "end": "🏁 End Game",
        "restart": "🔁 New Game",
        "result": "📌 Game Result:\n\n🔑 Real word: {real}\n🎭 Fake word: {fake}",
    },
    "tr": {
        "players": "👥 Kaç oyuncu var? (en az 3)",
        "start": "🎮 Oyunu Başlat",
        "show": "👁 Kelimeyi Gör",
        "seen": "👁 Gördüm",
        "player": "📱 Oyuncu",
        "end": "🏁 Oyunu Bitir",
        "restart": "🔁 Yeni Oyun",
        "result": "📌 Oyun Sonucu:\n\n🔑 Gerçek kelime: {real}\n🎭 Farklı kelime: {fake}",
    },
    "ru": {
        "players": "👥 Сколько игроков? (мин 3)",
        "start": "🎮 Начать игру",
        "show": "👁 Показать слово",
        "seen": "👁 Видел",
        "player": "📱 Игрок",
        "end": "🏁 Завершить игру",
        "restart": "🔁 Новая игра",
        "result": "📌 Результат игры:\n\n🔑 Основное слово: {real}\n🎭 Другое слово: {fake}",
    },
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "🕵️ Spy Game\nChoose language 👇",
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    games[q.from_user.id] = {"lang": lang, "state": "players"}
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
        return
    real, fake = random.choice(FAKE_PAIRS[game["lang"]])
    words = [real] * (n - 1) + [fake]
    random.shuffle(words)
    game.update({
        "players": n,
        "words": words,
        "real": real,
        "fake": fake,
        "current": 0,
        "state": "playing",
        "temp": [],
    })
    kb = [[InlineKeyboardButton(TEXT[game["lang"]]["start"], callback_data="start_game")]]
    await update.message.reply_text("📱 گوشی دست نفر اول", reply_markup=InlineKeyboardMarkup(kb))

# ================= START GAME =================
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    await show_player(q.message, uid)

# ================= SHOW PLAYER =================
async def show_player(message, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["current"]
    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show_word")]]
    msg = await message.reply_text(
        f"{TEXT[lang]['player']} {i + 1}",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    game["temp"].append(msg.message_id)

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]
    word = game["words"][game["current"]]
    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    msg = await q.message.reply_text(f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))
    game["temp"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    for mid in game["temp"]:
        try:
            await context.bot.delete_message(q.message.chat_id, mid)
        except:
            pass
    game["temp"] = []
    game["current"] += 1

    if game["current"] >= game["players"]:
        kb = [[InlineKeyboardButton(TEXT[lang]["end"], callback_data="end_game")]]
        await q.message.reply_text(TEXT[lang]["end"], reply_markup=InlineKeyboardMarkup(kb))
        return

    await show_player(q.message, uid)

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    text = TEXT[lang]["result"].format(real=game["real"], fake=game["fake"])
    kb = [[InlineKeyboardButton(TEXT[lang]["restart"], callback_data="restart")]]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

# ================= RESTART =================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    games.pop(q.from_user.id, None)
    await start(q, context)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
    app.add_handler(CallbackQueryHandler(start_game, pattern="start_game"))
    app.add_handler(CallbackQueryHandler(show_word, pattern="show_word"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(end_game, pattern="end_game"))
    app.add_handler(CallbackQueryHandler(restart, pattern="restart"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))
    app.run_polling()

if __name__ == "__main__":
    main()

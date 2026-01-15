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
        ("گیلاس", "آلبالو"), ("سیب", "گلابی"), ("پرتقال", "نارنگی"), ("لیمو", "لیموترش"), ("هلو", "شلیل"),
        ("دریا", "اقیانوس"), ("رودخانه", "نهر"), ("جنگل", "پارک"), ("کوه", "تپه"), ("ساحل", "دریا"),
        ("مدرسه", "دانشگاه"), ("دانشجو", "دانش‌آموز"), ("معلم", "استاد"), ("کلاس", "آمفی‌تئاتر"), ("کتابخانه", "کتاب‌فروشی"),
        ("بیمارستان", "کلینیک"), ("پزشک", "پرستار"), ("داروخانه", "درمانگاه"), ("آمبولانس", "اورژانس"), ("بخش", "اتاق"),
        ("فرودگاه", "ایستگاه"), ("هواپیما", "هلیکوپتر"), ("قطار", "مترو"), ("تاکسی", "اتوبوس"), ("سفر", "مسافرت"),
        ("پلیس", "سرباز"), ("دادگاه", "کلانتری"), ("قاضی", "وکیل"), ("زندان", "بازداشتگاه"), ("قانون", "مقررات"),
        ("رستوران", "کافه"), ("غذا", "خوراک"), ("آشپز", "گارسون"), ("منو", "لیست"), ("سفارش", "رزرو"),
    ],
    "en": [
        ("Cherry", "Sour Cherry"), ("Apple", "Pear"), ("Orange", "Mandarin"), ("Lemon", "Lime"), ("Peach", "Nectarine"),
        ("Sea", "Ocean"), ("River", "Stream"), ("Forest", "Park"), ("Mountain", "Hill"), ("Beach", "Coast"),
        ("School", "University"), ("Student", "Pupil"), ("Teacher", "Professor"), ("Class", "Lecture Hall"), ("Library", "Bookstore"),
        ("Hospital", "Clinic"), ("Doctor", "Nurse"), ("Pharmacy", "Drugstore"), ("Ambulance", "Emergency"), ("Ward", "Room"),
        ("Airport", "Station"), ("Airplane", "Helicopter"), ("Train", "Subway"), ("Taxi", "Bus"), ("Trip", "Travel"),
        ("Police", "Soldier"), ("Court", "Police Station"), ("Judge", "Lawyer"), ("Prison", "Jail"), ("Law", "Regulation"),
        ("Restaurant", "Cafe"), ("Food", "Meal"), ("Chef", "Waiter"), ("Menu", "List"), ("Order", "Reservation"),
    ],
    "tr": [
        ("Kiraz", "Vişne"), ("Elma", "Armut"), ("Portakal", "Mandalina"), ("Limon", "Misket Limonu"), ("Şeftali", "Nektarin"),
        ("Deniz", "Okyanus"), ("Nehir", "Dere"), ("Orman", "Park"), ("Dağ", "Tepe"), ("Sahil", "Kıyı"),
        ("Okul", "Üniversite"), ("Öğrenci", "Talebe"), ("Öğretmen", "Profesör"), ("Sınıf", "Amfi"), ("Kütüphane", "Kitapçı"),
        ("Hastane", "Klinik"), ("Doktor", "Hemşire"), ("Eczane", "Sağlık Ocağı"), ("Ambulans", "Acil"), ("Servis", "Oda"),
        ("Havalimanı", "İstasyon"), ("Uçak", "Helikopter"), ("Tren", "Metro"), ("Taksi", "Otobüs"), ("Seyahat", "Gezi"),
        ("Polis", "Asker"), ("Mahkeme", "Karakol"), ("Hakim", "Avukat"), ("Hapishane", "Cezaevi"), ("Kanun", "Yönetmelik"),
        ("Restoran", "Kafe"), ("Yemek", "Gıda"), ("Aşçı", "Garson"), ("Menü", "Liste"), ("Sipariş", "Rezervasyon"),
    ],
    "ru": [
        ("Вишня", "Черешня"), ("Яблоко", "Груша"), ("Апельсин", "Мандарин"), ("Лимон", "Лайм"), ("Персик", "Нектарин"),
        ("Море", "Океан"), ("Река", "Ручей"), ("Лес", "Парк"), ("Гора", "Холм"), ("Пляж", "Берег"),
        ("Школа", "Университет"), ("Студент", "Ученик"), ("Учитель", "Преподаватель"), ("Класс", "Аудитория"), ("Библиотека", "Книжный магазин"),
        ("Больница", "Клиника"), ("Врач", "Медсестра"), ("Аптека", "Поликлиника"), ("Скорая", "Экстренная помощь"), ("Палата", "Комната"),
        ("Аэропорт", "Станция"), ("Самолёт", "Вертолёт"), ("Поезд", "Метро"), ("Такси", "Автобус"), ("Путешествие", "Поездка"),
        ("Полиция", "Солдат"), ("Суд", "Участок"), ("Судья", "Адвокат"), ("Тюрьма", "Изолятор"), ("Закон", "Правило"),
        ("Ресторан", "Кафе"), ("Еда", "Блюдо"), ("Повар", "Официант"), ("Меню", "Список"), ("Заказ", "Бронь"),
    ],
}

# ================= TEXT =================
TEXT = {
    "fa": {
        "choose_lang": "🌍 زبان را انتخاب کنید",
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟",
        "ready": "📱 همه آماده‌اید؟ گوشی دست نفر اول",
        "start": "🎮 شروع بازی",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "next": "➡️ نفر بعد",
        "word": "🔑 کلمه: ",
        "end": "✅ همه کلمه‌ها دیده شد\n🕵️ بازی شروع شد!",
        "summary": "🏁 پایان بازی",
        "restart": "🔁 شروع بازی جدید",
        "end_btn": "🏁 پایان بازی",
        "player": "📱 بازیکن",
    }
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
    await update.message.reply_text("🕵️ Spy Game\nChoose language 👇", reply_markup=InlineKeyboardMarkup(kb))

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    games[q.from_user.id] = {"lang": lang, "state": "players", "control_messages": []}
    await q.message.reply_text(TEXT[lang]["players"])

# ================= PLAYERS =================
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    game = games.get(uid)
    if not game or game["state"] != "players":
        return
    try:
        players = int(update.message.text)
    except:
        return
    if players < 3:
        return
    game["players"] = players
    game["state"] = "ready"
    kb = [[InlineKeyboardButton(TEXT[game["lang"]]["start"], callback_data="start_game")]]
    await update.message.reply_text(TEXT[game["lang"]]["ready"], reply_markup=InlineKeyboardMarkup(kb))

# ================= START GAME =================
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    players = game["players"]
    spies = 1 if players <= 4 else random.randint(1, players // 2)
    roles = ["spy"] * spies + ["player"] * (players - spies)
    random.shuffle(roles)

    real_word, fake_word = random.choice(FAKE_PAIRS[game["lang"]])

    game.update({
        "roles": roles,
        "real_word": real_word,
        "fake_word": fake_word,
        "current": 0,
        "temp_messages": [],
        "state": "playing",
        "spy_count": spies,
    })
    await show_player(q.message, uid)

# ================= SHOW PLAYER =================
async def show_player(message, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["current"]
    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show_role")]]
    await message.reply_text(f"{TEXT[lang]['player']} {i+1}", reply_markup=InlineKeyboardMarkup(kb))

# ================= SHOW ROLE =================
async def show_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    word = game["fake_word"] if game["roles"][game["current"]] == "spy" else game["real_word"]
    kb = [[InlineKeyboardButton(TEXT[game["lang"]]["seen"], callback_data="seen")]]
    await q.message.reply_text(TEXT[game["lang"]]["word"] + word, reply_markup=InlineKeyboardMarkup(kb))

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    game["current"] += 1
    if game["current"] >= game["players"]:
        summary = (
            f"{TEXT[game['lang']]['summary']}\n\n"
            f"🔑 کلمه اصلی: {game['real_word']}\n"
            f"🎭 کلمه متفاوت: {game['fake_word']}"
        )
        kb = [[InlineKeyboardButton(TEXT[game["lang"]]["restart"], callback_data="restart")]]
        await q.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(kb))
        return
    await show_player(q.message, uid)

# ================= RESTART =================
async def restart_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = games[q.from_user.id]["lang"]
    games[q.from_user.id] = {"lang": lang, "state": "players", "control_messages": []}
    await q.message.reply_text(TEXT[lang]["players"])

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
    app.add_handler(CallbackQueryHandler(start_game, pattern="start_game"))
    app.add_handler(CallbackQueryHandler(show_role, pattern="show_role"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(restart_game, pattern="restart"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()

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

# ================= FAKE WORD PAIRS (30+ each) =================
FAKE_PAIRS = {
    "fa": [
        ("گیلاس","آلبالو"),("سیب","گلابی"),("پرتقال","نارنگی"),("لیمو","لیموترش"),
        ("هلو","شلیل"),("دریا","اقیانوس"),("ساحل","دریا"),("رودخانه","نهر"),
        ("جنگل","پارک"),("کوه","تپه"),("مدرسه","دانشگاه"),("دانش‌آموز","دانشجو"),
        ("معلم","استاد"),("کلاس","آمفی‌تئاتر"),("کتابخانه","کتاب‌فروشی"),
        ("بیمارستان","کلینیک"),("پزشک","پرستار"),("داروخانه","درمانگاه"),
        ("آمبولانس","اورژانس"),("فرودگاه","ایستگاه"),("هواپیما","هلیکوپتر"),
        ("قطار","مترو"),("تاکسی","اتوبوس"),("سفر","مسافرت"),
        ("پلیس","سرباز"),("دادگاه","کلانتری"),("قاضی","وکیل"),
        ("رستوران","کافه"),("منو","لیست"),("سفارش","رزرو"),
    ],
    "en": [
        ("Cherry","Sour Cherry"),("Apple","Pear"),("Orange","Mandarin"),
        ("Lemon","Lime"),("Peach","Nectarine"),("Sea","Ocean"),
        ("Beach","Coast"),("River","Stream"),("Forest","Park"),
        ("Mountain","Hill"),("School","University"),("Student","Pupil"),
        ("Teacher","Professor"),("Class","Lecture Hall"),
        ("Library","Bookstore"),("Hospital","Clinic"),
        ("Doctor","Nurse"),("Pharmacy","Drugstore"),
        ("Ambulance","Emergency"),("Airport","Station"),
        ("Airplane","Helicopter"),("Train","Subway"),
        ("Taxi","Bus"),("Trip","Travel"),
        ("Police","Soldier"),("Court","Police Station"),
        ("Judge","Lawyer"),("Restaurant","Cafe"),
        ("Menu","List"),("Order","Reservation"),
    ],
    "tr": [
        ("Kiraz","Vişne"),("Elma","Armut"),("Portakal","Mandalina"),
        ("Limon","Misket Limonu"),("Şeftali","Nektarin"),
        ("Deniz","Okyanus"),("Sahil","Kıyı"),("Nehir","Dere"),
        ("Orman","Park"),("Dağ","Tepe"),("Okul","Üniversite"),
        ("Öğrenci","Talebe"),("Öğretmen","Profesör"),
        ("Sınıf","Amfi"),("Kütüphane","Kitapçı"),
        ("Hastane","Klinik"),("Doktor","Hemşire"),
        ("Eczane","Sağlık Ocağı"),("Ambulans","Acil"),
        ("Havalimanı","İstasyon"),("Uçak","Helikopter"),
        ("Tren","Metro"),("Taksi","Otobüs"),
        ("Seyahat","Gezi"),("Polis","Asker"),
        ("Mahkeme","Karakol"),("Hakim","Avukat"),
        ("Restoran","Kafe"),("Menü","Liste"),
        ("Sipariş","Rezervasyon"),
    ],
    "ru": [
        ("Вишня","Черешня"),("Яблоко","Груша"),
        ("Апельсин","Мандарин"),("Лимон","Лайм"),
        ("Персик","Нектарин"),("Море","Океан"),
        ("Пляж","Берег"),("Река","Ручей"),
        ("Лес","Парк"),("Гора","Холм"),
        ("Школа","Университет"),("Студент","Ученик"),
        ("Учитель","Преподаватель"),("Класс","Аудитория"),
        ("Библиотека","Книжный магазин"),
        ("Больница","Клиника"),("Врач","Медсестра"),
        ("Аптека","Поликлиника"),("Скорая","Экстренная помощь"),
        ("Аэропорт","Станция"),("Самолёт","Вертолёт"),
        ("Поезд","Метро"),("Такси","Автобус"),
        ("Путешествие","Поездка"),("Полиция","Солдат"),
        ("Суд","Участок"),("Судья","Адвокат"),
        ("Ресторан","Кафе"),("Меню","Список"),
        ("Заказ","Бронь"),
    ],
}

TEXT = {
    "fa": {
        "choose": "🕵️ Spy Game\nزبان را انتخاب کنید 👇",
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟\n(حداقل 3 نفر)",
        "ready": "📱 همه آماده‌اید؟ گوشی دست نفر اول",
        "start": "🎮 شروع بازی",
        "player": "📱 بازیکن",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "show_result": "🏁 نمایش نتیجه",
        "summary": "🏁 پایان بازی",
        "restart": "🔁 شروع بازی جدید",
    },
    "en": {
        "choose": "🕵️ Spy Game\nChoose language 👇",
        "players": "👥 How many players? (min 3)",
        "ready": "📱 Everyone ready? Phone to Player 1",
        "start": "🎮 Start Game",
        "player": "📱 Player",
        "show": "👁 Show word",
        "seen": "👁 Seen",
        "show_result": "🏁 Show result",
        "summary": "🏁 Game Over",
        "restart": "🔁 New Game",
    },
    "tr": {
        "choose": "🕵️ Spy Game\nDil seçin 👇",
        "players": "👥 Kaç oyuncu var? (en az 3)",
        "ready": "📱 Herkes hazır mı? Telefon 1. oyuncuda",
        "start": "🎮 Oyunu Başlat",
        "player": "📱 Oyuncu",
        "show": "👁 Kelimeyi Gör",
        "seen": "👁 Gördüm",
        "show_result": "🏁 Sonucu Göster",
        "summary": "🏁 Oyun Bitti",
        "restart": "🔁 Yeni Oyun",
    },
    "ru": {
        "choose": "🕵️ Spy Game\nВыберите язык 👇",
        "players": "👥 Сколько игроков? (минимум 3)",
        "ready": "📱 Все готовы? Телефон у игрока 1",
        "start": "🎮 Начать игру",
        "player": "📱 Игрок",
        "show": "👁 Показать слово",
        "seen": "👁 Видел",
        "show_result": "🏁 Показать результат",
        "summary": "🏁 Игра окончена",
        "restart": "🔁 Новая игра",
    },
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
    ]
    await update.message.reply_text(TEXT["fa"]["choose"], reply_markup=InlineKeyboardMarkup(kb))

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    uid = q.from_user.id

    games[uid] = {"lang": lang, "state": "players"}
    await q.message.edit_text(TEXT[lang]["players"])

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
    real_word, fake_word = random.choice(FAKE_PAIRS[game["lang"]])

    game.update({
        "state": "playing",
        "players": players,
        "roles": roles,
        "real_word": real_word,
        "fake_word": fake_word,
        "current": 0,
        "ui_message_id": None,
    })

    kb = [[InlineKeyboardButton(TEXT[game["lang"]]["start"], callback_data="start_game")]]
    msg = await update.message.reply_text(TEXT[game["lang"]]["ready"], reply_markup=InlineKeyboardMarkup(kb))
    game["ui_message_id"] = msg.message_id

# ================= START GAME =================
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await show_player(context, q.message.chat_id, q.from_user.id)

# ================= SHOW PLAYER =================
async def show_player(context, chat_id, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show_word")]]
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=game["ui_message_id"],
        text=f"{TEXT[lang]['player']} {i+1}",
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    word = game["fake_word"] if game["roles"][game["current"]] == "spy" else game["real_word"]
    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]

    await q.message.edit_text(f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    game["current"] += 1
    if game["current"] >= game["players"]:
        kb = [[InlineKeyboardButton(TEXT[lang]["show_result"], callback_data="show_result")]]
        await context.bot.send_message(
            chat_id=q.message.chat_id,
            text="📱 همه بازیکن‌ها کلمه رو دیدن",
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
    lang = game["lang"]

    kb = [[InlineKeyboardButton(TEXT[lang]["restart"], callback_data="restart")]]
    await q.message.edit_text(
        f"{TEXT[lang]['summary']}\n\n"
        f"🔑 {game['real_word']}\n"
        f"🎭 {game['fake_word']}",
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ================= RESTART =================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await start(update, context)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(start_game, pattern="^start_game$"))
    app.add_handler(CallbackQueryHandler(show_word, pattern="^show_word$"))
    app.add_handler(CallbackQueryHandler(seen, pattern="^seen$"))
    app.add_handler(CallbackQueryHandler(show_result, pattern="^show_result$"))
    app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))

    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()

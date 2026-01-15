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


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa")]]
    await update.message.reply_text(
        "🕵️ Spy Game\nChoose language 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    lang = q.data.split("_")[1]

    games[uid] = {"lang": lang, "state": "players"}
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

    roles = ["spy"] + ["player"] * (game["players"] - 1)
    random.shuffle(roles)

    real_word, fake_word = random.choice(FAKE_PAIRS[game["lang"]])

    game.update({
        "roles": roles,
        "real_word": real_word,
        "fake_word": fake_word,
        "current": 0,
        "temp": [],
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
        f"{TEXT[lang]['player']} {i+1}",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    game["temp"].append(msg.message_id)

# ================= SHOW ROLE =================
async def show_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    word = game["fake_word"] if game["roles"][game["current"]] == "spy" else game["real_word"]

    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    msg = await q.message.reply_text(TEXT[lang]["word"] + word, reply_markup=InlineKeyboardMarkup(kb))
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

    # ⛔ هنوز پایان بازی نیست
    if game["current"] < game["players"]:
        return await show_player(q.message, uid)

    # ✅ فقط دکمه پایان بازی
    kb = [[InlineKeyboardButton(TEXT[lang]["end_btn"], callback_data="end_game")]]
    await q.message.reply_text(TEXT[lang]["end_btn"], reply_markup=InlineKeyboardMarkup(kb))

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    summary = (
        f"{TEXT[lang]['summary']}\n\n"
        f"🔑 کلمه اصلی: {game['real_word']}\n"
        f"🎭 کلمه متفاوت: {game['fake_word']}"
    )

    kb = [[InlineKeyboardButton(TEXT[lang]["restart"], callback_data="restart")]]
    await q.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(kb))

# ================= RESTART =================
async def restart_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = games[q.from_user.id]["lang"]
    games[q.from_user.id] = {"lang": lang, "state": "players"}
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

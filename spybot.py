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
    "fa": [("گیلاس","آلبالو"),("سیب","گلابی"),("رستوران","کافه"),("قطار","مترو"),("ساحل","دریا"),
           ("مدرسه","دانشگاه"),("پزشک","پرستار"),("هواپیما","هلیکوپتر"),("پلیس","سرباز"),("قاضی","وکیل"),
           ("بازار","مغازه"),("پارک","جنگل"),("بانک","صرافی"),("کتابخانه","کتابفروشی"),("سینما","تئاتر"),
           ("کلاس","آمفی‌تئاتر"),("دانشجو","دانش‌آموز"),("آشپز","گارسون"),("دادگاه","کلانتری"),("زندان","بازداشتگاه"),
           ("فرودگاه","ایستگاه"),("هتل","مسافرخانه"),("استخر","باشگاه"),("موزه","نمایشگاه"),("سفر","مسافرت"),
           ("داروخانه","درمانگاه"),("آمبولانس","اورژانس"),("قطب","شمال"),("کوه","تپه"),("خیابان","کوچه")],

    "en": [("Cherry","Sour Cherry"),("Apple","Pear"),("Restaurant","Cafe"),("Train","Subway"),("Beach","Sea"),
           ("School","University"),("Doctor","Nurse"),("Plane","Helicopter"),("Police","Soldier"),("Judge","Lawyer"),
           ("Market","Shop"),("Park","Forest"),("Bank","Exchange"),("Library","Bookstore"),("Cinema","Theater"),
           ("Class","Lecture Hall"),("Student","Pupil"),("Chef","Waiter"),("Court","Station"),("Prison","Jail"),
           ("Airport","Station"),("Hotel","Hostel"),("Pool","Gym"),("Museum","Gallery"),("Trip","Travel"),
           ("Pharmacy","Clinic"),("Ambulance","Emergency"),("Pole","North"),("Mountain","Hill"),("Street","Alley")],

    "tr": [("Kiraz","Vişne"),("Elma","Armut"),("Restoran","Kafe"),("Tren","Metro"),("Sahil","Deniz"),
           ("Okul","Üniversite"),("Doktor","Hemşire"),("Uçak","Helikopter"),("Polis","Asker"),("Hakim","Avukat"),
           ("Pazar","Mağaza"),("Park","Orman"),("Banka","Döviz"),("Kütüphane","Kitapçı"),("Sinema","Tiyatro"),
           ("Sınıf","Amfi"),("Öğrenci","Talebe"),("Aşçı","Garson"),("Mahkeme","Karakol"),("Hapishane","Cezaevi"),
           ("Havalimanı","İstasyon"),("Otel","Pansiyon"),("Havuz","Spor Salonu"),("Müze","Sergi"),("Gezi","Seyahat"),
           ("Eczane","Klinik"),("Ambulans","Acil"),("Kutup","Kuzey"),("Dağ","Tepe"),("Cadde","Sokak")],

    "ru": [("Вишня","Черешня"),("Яблоко","Груша"),("Ресторан","Кафе"),("Поезд","Метро"),("Пляж","Море"),
           ("Школа","Университет"),("Врач","Медсестра"),("Самолёт","Вертолёт"),("Полиция","Солдат"),("Судья","Адвокат"),
           ("Рынок","Магазин"),("Парк","Лес"),("Банк","Обмен"),("Библиотека","Книжный"),("Кино","Театр"),
           ("Класс","Аудитория"),("Студент","Ученик"),("Повар","Официант"),("Суд","Участок"),("Тюрьма","Изолятор"),
           ("Аэропорт","Станция"),("Отель","Хостел"),("Бассейн","Зал"),("Музей","Выставка"),("Поездка","Путешествие"),
           ("Аптека","Клиника"),("Скорая","Экстренная"),("Полюс","Север"),("Гора","Холм"),("Улица","Переулок")]
}

# ================= TEXT =================
TEXT = {
    "fa": {
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟ (حداقل ۳)",
        "ready": "📱 همه آماده‌اید؟ گوشی دست نفر اول",
        "start": "🎮 شروع بازی",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "player": "📱 بازیکن",
        "all_seen": "✅ همه بازیکن‌ها کلمه رو دیدن",
        "show_result": "🏁 نمایش نتیجه",
        "restart": "🔁 شروع بازی جدید",
        "result": "🏁 پایان بازی\n\n🔑 کلمه اصلی: {real}\n🎭 کلمه متفاوت: {fake}",
        "min": "حداقل ۳ نفر لازم است"
    }
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    games.pop(uid, None)

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]

    await update.message.reply_text(
        "🕵️ Spy Game\nChoose language 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    games[q.from_user.id] = {"lang": lang, "state": "players"}
    await q.message.reply_text(TEXT["fa"]["players"])

# ================= PLAYERS =================
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
        await update.message.reply_text(TEXT["fa"]["min"])
        return

    game.update({"players": n, "state": "ready"})
    kb = [[InlineKeyboardButton(TEXT["fa"]["start"], callback_data="start_game")]]
    await update.message.reply_text(TEXT["fa"]["ready"], reply_markup=InlineKeyboardMarkup(kb))


# ================= START GAME =================
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    spies = 1
    roles = ["spy"] + ["player"] * (game["players"] - 1)
    random.shuffle(roles)
    real, fake = random.choice(FAKE_PAIRS[game["lang"]])

    game.update({
        "roles": roles,
        "real": real,
        "fake": fake,
        "current": 0,
        "state": "showing"
    })

    await show_player(q.message, uid)

# ================= SHOW PLAYER =================
async def show_player(message, uid):
    game = games[uid]
    i = game["current"]
    kb = [[InlineKeyboardButton(TEXT["fa"]["show"], callback_data="show_word")]]
    await message.reply_text(f"{TEXT['fa']['player']} {i+1}", reply_markup=InlineKeyboardMarkup(kb))

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    word = game["fake"] if game["roles"][game["current"]] == "spy" else game["real"]
    kb = [[InlineKeyboardButton(TEXT["fa"]["seen"], callback_data="seen")]]
    await q.message.reply_text(f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    game["current"] += 1

    if game["current"] >= game["players"]:
        kb = [[InlineKeyboardButton(TEXT["fa"]["show_result"], callback_data="result")]]
        await q.message.reply_text(TEXT["fa"]["all_seen"], reply_markup=InlineKeyboardMarkup(kb))
        return

    await show_player(q.message, uid)

# ================= RESULT =================
async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    text = TEXT["fa"]["result"].format(real=game["real"], fake=game["fake"])
    kb = [[InlineKeyboardButton(TEXT["fa"]["restart"], callback_data="restart")]]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

# ================= RESTART =================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    games.pop(q.from_user.id, None)
    await start(update, context)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
    app.add_handler(CallbackQueryHandler(start_game, pattern="start_game"))
    app.add_handler(CallbackQueryHandler(show_word, pattern="show_word"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(result, pattern="result"))
    app.add_handler(CallbackQueryHandler(restart, pattern="restart"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))
    app.run_polling()

if __name__ == "__main__":
    main()

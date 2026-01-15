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
        "choose": "🌍 زبان را انتخاب کنید",
        "players": "👥 تعداد بازیکن‌ها؟ (حداقل ۳)",
        "ready": "📱 گوشی دست بازیکن اول",
        "player": "📱 بازیکن",
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "end_btn": "🏁 پایان بازی",
        "restart": "🔁 شروع دوباره",
        "summary": "🏁 پایان بازی\n\n🔑 کلمه اصلی: {real}\n🎭 کلمه متفاوت: {fake}",
        "min": "❗ حداقل ۳ نفر لازم است",
    },
    "en": {
        "choose": "🌍 Choose language",
        "players": "👥 Number of players? (min 3)",
        "ready": "📱 Phone to Player 1",
        "player": "📱 Player",
        "show": "👁 Show word",
        "seen": "👁 Seen",
        "end_btn": "🏁 End game",
        "restart": "🔁 New game",
        "summary": "🏁 Game Over\n\n🔑 Real word: {real}\n🎭 Fake word: {fake}",
        "min": "❗ At least 3 players required",
    },
    "tr": {
        "choose": "🌍 Dil seçin",
        "players": "👥 Oyuncu sayısı? (min 3)",
        "ready": "📱 Telefon 1. oyuncuda",
        "player": "📱 Oyuncu",
        "show": "👁 Kelimeyi gör",
        "seen": "👁 Gördüm",
        "end_btn": "🏁 Oyunu bitir",
        "restart": "🔁 Yeni oyun",
        "summary": "🏁 Oyun Bitti\n\n🔑 Gerçek: {real}\n🎭 Sahte: {fake}",
        "min": "❗ En az 3 oyuncu",
    },
    "ru": {
        "choose": "🌍 Выберите язык",
        "players": "👥 Сколько игроков? (мин 3)",
        "ready": "📱 Телефон у игрока 1",
        "player": "📱 Игрок",
        "show": "👁 Показать слово",
        "seen": "👁 Видел",
        "end_btn": "🏁 Завершить",
        "restart": "🔁 Новая игра",
        "summary": "🏁 Конец игры\n\n🔑 Основное: {real}\n🎭 Другое: {fake}",
        "min": "❗ Минимум 3 игрока",
    },
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    games.pop(uid, None)

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
    await update.message.reply_text(TEXT["fa"]["choose"], reply_markup=InlineKeyboardMarkup(kb))

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    uid = q.from_user.id

    games[uid] = {"lang": lang, "state": "players"}
    await q.message.reply_text(TEXT[lang]["players"])

# ================= SET PLAYERS =================
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    game = games.get(uid)
    if not game or game["state"] != "players":
        return

    try:
        n = int(update.message.text)
    except:
        return

    lang = game["lang"]
    if n < 3:
        await update.message.reply_text(TEXT[lang]["min"])
        return

    real, fake = random.choice(FAKE_PAIRS[lang])
    roles = ["real"] * (n - 1) + ["fake"]
    random.shuffle(roles)

    game.update({
        "players": n,
        "roles": roles,
        "real": real,
        "fake": fake,
        "current": 0,
        "messages": [],
        "state": "playing",
    })

    await update.message.reply_text(TEXT[lang]["ready"])
    await show_player(update.message, uid)

# ================= SHOW PLAYER =================
async def show_player(message, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show")]]
    msg = await message.reply_text(
        f"{TEXT[lang]['player']} {i + 1}",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    game["messages"].append(msg.message_id)

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    word = game["real"] if game["roles"][i] == "real" else game["fake"]

    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    msg = await q.message.reply_text(word, reply_markup=InlineKeyboardMarkup(kb))
    game["messages"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    for mid in game["messages"]:
        try:
            await context.bot.delete_message(q.message.chat_id, mid)
        except:
            pass
    game["messages"] = []

    game["current"] += 1

    if game["current"] >= game["players"]:
        kb = [[InlineKeyboardButton(TEXT[lang]["end_btn"], callback_data="end")]]
        await q.message.reply_text(TEXT[lang]["end_btn"], reply_markup=InlineKeyboardMarkup(kb))
        return

    await show_player(q.message, uid)

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games.pop(uid)

    lang = game["lang"]
    text = TEXT[lang]["summary"].format(real=game["real"], fake=game["fake"])
    kb = [[InlineKeyboardButton(TEXT[lang]["restart"], callback_data="restart")]]

    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

# ================= RESTART =================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
    app.add_handler(CallbackQueryHandler(show_word, pattern="show"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(end_game, pattern="end"))
    app.add_handler(CallbackQueryHandler(restart, pattern="restart"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))

    app.run_polling()

if __name__ == "__main__":
    main()

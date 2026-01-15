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

# ===================== DATA =====================

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


TEXT = {
    "fa": {
        "choose_lang": "🌍 زبان را انتخاب کنید",
        "players": "👥 تعداد بازیکن‌ها چند نفر است؟ (حداقل ۳)",
        "ready": "📱 همه آماده‌اید؟ گوشی دست نفر اول",
        "start": "🎮 شروع بازی",
        "show": "👁 دیدن نقش",
        "seen": "👁 دیدم",
        "player": "📱 بازیکن",
        "spy": "😈 تو جاسوسی\n❌ کلمه‌ای نداری",
        "end": "✅ همه نقش‌ها دیده شد",
        "end_btn": "🏁 پایان بازی",
        "restart": "🔁 شروع بازی جدید",
        "summary": "🏁 پایان بازی\n\n🔑 کلمه اصلی: {real}\n🎭 کلمه متفاوت: {fake}",
        "min": "😅 حداقل ۳ نفر لازمه!",
    },
    "en": {
        "choose_lang": "🌍 Choose language",
        "players": "👥 How many players? (min 3)",
        "ready": "📱 Everyone ready? Phone to Player 1",
        "start": "🎮 Start Game",
        "show": "👁 Show role",
        "seen": "👁 Seen",
        "player": "📱 Player",
        "spy": "😈 You are the SPY\n❌ No word",
        "end": "✅ All roles seen",
        "end_btn": "🏁 End Game",
        "restart": "🔁 New Game",
        "summary": "🏁 Game Over\n\n🔑 Real word: {real}\n🎭 Fake word: {fake}",
        "min": "😅 Minimum 3 players required!",
    },
    "tr": {
        "choose_lang": "🌍 Dil seçin",
        "players": "👥 Kaç oyuncu var? (en az 3)",
        "ready": "📱 Herkes hazır mı? Telefon 1. oyuncuda",
        "start": "🎮 Oyunu Başlat",
        "show": "👁 Rolü Gör",
        "seen": "👁 Gördüm",
        "player": "📱 Oyuncu",
        "spy": "😈 Sen CASUSSUN\n❌ Kelimen yok",
        "end": "✅ Herkes rolünü gördü",
        "end_btn": "🏁 Oyunu Bitir",
        "restart": "🔁 Yeni Oyun",
        "summary": "🏁 Oyun Bitti\n\n🔑 Asıl kelime: {real}\n🎭 Farklı kelime: {fake}",
        "min": "😅 En az 3 kişi lazım!",
    },
    "ru": {
        "choose_lang": "🌍 Выберите язык",
        "players": "👥 Сколько игроков? (минимум 3)",
        "ready": "📱 Все готовы? Телефон у игрока 1",
        "start": "🎮 Начать игру",
        "show": "👁 Показать роль",
        "seen": "👁 Видел",
        "player": "📱 Игрок",
        "spy": "😈 Ты ШПИОН\n❌ У тебя нет слова",
        "end": "✅ Все роли просмотрены",
        "end_btn": "🏁 Завершить игру",
        "restart": "🔁 Новая игра",
        "summary": "🏁 Игра окончена\n\n🔑 Основное слово: {real}\n🎭 Другое слово: {fake}",
        "min": "😅 Нужно минимум 3 игрока!",
    },
}

games = {}

# ===================== START =====================

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

    await update.message.reply_text(
        "🕵️ Spy Game\n\nChoose language 👇",
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ===================== LANGUAGE =====================

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    uid = q.from_user.id

    games[uid] = {
        "lang": lang,
        "state": "players",
        "messages": [],
    }

    await q.message.reply_text(TEXT[lang]["players"])

# ===================== PLAYERS =====================

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
    roles = ["spy", "fake"] + ["real"] * (n - 2)
    random.shuffle(roles)

    game.update({
        "players": n,
        "roles": roles,
        "real": real,
        "fake": fake,
        "current": 0,
        "state": "playing",
    })

    kb = [[InlineKeyboardButton(TEXT[lang]["start"], callback_data="start_game")]]
    await update.message.reply_text(TEXT[lang]["ready"], reply_markup=InlineKeyboardMarkup(kb))

# ===================== GAME FLOW =====================

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    await show_player(q.message, uid)

async def show_player(message, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show_role")]]
    await message.reply_text(
        f"{TEXT[lang]['player']} {i + 1}",
        reply_markup=InlineKeyboardMarkup(kb),
    )

async def show_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    role = game["roles"][i]
    if role == "spy":
        text = TEXT[lang]["spy"]
    elif role == "fake":
        text = f"🔑 {game['fake']}"
    else:
        text = f"🔑 {game['real']}"

    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    game["current"] += 1

    if game["current"] >= game["players"]:
        kb = [[InlineKeyboardButton(TEXT[lang]["end_btn"], callback_data="end_game")]]
        await q.message.reply_text(TEXT[lang]["end"], reply_markup=InlineKeyboardMarkup(kb))
    else:
        await show_player(q.message, uid)

# ===================== END =====================

async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games.pop(uid)
    lang = game["lang"]

    await q.message.reply_text(
        TEXT[lang]["summary"].format(real=game["real"], fake=game["fake"]),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(TEXT[lang]["restart"], callback_data="restart")]]
        ),
    )

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    games.pop(uid, None)
    await start(q, context)

# ===================== MAIN =====================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))
    app.add_handler(CallbackQueryHandler(start_game, pattern="start_game"))
    app.add_handler(CallbackQueryHandler(show_role, pattern="show_role"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(end_game, pattern="end_game"))
    app.add_handler(CallbackQueryHandler(restart, pattern="restart"))

    app.run_polling()

if __name__ == "__main__":
    main()

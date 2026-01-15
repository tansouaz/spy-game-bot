import os
import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

# ================== DATA ==================

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
        "show": "👁 دیدن کلمه",
        "seen": "👁 دیدم",
        "spy": "😈 تو جاسوسی\n❌ کلمه‌ای نداری",
        "player": "📱 بازیکن",
        "all_seen": "✅ همه بازیکن‌ها کلمه رو دیدن",
        "end": "🏁 پایان بازی",
        "restart": "🔁 شروع بازی جدید",
        "summary": "🏁 نتیجه بازی",
        "min_players": "😅 حداقل ۳ نفر لازمه!",
    },
    "en": {
        "choose_lang": "🌍 Choose language",
        "players": "👥 How many players? (min 3)",
        "ready": "📱 Everyone ready? Phone to Player 1",
        "start": "🎮 Start game",
        "show": "👁 Show word",
        "seen": "👁 Seen",
        "spy": "😈 You are the SPY\n❌ No word",
        "player": "📱 Player",
        "all_seen": "✅ All players saw the word",
        "end": "🏁 End game",
        "restart": "🔁 New game",
        "summary": "🏁 Game result",
        "min_players": "😅 At least 3 players needed!",
    },
    "tr": {
        "choose_lang": "🌍 Dil seçin",
        "players": "👥 Kaç oyuncu var? (en az 3)",
        "ready": "📱 Herkes hazır mı? Telefon 1. oyuncuda",
        "start": "🎮 Oyunu başlat",
        "show": "👁 Kelimeyi gör",
        "seen": "👁 Gördüm",
        "spy": "😈 Sen CASUSSUN\n❌ Kelimen yok",
        "player": "📱 Oyuncu",
        "all_seen": "✅ Herkes kelimeyi gördü",
        "end": "🏁 Oyunu bitir",
        "restart": "🔁 Yeni oyun",
        "summary": "🏁 Oyun sonucu",
        "min_players": "😅 En az 3 kişi lazım!",
    },
    "ru": {
        "choose_lang": "🌍 Выберите язык",
        "players": "👥 Сколько игроков? (минимум 3)",
        "ready": "📱 Все готовы? Телефон у игрока 1",
        "start": "🎮 Начать игру",
        "show": "👁 Показать слово",
        "seen": "👁 Видел",
        "spy": "😈 Ты ШПИОН\n❌ У тебя нет слова",
        "player": "📱 Игрок",
        "all_seen": "✅ Все увидели слово",
        "end": "🏁 Завершить игру",
        "restart": "🔁 Новая игра",
        "summary": "🏁 Результат игры",
        "min_players": "😅 Нужно минимум 3 игрока!",
    },
}

games = {}
GAME_MESSAGES = {}

# ================== HELPERS ==================

async def track(uid, msg):
    GAME_MESSAGES.setdefault(uid, []).append(msg.message_id)

async def clear_game_messages(context, chat_id, uid):
    for mid in GAME_MESSAGES.get(uid, []):
        try:
            await context.bot.delete_message(chat_id, mid)
        except:
            pass
    GAME_MESSAGES[uid] = []

# ================== START ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    await clear_game_messages(context, chat_id, uid)
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

    msg = await update.message.reply_text(
        "🕵️ Spy Game\n\nChoose language 👇",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    await track(uid, msg)

# ================== LANGUAGE ==================

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    lang = q.data.split("_")[1]

    games[uid] = {
        "lang": lang,
        "state": "players",
    }

    msg = await q.message.reply_text(TEXT[lang]["players"])
    await track(uid, msg)

# ================== PLAYERS ==================

async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    game = games.get(uid)
    if not game or game["state"] != "players":
        return

    try:
        players = int(update.message.text)
    except:
        return

    lang = game["lang"]
    if players < 3:
        await update.message.reply_text(TEXT[lang]["min_players"])
        return

    real, fake = random.choice(FAKE_PAIRS[lang])
    roles = ["spy"] + ["player"] * (players - 1)
    random.shuffle(roles)

    game.update({
        "players": players,
        "roles": roles,
        "real": real,
        "fake": fake,
        "current": 0,
        "state": "playing",
    })

    kb = [[InlineKeyboardButton(TEXT[lang]["start"], callback_data="start_game")]]
    msg = await update.message.reply_text(TEXT[lang]["ready"], reply_markup=InlineKeyboardMarkup(kb))
    await track(uid, msg)

# ================== GAME FLOW ==================

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    await show_player(q.message, context, uid)

async def show_player(message, context, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show_word")]]
    msg = await message.reply_text(
        f"{TEXT[lang]['player']} {i + 1}",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    await track(uid, msg)

async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]
    i = game["current"]

    text = (
        TEXT[lang]["spy"]
        if game["roles"][i] == "spy"
        else f"🔑 {game['real']}"
    )

    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]
    msg = await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    await track(uid, msg)

async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    game["current"] += 1

    if game["current"] >= game["players"]:
        lang = game["lang"]
        kb = [[InlineKeyboardButton(TEXT[lang]["end"], callback_data="end_game")]]
        msg = await q.message.reply_text(TEXT[lang]["all_seen"], reply_markup=InlineKeyboardMarkup(kb))
        await track(uid, msg)
    else:
        await show_player(q.message, context, uid)

# ================== END GAME ==================

async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    chat_id = q.message.chat_id
    game = games[uid]
    lang = game["lang"]

    await clear_game_messages(context, chat_id, uid)

    summary = (
        f"{TEXT[lang]['summary']}\n\n"
        f"🔑 کلمه اصلی: {game['real']}\n"
        f"🎭 کلمه متفاوت: {game['fake']}"
    )

    kb = [[InlineKeyboardButton(TEXT[lang]["restart"], callback_data="restart")]]
    msg = await q.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(kb))
    await track(uid, msg)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await start(q.message, context)

# ================== MAIN ==================

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

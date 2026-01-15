import os
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

# ================= FAKE PAIRS (30+) =================
FAKE_PAIRS = {
    "fa": [
        ("فرودگاه", "ایستگاه"), ("بیمارستان", "درمانگاه"),
        ("مدرسه", "دانشگاه"), ("دادگاه", "کلانتری"),
        ("بازار", "مغازه"), ("ساحل", "دریا"),
        ("جنگل", "پارک"), ("استخر", "باشگاه"),
        ("سینما", "تئاتر"), ("کتابخانه", "کتابفروشی"),
        ("هتل", "مهمانسرا"), ("بانک", "صرافی"),
        ("کافه", "رستوران"), ("موزه", "گالری"),
        ("قطار", "مترو"), ("اتوبوس", "تاکسی"),
        ("کارخانه", "کارگاه"), ("آشپزخانه", "رستوران"),
        ("پزشک", "پرستار"), ("داروخانه", "درمانگاه"),
        ("ورزشگاه", "باشگاه"), ("ساحل", "اسکله"),
        ("خیابان", "کوچه"), ("پل", "تونل"),
        ("پارکینگ", "گاراژ"), ("دفتر", "اداره"),
        ("کارمند", "مدیر"), ("کلاس", "جلسه"),
        ("پرواز", "فرود"),
    ],
    "en": [
        ("Airport", "Station"), ("Hospital", "Clinic"),
        ("School", "University"), ("Court", "Police Station"),
        ("Market", "Shop"), ("Beach", "Sea"),
        ("Forest", "Park"), ("Pool", "Gym"),
        ("Cinema", "Theater"), ("Library", "Bookstore"),
        ("Hotel", "Hostel"), ("Bank", "Exchange"),
        ("Cafe", "Restaurant"), ("Museum", "Gallery"),
        ("Train", "Metro"), ("Bus", "Taxi"),
        ("Factory", "Workshop"), ("Kitchen", "Restaurant"),
        ("Doctor", "Nurse"), ("Pharmacy", "Clinic"),
        ("Stadium", "Gym"), ("Street", "Alley"),
        ("Bridge", "Tunnel"), ("Office", "Department"),
        ("Employee", "Manager"), ("Class", "Meeting"),
        ("Flight", "Landing"),
    ],
    "tr": [
        ("Havalimanı", "İstasyon"), ("Hastane", "Klinik"),
        ("Okul", "Üniversite"), ("Mahkeme", "Karakol"),
        ("Pazar", "Mağaza"), ("Plaj", "Deniz"),
        ("Orman", "Park"), ("Havuz", "Spor Salonu"),
        ("Sinema", "Tiyatro"), ("Kütüphane", "Kitapçı"),
        ("Otel", "Pansiyon"), ("Banka", "Dövizci"),
        ("Kafe", "Restoran"), ("Müze", "Galeri"),
        ("Tren", "Metro"), ("Otobüs", "Taksi"),
        ("Fabrika", "Atölye"), ("Mutfak", "Restoran"),
        ("Doktor", "Hemşire"), ("Eczane", "Klinik"),
        ("Stadyum", "Salon"), ("Cadde", "Sokak"),
        ("Köprü", "Tünel"), ("Ofis", "Departman"),
        ("Çalışan", "Müdür"), ("Uçuş", "İniş"),
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
        ("Стадион", "Зал"), ("Улица", "Переулок"),
        ("Мост", "Тоннель"), ("Офис", "Отдел"),
        ("Работник", "Менеджер"), ("Рейс", "Посадка"),
    ],
}

TEXT = {
    "choose": {
        "fa": "🌍 زبان را انتخاب کنید",
        "en": "🌍 Choose language",
        "tr": "🌍 Dil seç",
        "ru": "🌍 Выберите язык",
    },
    "players": {
        "fa": "👥 تعداد بازیکن‌ها چند نفر است؟ (حداقل ۳)",
        "en": "👥 Number of players? (min 3)",
        "tr": "👥 Oyuncu sayısı kaç? (en az 3)",
        "ru": "👥 Сколько игроков? (минимум 3)",
    },
    "player": {
        "fa": "📱 بازیکن {n}",
        "en": "📱 Player {n}",
        "tr": "📱 Oyuncu {n}",
        "ru": "📱 Игрок {n}",
    },
    "end_players": {
        "fa": "🏁 پایان بازیکن‌ها",
        "en": "🏁 End of players",
        "tr": "🏁 Oyuncular bitti",
        "ru": "🏁 Игроки закончились",
    },
    "result": {
        "fa": "📌 نتیجه بازی\n\n🔑 کلمه اصلی: {real}\n🎭 کلمه متفاوت: {fake}",
        "en": "📌 Game result\n\n🔑 Real word: {real}\n🎭 Fake word: {fake}",
        "tr": "📌 Oyun sonucu\n\n🔑 Gerçek kelime: {real}\n🎭 Farklı kelime: {fake}",
        "ru": "📌 Результат игры\n\n🔑 Основное слово: {real}\n🎭 Другое слово: {fake}",
    }
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    games[chat_id] = {"state": "lang"}

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
    ]
    await update.message.reply_text(
        TEXT["choose"]["en"],
        reply_markup=InlineKeyboardMarkup(kb),
    )

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    lang = q.data.split("_")[1]

    games[chat_id] = {
        "lang": lang,
        "state": "players",
        "msgs": []
    }

    await q.message.delete()
    await context.bot.send_message(chat_id, TEXT["players"][lang])

# ================= PLAYER COUNT =================
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    game = games.get(chat_id)

    if not game or game["state"] != "players":
        return

    try:
        n = int(update.message.text)
    except:
        return

    if n < 3:
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

    await show_player(context, chat_id)

# ================= SHOW PLAYER =================
async def show_player(context, chat_id):
    game = games[chat_id]
    i = game["i"]
    lang = game["lang"]

    kb = [[InlineKeyboardButton("👁", callback_data="show")]]
    msg = await context.bot.send_message(
        chat_id,
        TEXT["player"][lang].format(n=i + 1),
        reply_markup=InlineKeyboardMarkup(kb),
    )
    game["msgs"].append(msg.message_id)

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games[chat_id]

    word = game["words"][game["i"]]
    kb = [[InlineKeyboardButton("✅", callback_data="seen")]]

    msg = await context.bot.send_message(
        chat_id,
        f"🔑 {word}",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    game["msgs"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games[chat_id]

    for mid in game["msgs"]:
        try:
            await context.bot.delete_message(chat_id, mid)
        except:
            pass
    game["msgs"].clear()

    game["i"] += 1

    if game["i"] >= len(game["words"]):
        kb = [[InlineKeyboardButton("🏁", callback_data="end")]]
        await context.bot.send_message(
            chat_id,
            TEXT["end_players"][game["lang"]],
            reply_markup=InlineKeyboardMarkup(kb),
        )
        return

    await show_player(context, chat_id)

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games.pop(chat_id)

    text = TEXT["result"][game["lang"]].format(
        real=game["real"], fake=game["fake"]
    )
    kb = [[InlineKeyboardButton("🔁", callback_data="restart")]]

    await context.bot.send_message(chat_id, text, reply_markup=InlineKeyboardMarkup(kb))

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))

    app.run_polling()

if __name__ == "__main__":
    main()

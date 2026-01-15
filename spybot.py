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
        ("ورزشگاه", "باشگاه"), ("خیابان", "کوچه"),
        ("پل", "تونل"), ("دفتر", "اداره"),
        ("کارمند", "مدیر"), ("پارکینگ", "گاراژ"),
    ],
    "en": [
        ("Airport", "Station"), ("Hospital", "Clinic"),
        ("School", "University"), ("Court", "Police"),
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
        ("Employee", "Manager"),
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
        ("Çalışan", "Müdür"),
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
        ("Работник", "Менеджер"),
    ],
}

games = {}

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    games[uid] = {"state": "lang"}

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    await update.message.reply_text(
        "🌍 Choose language",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ---------- LANGUAGE ----------
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    lang = q.data.split("_")[1]

    games[uid] = {
        "lang": lang,
        "state": "players",
        "msgs": []
    }

    await q.message.delete()
    texts = {
        "fa": "👥 تعداد بازیکن‌ها؟ (حداقل ۳)",
        "en": "👥 Number of players? (min 3)",
        "tr": "👥 Oyuncu sayısı? (min 3)",
        "ru": "👥 Количество игроков? (мин 3)",
    }
    await q.message.chat.send_message(texts[lang])

# ---------- PLAYER COUNT ----------
async def set_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    game = games.get(uid)
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
        "state": "play"
    })

    await show_player(update.message, uid)

# ---------- SHOW PLAYER ----------
async def show_player(msg, uid):
    game = games[uid]
    i = game["i"]

    kb = [[InlineKeyboardButton("👁 دیدن نقش", callback_data="show")]]
    m = await msg.reply_text(
        f"📱 بازیکن {i+1}",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    game["msgs"].append(m.message_id)

# ---------- SHOW WORD ----------
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    word = game["words"][game["i"]]
    kb = [[InlineKeyboardButton("👁 دیدم", callback_data="seen")]]
    m = await q.message.reply_text(f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))
    game["msgs"].append(m.message_id)

# ---------- SEEN ----------
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]

    for mid in game["msgs"]:
        try:
            await context.bot.delete_message(q.message.chat_id, mid)
        except:
            pass
    game["msgs"].clear()

    game["i"] += 1

    if game["i"] >= len(game["words"]):
        kb = [[InlineKeyboardButton("🏁 پایان بازی", callback_data="end")]]
        await q.message.reply_text("🏁 پایان بازیکن‌ها", reply_markup=InlineKeyboardMarkup(kb))
        return

    await show_player(q.message, uid)

# ---------- END GAME ----------
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games.pop(uid)

    text = (
        "📌 نتیجه بازی:\n\n"
        f"🔑 کلمه اصلی: {game['real']}\n"
        f"🎭 کلمه متفاوت: {game['fake']}"
    )
    kb = [[InlineKeyboardButton("🔁 New game", callback_data="restart")]]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

# ---------- RESTART ----------
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await start(Update(update_id=0, message=q.message), context)

# ---------- MAIN ----------
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

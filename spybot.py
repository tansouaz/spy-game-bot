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

# ================= FAKE PAIRS (MIN 30 EACH) =================
FAKE_PAIRS = {
    "fa": [
        ("فرودگاه","ایستگاه"),("بیمارستان","درمانگاه"),("مدرسه","دانشگاه"),
        ("دادگاه","کلانتری"),("بازار","مغازه"),("ساحل","دریا"),
        ("جنگل","پارک"),("استخر","باشگاه"),("سینما","تئاتر"),
        ("کتابخانه","کتابفروشی"),("هتل","مهمانسرا"),("بانک","صرافی"),
        ("کافه","رستوران"),("موزه","گالری"),("پلیس","نگهبان"),
        ("قطار","مترو"),("اتوبوس","تاکسی"),("کارخانه","کارگاه"),
        ("فرود","پرواز"),("کلاس","جلسه"),("پزشک","پرستار"),
        ("داروخانه","درمانگاه"),("ورزشگاه","باشگاه"),("خیابان","کوچه"),
        ("پل","تونل"),("پارکینگ","گاراژ"),("دفتر","اداره"),
        ("کارمند","مدیر"),("ساحل","اسکله")
    ],
    "en": [
        ("Airport","Station"),("Hospital","Clinic"),("School","University"),
        ("Court","Police Station"),("Market","Shop"),("Beach","Sea"),
        ("Forest","Park"),("Pool","Gym"),("Cinema","Theater"),
        ("Library","Bookstore"),("Hotel","Hostel"),("Bank","Exchange"),
        ("Cafe","Restaurant"),("Museum","Gallery"),("Police","Guard"),
        ("Train","Metro"),("Bus","Taxi"),("Factory","Workshop"),
        ("Landing","Flight"),("Class","Meeting"),("Doctor","Nurse"),
        ("Pharmacy","Clinic"),("Stadium","Gym"),("Street","Alley"),
        ("Bridge","Tunnel"),("Parking","Garage"),("Office","Department"),
        ("Employee","Manager")
    ],
    "tr": [
        ("Havalimanı","İstasyon"),("Hastane","Klinik"),("Okul","Üniversite"),
        ("Mahkeme","Karakol"),("Pazar","Mağaza"),("Plaj","Deniz"),
        ("Orman","Park"),("Havuz","Spor Salonu"),("Sinema","Tiyatro"),
        ("Kütüphane","Kitapçı"),("Otel","Pansiyon"),("Banka","Dövizci"),
        ("Kafe","Restoran"),("Müze","Galeri"),("Polis","Güvenlik"),
        ("Tren","Metro"),("Otobüs","Taksi"),("Fabrika","Atölye"),
        ("İniş","Uçuş"),("Sınıf","Toplantı"),("Doktor","Hemşire"),
        ("Eczane","Klinik"),("Stadyum","Salon"),("Cadde","Sokak"),
        ("Köprü","Tünel"),("Otopark","Garaj"),("Ofis","Departman"),
        ("Çalışan","Müdür")
    ],
    "ru": [
        ("Аэропорт","Станция"),("Больница","Клиника"),("Школа","Университет"),
        ("Суд","Полиция"),("Рынок","Магазин"),("Пляж","Море"),
        ("Лес","Парк"),("Бассейн","Спортзал"),("Кино","Театр"),
        ("Библиотека","Книжный"),("Отель","Хостел"),("Банк","Обмен"),
        ("Кафе","Ресторан"),("Музей","Галерея"),("Полиция","Охрана"),
        ("Поезд","Метро"),("Автобус","Такси"),("Фабрика","Мастерская"),
        ("Посадка","Рейс"),("Класс","Встреча"),("Врач","Медсестра"),
        ("Аптека","Клиника"),("Стадион","Зал"),("Улица","Переулок"),
        ("Мост","Тоннель"),("Парковка","Гараж"),("Офис","Отдел"),
        ("Работник","Менеджер")
    ]
}

TEXT = {
    "choose": "🌍 Choose language",
    "players": {
        "fa":"👥 تعداد بازیکن‌ها؟ (حداقل ۳)",
        "en":"👥 Number of players? (min 3)",
        "tr":"👥 Oyuncu sayısı? (min 3)",
        "ru":"👥 Кол-во игроков? (мин 3)"
    },
    "player": {
        "fa":"📱 بازیکن {}",
        "en":"📱 Player {}",
        "tr":"📱 Oyuncu {}",
        "ru":"📱 Игрок {}"
    },
    "end_players":{
        "fa":"🏁 همه بازیکن‌ها دیدند",
        "en":"🏁 All players finished",
        "tr":"🏁 Tüm oyuncular gördü",
        "ru":"🏁 Все посмотрели"
    },
    "result":{
        "fa":"📌 نتیجه بازی\n\n🔑 کلمه اصلی: {}\n🎭 کلمه متفاوت: {}",
        "en":"📌 Result\n\n🔑 Real: {}\n🎭 Fake: {}",
        "tr":"📌 Sonuç\n\n🔑 Gerçek: {}\n🎭 Sahte: {}",
        "ru":"📌 Результат\n\n🔑 Основное: {}\n🎭 Фейк: {}"
    }
}

games = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    games.pop(chat_id, None)

    kb = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    await update.message.reply_text(TEXT["choose"], reply_markup=InlineKeyboardMarkup(kb))

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    chat_id = q.message.chat_id
    lang = q.data.split("_")[1]

    games[chat_id] = {
        "lang": lang,
        "state": "players",
        "i": 0,
        "last_msgs": []
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
    words = [pair[0]]*(n-1) + [pair[1]]
    random.shuffle(words)

    game.update({
        "words": words,
        "real": pair[0],
        "fake": pair[1],
        "state": "playing"
    })

    await show_player(context, chat_id)

# ================= SHOW PLAYER =================
async def show_player(context, chat_id):
    game = games[chat_id]
    lang = game["lang"]

    kb = [[InlineKeyboardButton("👁", callback_data="show")]]
    msg = await context.bot.send_message(
        chat_id,
        TEXT["player"][lang].format(game["i"]+1),
        reply_markup=InlineKeyboardMarkup(kb)
    )
    game["last_msgs"] = [msg.message_id]

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games[chat_id]

    word = game["words"][game["i"]]
    kb = [[InlineKeyboardButton("✅", callback_data="seen")]]
    msg = await context.bot.send_message(chat_id, f"🔑 {word}", reply_markup=InlineKeyboardMarkup(kb))
    game["last_msgs"].append(msg.message_id)

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games[chat_id]

    for mid in game["last_msgs"]:
        try:
            await context.bot.delete_message(chat_id, mid)
        except:
            pass

    game["last_msgs"] = []
    game["i"] += 1

    if game["i"] < len(game["words"]):
        await show_player(context, chat_id)
    else:
        kb = [[InlineKeyboardButton("🏁", callback_data="end")]]
        await context.bot.send_message(
            chat_id,
            TEXT["end_players"][game["lang"]],
            reply_markup=InlineKeyboardMarkup(kb)
        )

# ================= END GAME =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat_id
    game = games.pop(chat_id)

    text = TEXT["result"][game["lang"]].format(game["real"], game["fake"])
    kb = [[InlineKeyboardButton("🔁 New game", callback_data="restart")]]
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

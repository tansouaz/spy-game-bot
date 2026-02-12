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

# =========================
# FAKE PAIRS (40+)
# =========================
FAKE_PAIRS = {
    "fa": [
       ("فرودگاه","ترمینال"),
    ("بیمارستان","اورژانس"),
    ("مدرسه","دبیرستان"),
    ("دادگاه","زندان"),
    ("بازار","پاساژ"),
    ("ساحل","اسکله"),
    ("جنگل","کویر"),
    ("استخر","دریاچه"),
    ("سینما","آمفی‌تئاتر"),
    ("کتابخانه","آرشیو"),
    ("هتل","هاستل"),
    ("بانک","خودپرداز"),
    ("کافه","کافی‌شاپ"),
    ("موزه","نمایشگاه"),
    ("قطار","تراموا"),
    ("اتوبوس","مینی‌بوس"),
    ("کارخانه","کارگاه"),
    ("آشپزخانه","آشپزخانه صنعتی"),
    ("پزشک","جراح"),
    ("داروخانه","آزمایشگاه"),
    ("ورزشگاه","استادیوم"),
    ("پل","روگذر"),
    ("خیابان","بلوار"),
    ("پارکینگ","پارکینگ طبقاتی"),
    ("دفتر","شرکت"),
    ("کارمند","کارآموز"),
    ("بازارچه","مال"),
    ("سینما","سریال"),
    ("کتاب","مجله"),
    ("خانه","ویلا"),
    ("مسجد","کلیسا"),
    ("مدرس","سخنران"),
    ("دانش‌آموز","هنرجو"),
    ("سالن","سالن همایش"),
    ("اتاق","سوئیت"),
    ("پادگان","قرارگاه"),
    ("بندر","اسکله"),
    ("کارگاه","کارخانه"),
    ("اینستاگرام","تیک‌تاک"),
    ("گوشی","موبایل"),
    ("لپ‌تاپ","نوت‌بوک"),
    ("نتفلیکس","فیلیمو"),
    ("پیتزا","ساندویچ"),
    ("دیجی","پرودوسر"),
    ("کنسرت","شو"),
    ("برنامه‌نویس","توسعه‌دهنده"),
    ("کریپتو","فارکس"),
    ("بیت‌کوین","دوج‌کوین"),
    ("هوش مصنوعی","یادگیری ماشین"),
    ("گیم","استریم"),
    ("پابجی","کال‌آف‌دیوتی"),
    ("مارول","دی‌سی"),
    ("زومبی","هیولا"),
    ("انیمه","مانگا"),
    ("میم","ترول"),
    ("استریمر","یوتیوبر"),
    ("باشگاه","فیتنس"),
    ("ماشین","خودرو"),
    ("اوبر","اسنپ"),
    ("جزیره","شبه‌جزیره"),
    ("کمپ","اردو"),
    ("مهمانی","جشن"),
    ("فالوور","دنبال‌کننده"),
    ("ایموجی","استیکر"),
    ("فیلتر","پریست"),
    ("پارتی","کلاب"),
    ("کافه","لانژ"),
    ("دانشجو","فارغ‌التحصیل"),
    ("استاد","پروفسور"),
    ("پلی‌استیشن","ایکس‌باکس"),
    ("دیسکو","بار"),
    ("عکس","ویدیو"),
    ("فیلم","مستند"),
    ("پول","سکه"),
    ("سفر","گردش"),
    ("خانه","آپارتمان"),
    ("مدیر","سرپرست"),


    ],
    "en": [
        ("Airport","Station"),("Hospital","Clinic"),("School","University"),
        ("Court","Police"),("Market","Shop"),("Beach","Sea"),
        ("Forest","Park"),("Pool","Gym"),("Cinema","Theater"),
        ("Library","Bookstore"),("Hotel","Hostel"),("Bank","Exchange"),
        ("Cafe","Restaurant"),("Museum","Gallery"),("Train","Metro"),
        ("Bus","Taxi"),("Factory","Workshop"),("Kitchen","Restaurant"),
        ("Doctor","Nurse"),("Pharmacy","Clinic"),("Stadium","Gym"),
        ("Bridge","Tunnel"),("Street","Alley"),("Parking","Garage"),
        ("Office","Department"),("Employee","Manager"),("House","Apartment"),
        ("Mosque","Shrine"),("Student","Teacher"),("Class","Room"),
        ("Room","Hall"),("Base","Camp"),("Port","Dock"),
        ("Library","Archive"),("Cinema","Screen"),("Instagram","TikTok"),
        ("iPhone","Samsung"),("Laptop","Tablet"),("Netflix","YouTube"),
        ("Pizza","Burger"),("Snapchat","Telegram"),("Discord","Skype"),
        ("PlayStation","Xbox"),("PUBG","Fortnite"),("Coffee","Energy drink"),
        ("Selfie","Photo"),("Influencer","Blogger"),("DJ","Producer"),
        ("Rap","HipHop"),("Concert","Festival"),("Hacker","Programmer"),
        ("Crypto","Stock"),("Bitcoin","Ethereum"),("AI","Robot"),("Drone","Helicopter"),
        ("Zombie","Vampire"),("Marvel","DC"),("Spider-Man","Batman"),("Anime","Cartoon"),
        ("Meme","Joke"),("Stream","Video"),("Club","Party"),("Camping","Hiking"),
        ("Beach","Island"),("DJ","Singer"),("Gamer","Streamer"),("Online","Offline"),
        ("Follower","Subscriber"),("Emoji","Sticker"),("Filter","Effect"),("Gym","Workout"),
        ("Car","Motorcycle"),("Uber","Taxi"),("Mall","Supermarket"),

    ],
    "tr": [
        ("Havalimanı","İstasyon"),("Hastane","Klinik"),("Okul","Üniversite"),
        ("Mahkeme","Karakol"),("Pazar","Mağaza"),("Plaj","Deniz"),
        ("Orman","Park"),("Havuz","Spor Salonu"),("Sinema","Tiyatro"),
        ("Kütüphane","Kitapçı"),("Otel","Pansiyon"),("Banka","Dövizci"),
        ("Kafe","Restoran"),("Müze","Galeri"),("Tren","Metro"),
        ("Otobüs","Taksi"),("Fabrika","Atölye"),("Mutfak","Restoran"),
        ("Doktor","Hemşire"),("Eczane","Klinik"),("Stadyum","Salon"),
        ("Köprü","Tünel"),("Cadde","Sokak"),("Otopark","Garaj"),
        ("Ofis","Departman"),("Çalışan","Müdür"),("Ev","Apartman"),
        ("Öğrenci","Öğretmen"),("Sınıf","Oda"),("Oda","Salon"),
        ("Liman","İskele"),("Sinema","Perde"),
        ("Instagram","TikTok"),("Telefon","Tablet"),("Laptop","Bilgisayar"),(
            "Netflix","YouTube"),("Pizza","Burger"),("DJ","Şarkıcı"),("Konser","Festival"),
        ("Programcı","Hacker"),("Kripto","Borsa"),("Bitcoin","Ethereum"),("Yapay Zeka","Robot"),
        ("Oyun","Game"),("PUBG","Fortnite"),("Marvel","DC"),("Zombi","Vampir"),("Anime","Çizgi Film"),
        ("Mizah","Şaka"),("Yayıncı","Gamer"),("Spor Salonu","Fitness"),("Araba","Motor"),("Uber","Taksi"),
        ("Ada","Plaj"),("Kamp","Dağcılık"),("Parti","Kulüp"),("Takipçi","Abone"),("Emoji","Sticker"),
        ("Filtre","Efekt"),("Fotoğraf","Selfie"),("Film","Dizi"),("Para","Dolar"),("Seyahat","Tatil"),
        ("Ev","Villa"),("Müdür","Patron"),

    ],
    "ru": [
        ("Аэропорт","Станция"),("Больница","Клиника"),("Школа","Университет"),
        ("Суд","Полиция"),("Рынок","Магазин"),("Пляж","Море"),
        ("Лес","Парк"),("Бассейн","Спортзал"),("Кино","Театр"),
        ("Библиотека","Книжный"),("Отель","Хостел"),("Банк","Обмен"),
        ("Кафе","Ресторан"),("Музей","Галерея"),("Поезд","Метро"),
        ("Автобус","Такси"),("Фабрика","Мастерская"),("Кухня","Ресторан"),
        ("Врач","Медсестра"),("Аптека","Клиника"),("Стадион","Зал"),
        ("Мост","Тоннель"),("Улица","Переулок"),("Парковка","Гараж"),
        ("Офис","Отдел"),("Работник","Менеджер"),("Дом","Квартира"),
        ("Студент","Преподаватель"),("Комната","Зал"),
        ("Порт","Причал"),("Кино","Экран"),
        ("Instagram","TikTok"),("Телефон","Планшет"),("Ноутбук","Компьютер"),
        ("Netflix","YouTube"),("Пицца","Бургер"),("DJ","Певец"),("Концерт","Фестиваль"),(
            "Программист","Хакер"),("Крипто","Биржа"),("Биткоин","Эфириум"),("ИИ","Робот"),
        ("Игра","Гейм"),("PUBG","Fortnite"),("Marvel","DC"),("Зомби","Вампир"),("Аниме","Мультфильм"),
        ("Мем","Шутка"),("Стример","Геймер"),("Фитнес","Спортзал"),("Машина","Мотоцикл"),
        ("Uber","Такси"),("Остров","Пляж"),("Кемпинг","Поход"),("Вечеринка","Клуб"),("Подписчик","Фолловер"),
        ("Эмодзи","Стикер"),("Фильтр","Эффект"),("Фото","Селфи"),("Фильм","Сериал"),("Деньги","Доллар"),
        ("Путешествие","Отпуск"),("Дом","Вилла"),("Директор","Босс"),
    ],
}

TEXT = {
    "fa": {
        "choose":"🌍 انتخاب زبان",
        "players":"👥 تعداد بازیکن‌ها؟ (حداقل 3)",
        "player":"📱 بازیکن",
        "show":"👁 دیدن کلمه",
        "seen":"👁 دیدم",
        "checked":"🏁 همه بازیکن‌ها دیدند",
        "end":"🏁 پایان بازی",
        "result":"📌 نتیجه بازی",
        "real":"🔑 کلمه اصلی:",
        "fake":"🎭 کلمه متفاوت:",
        "new":"🔁 شروع بازی جدید",
    },
    "en": {
        "choose":"🌍 Choose language",
        "players":"👥 Number of players? (min 3)",
        "player":"📱 Player",
        "show":"👁 Show word",
        "seen":"👁 Seen",
        "checked":"🏁 All players checked",
        "end":"🏁 End game",
        "result":"📌 Game result",
        "real":"🔑 Real word:",
        "fake":"🎭 Fake word:",
        "new":"🔁 New game",
    },
    "tr": {
        "choose":"🌍 Dil seç",
        "players":"👥 Kaç oyuncu? (min 3)",
        "player":"📱 Oyuncu",
        "show":"👁 Kelimeyi gör",
        "seen":"👁 Gördüm",
        "checked":"🏁 Herkes baktı",
        "end":"🏁 Oyunu bitir",
        "result":"📌 Oyun sonucu",
        "real":"🔑 Asıl kelime:",
        "fake":"🎭 Farklı kelime:",
        "new":"🔁 Yeni oyun",
    },
    "ru": {
        "choose":"🌍 Выберите язык",
        "players":"👥 Сколько игроков? (мин 3)",
        "player":"📱 Игрок",
        "show":"👁 Показать слово",
        "seen":"👁 Видел",
        "checked":"🏁 Все посмотрели",
        "end":"🏁 Конец игры",
        "result":"📌 Результат",
        "real":"🔑 Основное слово:",
        "fake":"🎭 Другое слово:",
        "new":"🔁 Новая игра",
    },
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
    await update.effective_message.reply_text(
        TEXT["en"]["choose"],
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]

    games[q.from_user.id] = {
        "lang": lang,
        "state": "players",
    }
    await q.message.delete()
    await q.message.reply_text(TEXT[lang]["players"])

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
        await update.message.reply_text(TEXT[game["lang"]]["players"])
        return

    real, fake = random.choice(FAKE_PAIRS[game["lang"]])
    if n>4 :
     fake_count = random.randint(1, n // 2)
    else :
     fake_count = 1
     

    words = [real]*(n-fake_count) + [fake]*fake_count
    random.shuffle(words)

    game.update({
        "words": words,
        "real": real,
        "fake": fake,
        "i": 0,
        "state": "play",
    })

    await show_player(update.effective_message, uid)

# ================= SHOW PLAYER =================
async def show_player(msg, uid):
    game = games[uid]
    lang = game["lang"]
    i = game["i"]

    kb = [[InlineKeyboardButton(TEXT[lang]["show"], callback_data="show")]]
    await msg.reply_text(
        f"{TEXT[lang]['player']} {i+1}",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= SHOW WORD =================
async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    await q.message.delete()

    word = game["words"][game["i"]]

    # ✅ تشخیص نقش
    if word == game["real"]:
        role_label = TEXT[lang]["real"]
    else:
        role_label = TEXT[lang]["fake"]

    kb = [[InlineKeyboardButton(TEXT[lang]["seen"], callback_data="seen")]]

    await q.message.reply_text(
        f"{role_label} {word}",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= SEEN =================
async def seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games[uid]
    lang = game["lang"]

    await q.message.delete()
    game["i"] += 1

    if game["i"] >= len(game["words"]):
        kb = [[InlineKeyboardButton(TEXT[lang]["end"], callback_data="end")]]
        await q.message.reply_text(TEXT[lang]["checked"], reply_markup=InlineKeyboardMarkup(kb))
    else:
        await show_player(q.message, uid)

# ================= END =================
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    game = games.pop(uid)
    lang = game["lang"]

    text = (
        f"{TEXT[lang]['result']}\n\n"
        f"{TEXT[lang]['real']} {game['real']}\n"
        f"{TEXT[lang]['fake']} {game['fake']}"
    )

    kb = [[InlineKeyboardButton(TEXT[lang]["new"], callback_data="restart")]]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

# ================= RESTART =================
# ================= RESTART (FIXED) =================
# ================= RESTART (FINAL FIX) =================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    # پاک‌سازی کامل state
    games[uid] = {
        "lang": games.get(uid, {}).get("lang", "fa"),
        "state": "players",
        "msgs": [],
    }

    lang = games[uid]["lang"]

    # فقط پرسش تعداد بازیکن – بدون تغییر ظاهر
    await q.message.reply_text(TEXT[lang]["players"])


# ================= HOW TO PLAY =================
async def how_to_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎮 How to Play:\n\n"
        "1️⃣ Pick a language\n"
        "2️⃣ Choose number of players\n"
        "3️⃣ Player taps 'Show Word'\n"
        "4️⃣ See the word\n"
        "5️⃣ Tap 'Seen'\n"
        "6️⃣ Pass the phone to the next player\n"
        "7️⃣ After everyone sees, find the spy!"
    )
    await update.message.reply_text(text)
    
    # ================= WHAT IS GAME =================
async def whats_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🕵️ Spy Game\n\n"
        "A fun party game for friends!\n"
        "Everyone gets a word… but one or more players get a different one 🤫\n"
        "Talk, guess, and find the spy before they fool you! 👀🔥"
    )
    await update.message.reply_text(text)

    
# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_players))
    app.add_handler(CallbackQueryHandler(show_word, pattern="show"))
    app.add_handler(CallbackQueryHandler(seen, pattern="seen"))
    app.add_handler(CallbackQueryHandler(end_game, pattern="end"))
    app.add_handler(CallbackQueryHandler(restart, pattern="restart"))
    app.add_handler(CommandHandler("whatsgame", whats_game))
    app.add_handler(CommandHandler("howtoplay", how_to_play))

    app.run_polling()

if __name__ == "__main__":
    main()

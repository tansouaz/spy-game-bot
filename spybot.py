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

    # 🍕 غذا (۳۰ جفت)
    ("پیتزا","برگر"),("چلوکباب","جوجه‌کباب"),("قره‌سبزی","قیمه"),("کوکو","کتلت"),("آبگوشت","حلیم"),("ساندویچ","فلافل"),("پفک","چیپس"),("بستنی","ژله"),("نوشابه","دلستر"),("قهوه","چای"),("دوغ","آبمیوه"),("شکلات","بیسکویت"),("کیک","دسر"),("سیب‌زمینی سرخ‌کرده","پاپ‌کورن"),("لازانیا","ماکارونی"),("همبرگر","هات‌داگ"),("آش","سوپ"),("کباب","خوراک"),("املت","نیمرو"),("عدسی","لوبیا"),("کله‌پاچه","سیرابی"),("سمبوسه","پیراشکی"),("سالاد","ماست"),("خورشت","خوراک مرغ"),("شیر","شیرکاکائو"),("چلو","پلو"),("زرشک‌پلو","باقالی‌پلو"),("کشک بادمجان","میرزاقاسمی"),("سوسیس","کالباس"),("چیزکیک","کاپ‌کیک"),

    # 🎉 مهمونی و پارتی (۳۰ جفت)
    ("مهمانی","دورهمی"),("پارتی","جشن"),("عروسی","نامزدی"),("تولد","سالگرد"),("کلاب","کافه"),("آهنگ","پلی‌لیست"),("دیجی","خواننده"),("رقص","دست‌زدن"),("هدیه","کادو"),("عکس","استوری"),("لباس مجلسی","کت‌وشلوار"),("کفش رسمی","کتونی"),("آرایش","عطر"),("میکاپ","مدل مو"),("شمع","بادکنک"),("کیک تولد","دسر"),("خنده","شوخی"),("بازی گروهی","چالش"),("فیلم گرفتن","عکس گرفتن"),("دعوت","خبر دادن"),("شب‌نشینی","پیک‌نیک"),("گپ","حرف زدن"),("سلفی","عکس دسته‌جمعی"),("فشفشه","نورپردازی"),("رقص دو نفره","رقص گروهی"),("سورپرایز","غافلگیری"),("پخش زنده","فیلم گرفتن"),("موزیک بلند","موزیک ملایم"),("چیدمان","دکور"),("میز شام","میز مزه"),

    # 😂 کل‌کل و خنده‌دار (۳۰ جفت)
    ("شوهر","داماد"),("نامزد","خواستگار"),("دوست","رفیق"),("داداش","پسرخاله"),("مادرشوهر","عمه"),("غر زدن","حرف زدن"),("ناز","لوس‌بازی"),("رئیس","مدیر"),("همکار","شریک"),("همسایه","صاحبخانه"),("آنلاین","در دسترس"),("چت","تماس"),("خواب","استراحت"),("پشه","مگس"),("لاکچری","مجلسی"),("پز دادن","ژست گرفتن"),("عصبانی","اخمو"),("آروم","ساکت"),("شیطون","بازیگوش"),("باهوش","زرنگ"),("حسود","کنجکاو"),("خسیس","حسابگر"),("پررو","راحت"),("بدقول","دیررس"),("خوشتیپ","مرتب"),("اهل حال","اهل کار"),("خوش‌اخلاق","مودب"),("بامزه","شوخ"),("کم‌حرف","ساکت"),("پر انرژی","فعال"),

    # 🚗 زندگی روزمره (۳۰ جفت)
    ("ماشین","شاسی‌بلند"),("موتور","دوچرخه"),("اوبر","اسنپ"),("پول نقد","کارت"),("خرید","سفارش"),("سفر","مسافرت"),("کمپ","پیک‌نیک"),("خانه","ویلا"),("آپارتمان","سوئیت"),("مغازه","سوپرمارکت"),("پارک","شهربازی"),("استخر","دریاچه"),("سینما","کنسرت"),("تلویزیون","لپتاپ"),("گوشی","تبلت"),("شارژر","پاوربانک"),("لباس","کفش"),("ساعت","عینک"),("طلا","نقره"),("عروسی","تولد"),("صبحانه","ناهار"),("شام","میان‌وعده"),("باشگاه","استخر"),("کتاب","مجله"),("فیلم","سریال"),("فوتبال","والیبال"),("چای عصرانه","قهوه عصر"),("کار","شغل"),("مدیر","کارمند"),("دانشجو","دانش‌آموز"),

    ],
    "en": [
    # 🍕 FOOD (30 pairs)
    ("Pizza","Burger"),("Steak","BBQ"),("Tacos","Burrito"),("Pasta","Lasagna"),("Fries","Onion rings"),("Hotdog","Sandwich"),("Sushi","Ramen"),("Donut","Cupcake"),("Cake","Brownie"),("Ice cream","Milkshake"),("Coffee","Iced coffee"),("Tea","Latte"),("Energy drink","Soda"),("Beer","Cocktail"),("Wine","Champagne"),("Chips","Nachos"),("Popcorn","Pretzels"),("Pancakes","Waffles"),("Bacon","Sausage"),("Omelet","Scrambled eggs"),("Salad","Coleslaw"),("Cheesecake","Apple pie"),("Chocolate","Candy"),("Peanut butter","Nutella"),("Mac & cheese","Grilled cheese"),("Fried chicken","Chicken wings"),("BBQ sauce","Ketchup"),("Smoothie","Juice"),("Milk","Chocolate milk"),("Brunch","Dinner"),

    # 🎉 PARTY MODE (30 pairs)
    ("Party","Get-together"),("Birthday","Anniversary"),("Wedding","Engagement"),("Club","Bar"),("DJ","Singer"),("Playlist","Mixtape"),("Selfie","Group photo"),("Dress up","Casual wear"),("High heels","Sneakers"),("Makeup","Perfume"),("Gift","Surprise"),("Dance","Vibes"),("Loud music","Chill music"),("Afterparty","Pre-game"),("Game night","Movie night"),("BBQ night","House party"),("Pool party","Beach party"),("Girls night","Boys night"),("Shots","Beer pong"),("Red carpet","VIP"),("Snap","Story"),("Live","Reel"),("Glow up","Makeover"),("Decor","Lights"),("Cake cutting","Toast speech"),("Late night","All-nighter"),("Dress code","Theme"),("Dance floor","VIP section"),("Hangout","Meet-up"),("Sleepover","Road trip"),

    # 😂 FUN & FRIEND DRAMA (30 pairs)
    ("Boyfriend","Crush"),("Girlfriend","Date"),("Best friend","Close friend"),("Roommate","Neighbor"),("Boss","Manager"),("Tease","Roast"),("Flirt","Compliment"),("Ghosting","Ignoring"),("Drama","Chaos"),("Lazy","Chill"),("Moody","Quiet"),("Savage","Sassy"),("Boujee","Fancy"),("Messy","Clumsy"),("Late","Fashionably late"),("Gym bro","Fitness freak"),("Party animal","Night owl"),("Hopeless romantic","Player"),("Ex","Situationship"),("Texting","Calling"),("Blocked","Muted"),("Screenshot","Forwarded"),("Jealous","Curious"),("Secret","Surprise"),("Flexing","Showing off"),("Glow up","Level up"),("Overthinking","Daydreaming"),("Loud","Extra"),("Low-key","Private"),("Hangry","Grumpy"),

    # 🚗 DAILY LIFE (30 pairs)
    ("Car","SUV"),("Bike","Scooter"),("Uber","Lyft"),("Cash","Credit card"),("Shopping","Ordering"),("Vacation","Trip"),("Camping","Picnic"),("Apartment","House"),("Mall","Supermarket"),("Park","Amusement park"),("Pool","Beach"),("Cinema","Concert"),("TV","Laptop"),("Phone","Tablet"),("Charger","Power bank"),("Watch","Sunglasses"),("Gold","Silver"),("Breakfast","Brunch"),("Lunch","Dinner"),("Workout","Training"),("Book","Magazine"),("Movie","Series"),("Soccer","Basketball"),("Tea time","Coffee break"),("Job","Career"),("Student","Intern"),("Office","Studio"),("Meeting","Hangout"),("Morning person","Night owl"),("Alarm","Reminder"),

    ],
    "tr": [

    # 🍕 YEMEK (30 pairs)
    ("Kebap","Lahmacun"),("Döner","Tantuni"),("Mantı","Gözleme"),("Pizza","Burger"),("Köfte","Sucuk"),("Menemen","Omlet"),("Pide","Poğaça"),("Baklava","Künefe"),("Dondurma","Sütlaç"),("Ayran","Şalgam"),("Çay","Kahve"),("Türk kahvesi","Filtre kahve"),("Enerji içeceği","Kola"),("Cips","Kraker"),("Çikolata","Bisküvi"),("Simit","Açma"),("Tost","Sandviç"),("Balık ekmek","Midye"),("Kumpir","Mısır"),("Lokum","Şeker"),("Tatlı","Pasta"),("Sucuklu yumurta","Sahanda yumurta"),("Mercimek çorbası","Ezogelin"),("Adana","Urfa"),("Kokoreç","Ciğer"),("Pilav","Bulgur"),("Fırın makarna","Spagetti"),("Salata","Meze"),("Hamburger","Islak hamburger"),("Nargile","Çekirdek"),

    # 🎉 PARTİ & EĞLENCE (30 pairs)
    ("Parti","Ev buluşması"),("Doğum günü","Yıl dönümü"),("Düğün","Nişan"),("Kulüp","Bar"),("DJ","Şarkıcı"),("Playlist","Şarkı listesi"),("Selfie","Toplu foto"),("Takım elbise","Spor kombin"),("Topuklu ayakkabı","Spor ayakkabı"),("Makyaj","Parfüm"),("Hediye","Sürpriz"),("Dans","Oyun havası"),("Yüksek müzik","Slow şarkı"),("After party","Öncesi buluşma"),("Kız kıza","Erkek erkeğe"),("Gece çıkışı","Akşam takılması"),("Sahil","Çatı katı"),("Ev partisi","Yazlık partisi"),("Shot","Bira"),("VIP masa","Normal masa"),("Hikaye","Gönderi"),("Canlı yayın","Video çekmek"),("Dekor","Işık"),("Pasta kesmek","Kadeh kaldırmak"),("Gece geç saat","Sabaha kadar"),("Konsept","Tema"),("Dans pisti","Masa başı"),("Takılmak","Buluşmak"),("Yaz partisi","Havuz partisi"),("Sürpriz giriş","Alkış"),

    # 😂 ARKADAŞ MUHABBETİ (30 pairs)
    ("Sevgili","Flört"),("Eski sevgili","Takipte kalmak"),("En yakın arkadaş","Kanka"),("Ev arkadaşı","Komşu"),("Patron","Müdür"),("Takılmak","Yazışmak"),("Trip atmak","Darılmak"),("Naz yapmak","Kapris"),("Drama","Kriz"),("Tembel","Rahat"),("Havalı","Cool"),("Gösteriş","Şekil yapmak"),("Zengin","Paralı"),("Geç kalmak","Son anda gelmek"),("Sporcu","Gym manyağı"),("Partici","Gece kuşu"),("Romantik","Aşık"),("Mesaj atmak","Aramak"),("Engellemek","Sessize almak"),("Ekran görüntüsü","Paylaşmak"),("Kıskanç","Meraklı"),("Sır","Sürpriz"),("Hava atmak","Övünmek"),("Abartmak","Büyütmek"),("Sessiz","Sakin"),("Enerjik","Hareketli"),("Utangaç","Rahat"),("Ciddi","Şakacı"),("Cool takılmak","Umursamamak"),("Dedikodu","Sohbet"),

    # 🚗 GÜNLÜK HAYAT (30 pairs)
    ("Araba","Jeep"),("Motor","Scooter"),("Uber","Taksi"),("Nakit","Kart"),("Alışveriş","Sipariş"),("Tatil","Gezi"),("Kamp","Piknik"),("Apartman","Site"),("AVM","Market"),("Park","Lunapark"),("Havuz","Deniz"),("Sinema","Konser"),("Televizyon","Laptop"),("Telefon","Tablet"),("Şarj aleti","Powerbank"),("Saat","Gözlük"),("Altın","Gümüş"),("Kahvaltı","Brunch"),("Öğle yemeği","Akşam yemeği"),("Spor","Antrenman"),("Kitap","Dergi"),("Dizi","Film"),("Futbol","Basketbol"),("Çay molası","Kahve molası"),("İş","Meslek"),("Öğrenci","Stajyer"),("Ofis","Atölye"),("Toplantı","Buluşma"),("Sabah insanı","Gece kuşu"),("Alarm","Hatırlatma"),
    
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
    game = games[uid]
    lang = game["lang"]

    text = (
        f"{TEXT[lang]['result']}\n\n"
        f"{TEXT[lang]['real']} {game['real']}\n"
        f"{TEXT[lang]['fake']} {game['fake']}"
    )

    kb = [[InlineKeyboardButton(TEXT[lang]["new"], callback_data="restart")]]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

    game["state"] = "finished"

# ================= RESTART =================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    lang = games[uid]["lang"]

    games[uid] = {
        "lang": lang,
        "state": "players",
    }
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

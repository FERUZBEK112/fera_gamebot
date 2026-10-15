# GameHub — o‘zbekcha Telegram o‘yin bot

Shaxsiy chatda uchta o‘yin: 3 kompyuter raqibi bilan UNO, 6 kompyuter raqibi bilan Mafia, tosh-qaychi-qog‘oz. O‘zbekcha menyu, kabinet, reyting, /resume, /admin. Ballar virtual, pul qiymatiga ega emas.

## Ishga tushirish

Python 3.12 yoki Docker. Tashqi Python paketlari kerak emas.

1. BotFather orqali yangi bot yarating.
2. `BOT_TOKEN` muhit o‘zgaruvchisiga tokenni kiriting.
3. Ixtiyoriy: `ADMIN_ID` — adminning raqamli Telegram ID raqami.
4. `python bot.py` yoki Docker orqali ishga tushiring.

## Railway

GitHub repo manbasini ulang. Dockerfile avtomatik build qiladi. Bitta replika ishlating. `/data` manziliga doimiy volume ulang, `DATA_DIR=/data` belgilang. Domen, PORT va webhook kerak emas: bot long polling orqali ishlaydi. BOT_TOKEN bo‘lmasa worker kutadi, token qo‘shilgach qayta deploy qiling. Tokenni GitHub fayllariga yozmang.

## O‘yin qoidalari

UNO: mos rang/belgi, reverse, skip, +2, wild va +4. +4 faqat faol rangdagi karta bo‘lmaganda. Draw stacking yo‘q. Karta olish yurishni yakunlaydi, UNO avtomatik. Wild rangini odam tanlaydi. Botlar oddiy ustuvorlik bilan mos kartani tanlaydi.

Mafia: 2 mafiyachi, doktor, detektiv, 3 fuqaro. Tunda odam roli bo‘yicha nishon tanlaydi. Doktor o‘zini ham qutqarishi mumkin. Detektiv natijasi faqat odamga ko‘rinadi. Kunduzi botlar tasodifiy ovoz beradi, mafiyachilar sherigiga ovoz bermaydi. Teng ovozda hech kim chiqarilmaydi. Odam o‘lsa kuzatishni davom ettiradi. Bu LLM suhbatli Mafia emas; botlar oddiy mahalliy algoritmlarda ishlaydi.

## Tekshirish

`python -m unittest -v test_games.py`

Testlar: 100 UNO o‘yini davomida 108 kartaning saqlanishi va yakunlanishi; +4 cheklovi; 100 Mafia o‘yini yakunlanishi. Telegram va Railway smoke test uchun haqiqiy BOT_TOKEN kerak.

SQLite o‘yinlar va reytingni volume ichida saqlaydi. Yangi o‘yin eski sessiyani almashtiradi. Eski tugmalar reviziya orqali rad etiladi. Token va API javoblari logga yozilmaydi.

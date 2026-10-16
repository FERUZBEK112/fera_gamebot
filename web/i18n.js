(function(){
"use strict";
var user=window.Telegram&&window.Telegram.WebApp&&window.Telegram.WebApp.initDataUnsafe?window.Telegram.WebApp.initDataUnsafe.user:null;
var storageKey="fera_language_"+(user&&user.id?user.id:"guest");
var supported=["uz","ru","en"];
var saved="";
try{saved=localStorage.getItem(storageKey)||""}catch(e){}
var lang=supported.indexOf(saved)>=0?saved:"";

var D={
 uz:{
  heroPlay:"O‘yna. Yut.",heroLead:"Yetakchi bo‘l.",heroText:"Botlarga qarshi tezkor o‘yinlar va jonli reyting.",
  games:"O‘YINLAR",today:"Bugun nimani o‘ynaymiz?",popular:"ENG MASHHUR",smartBots:"3 ta aqlli botga qarshi",
  mystery:"SIRLI O‘YIN",hiddenRole:"Yashirin rol • 7 o‘yinchi",quickFight:"Tezkor jang",testReflex:"Reaksiyangni sina",
  tenMath:"10 ta tezkor misol",testKnowledge:"Bilimingni tekshir",smartBot:"Aqlli botga qarshi",findPairs:"Juftliklarni top",
  guessSecret:"Sirli sonni aniqlang",friends:"Do‘stlar",friendsText:"Do‘stlaringizni chaqiring va har biri uchun mukofot oling",
  balance:"SIZNING BALANSINGIZ",inviteRule:"Har bir yangi do‘st botga taklif havolangiz orqali kirsa, sizga +0.5 ⭐.",
  invite:"🚀 DO‘STNI TAKLIF QILISH",copy:"🔗 Havolani nusxalash",virtual:"Game Stars — GameHub ichidagi virtual mukofot.",
  invited:"Taklif qilinganlar",loading:"Yuklanmoqda…",rating:"Reyting",bestPlayers:"Eng kuchli o‘yinchilar",
  score:"BALL",wins:"G‘ALABA",gamesStat:"O‘YIN",firstStep:"Birinchi qadam",finishFirst:"Birinchi o‘yiningizni yakunlang",
  about:"UNO, Mafia va tezkor mini-o‘yinlar. Natijalar Telegram profilingizga saqlanadi.",
  home:"Bosh sahifa",profile:"Profil",game:"O‘yin",language:"Til",changeLanguage:"🌐 Tilni o‘zgartirish",
  languageSaved:"Til saqlandi ✅",soundOn:"Musiqa yoqildi",soundOff:"Musiqa o‘chirildi",
  "Sizning yurishingiz":"Sizning yurishingiz","Bot o‘ylayapti…":"Bot o‘ylayapti…","Siz boshlaysiz":"Siz boshlaysiz",
  "Rangni tanlang":"Rangni tanlang","+ KARTA OLISH":"+ KARTA OLISH","Siz karta oldingiz":"Siz karta oldingiz",
  "Siz yutdingiz!":"Siz yutdingiz!","Bot g‘alaba qildi":"Bot g‘alaba qildi","QAYTA O‘YNASH":"QAYTA O‘YNASH",
  "O‘YINNI BOSHLASH":"O‘YINNI BOSHLASH","YANA O‘YNASH":"YANA O‘YNASH","YANA":"YANA","QAYTA":"QAYTA",
  "To‘g‘ri javobni tanlang":"To‘g‘ri javobni tanlang","Ajoyib natija!":"Ajoyib natija!","Yana mashq qilamiz!":"Yana mashq qilamiz!",
  "Sirli sonni toping":"Sirli sonni toping","TEKSHIRISH":"TEKSHIRISH","Topdingiz!":"Topdingiz!","Urinishlar tugadi":"Urinishlar tugadi",
  "Juftliklarni top":"Juftliklarni top","Hammasini topdingiz!":"Hammasini topdingiz!","O‘yin tugadi":"O‘yin tugadi",
  "Bot yutdi":"Bot yutdi","Durrang":"Durrang","Kuting…":"Kuting…","Hali bosmang":"Hali bosmang","BOSING!":"BOSING!",
  "Juda erta!":"Juda erta!","Qanchalik tezsiz?":"Qanchalik tezsiz?","Rang yashil bo‘lganda darhol bosing.":"Rang yashil bo‘lganda darhol bosing.",
  "BOSHLASH":"BOSHLASH","Tosh, qaychi yoki qog‘ozni tanlang":"Tosh, qaychi yoki qog‘ozni tanlang"
 },
 ru:{
  heroPlay:"Играй. Побеждай.",heroLead:"Стань лидером.",heroText:"Быстрые игры против ботов и живой рейтинг.",
  games:"ИГРЫ",today:"Во что сыграем сегодня?",popular:"ПОПУЛЯРНОЕ",smartBots:"Против 3 умных ботов",
  mystery:"ТАЙНАЯ ИГРА",hiddenRole:"Скрытая роль • 7 игроков",quickFight:"Быстрый бой",testReflex:"Проверь реакцию",
  tenMath:"10 быстрых примеров",testKnowledge:"Проверь знания",smartBot:"Против умного бота",findPairs:"Найди пары",
  guessSecret:"Угадай секретное число",friends:"Друзья",friendsText:"Приглашайте друзей и получайте награду за каждого",
  balance:"ВАШ БАЛАНС",inviteRule:"За каждого нового друга, вошедшего по вашей ссылке, вы получите +0.5 ⭐.",
  invite:"🚀 ПРИГЛАСИТЬ ДРУГА",copy:"🔗 Скопировать ссылку",virtual:"Game Stars — виртуальная награда внутри GameHub.",
  invited:"Приглашённые друзья",loading:"Загрузка…",rating:"Рейтинг",bestPlayers:"Лучшие игроки",
  score:"ОЧКИ",wins:"ПОБЕДЫ",gamesStat:"ИГРЫ",firstStep:"Первый шаг",finishFirst:"Завершите свою первую игру",
  about:"UNO, Mafia и быстрые мини-игры. Результаты сохраняются в вашем Telegram-профиле.",
  home:"Главная",profile:"Профиль",game:"Игра",language:"Язык",changeLanguage:"🌐 Изменить язык",
  languageSaved:"Язык сохранён ✅",soundOn:"Музыка включена",soundOff:"Музыка выключена",
  "Sizning yurishingiz":"Ваш ход","Bot o‘ylayapti…":"Бот думает…","Siz boshlaysiz":"Вы начинаете",
  "Rangni tanlang":"Выберите цвет","+ KARTA OLISH":"+ ВЗЯТЬ КАРТУ","Siz karta oldingiz":"Вы взяли карту",
  "Siz yutdingiz!":"Вы победили!","Bot g‘alaba qildi":"Бот победил","QAYTA O‘YNASH":"ИГРАТЬ СНОВА",
  "O‘YINNI BOSHLASH":"НАЧАТЬ ИГРУ","YANA O‘YNASH":"ИГРАТЬ СНОВА","YANA":"ЕЩЁ","QAYTA":"ПОВТОРИТЬ",
  "To‘g‘ri javobni tanlang":"Выберите правильный ответ","Ajoyib natija!":"Отличный результат!","Yana mashq qilamiz!":"Попробуем ещё раз!",
  "Sirli sonni toping":"Угадайте секретное число","TEKSHIRISH":"ПРОВЕРИТЬ","Topdingiz!":"Вы угадали!","Urinishlar tugadi":"Попытки закончились",
  "Juftliklarni top":"Найдите пары","Hammasini topdingiz!":"Все пары найдены!","O‘yin tugadi":"Игра окончена",
  "Bot yutdi":"Бот победил","Durrang":"Ничья","Kuting…":"Ждите…","Hali bosmang":"Пока не нажимайте","BOSING!":"ЖМИТЕ!",
  "Juda erta!":"Слишком рано!","Qanchalik tezsiz?":"Насколько вы быстры?","Rang yashil bo‘lganda darhol bosing.":"Нажмите сразу, когда цвет станет зелёным.",
  "BOSHLASH":"НАЧАТЬ","Tosh, qaychi yoki qog‘ozni tanlang":"Выберите камень, ножницы или бумагу"
 },
 en:{
  heroPlay:"Play. Win.",heroLead:"Become the leader.",heroText:"Fast games against bots and a live leaderboard.",
  games:"GAMES",today:"What shall we play today?",popular:"MOST POPULAR",smartBots:"Against 3 smart bots",
  mystery:"MYSTERY GAME",hiddenRole:"Secret role • 7 players",quickFight:"Quick battle",testReflex:"Test your reflexes",
  tenMath:"10 quick problems",testKnowledge:"Test your knowledge",smartBot:"Against a smart bot",findPairs:"Find matching pairs",
  guessSecret:"Guess the secret number",friends:"Friends",friendsText:"Invite friends and earn a reward for each one",
  balance:"YOUR BALANCE",inviteRule:"Earn +0.5 ⭐ for every new friend who joins through your invite link.",
  invite:"🚀 INVITE A FRIEND",copy:"🔗 Copy invite link",virtual:"Game Stars are virtual rewards inside GameHub.",
  invited:"Invited friends",loading:"Loading…",rating:"Leaderboard",bestPlayers:"Top players",
  score:"SCORE",wins:"WINS",gamesStat:"GAMES",firstStep:"First step",finishFirst:"Complete your first game",
  about:"UNO, Mafia and quick mini-games. Results are saved to your Telegram profile.",
  home:"Home",profile:"Profile",game:"Game",language:"Language",changeLanguage:"🌐 Change language",
  languageSaved:"Language saved ✅",soundOn:"Music on",soundOff:"Music off",
  "Sizning yurishingiz":"Your turn","Bot o‘ylayapti…":"Bot is thinking…","Siz boshlaysiz":"You start",
  "Rangni tanlang":"Choose a color","+ KARTA OLISH":"+ DRAW A CARD","Siz karta oldingiz":"You drew a card",
  "Siz yutdingiz!":"You won!","Bot g‘alaba qildi":"The bot won","QAYTA O‘YNASH":"PLAY AGAIN",
  "O‘YINNI BOSHLASH":"START GAME","YANA O‘YNASH":"PLAY AGAIN","YANA":"AGAIN","QAYTA":"RETRY",
  "To‘g‘ri javobni tanlang":"Choose the correct answer","Ajoyib natija!":"Great result!","Yana mashq qilamiz!":"Let’s practice again!",
  "Sirli sonni toping":"Guess the secret number","TEKSHIRISH":"CHECK","Topdingiz!":"You got it!","Urinishlar tugadi":"No attempts left",
  "Juftliklarni top":"Find the pairs","Hammasini topdingiz!":"You found them all!","O‘yin tugadi":"Game over",
  "Bot yutdi":"Bot won","Durrang":"Draw","Kuting…":"Wait…","Hali bosmang":"Do not tap yet","BOSING!":"TAP!",
  "Juda erta!":"Too early!","Qanchalik tezsiz?":"How fast are you?","Rang yashil bo‘lganda darhol bosing.":"Tap as soon as the color turns green.",
  "BOSHLASH":"START","Tosh, qaychi yoki qog‘ozni tanlang":"Choose rock, scissors or paper"
 }
};
var reverse={};
Object.keys(D.uz).forEach(function(key){supported.forEach(function(code){var value=D[code][key];if(value)reverse[value]=key})});
function t(key){return(D[lang]&&D[lang][key])||D.uz[key]||key}
function translateText(raw){
 var trimmed=String(raw||"").trim();if(!trimmed)return raw;
 var key=reverse[trimmed];if(!key)return raw;
 var out=t(key),start=raw.indexOf(trimmed);return raw.slice(0,start)+out+raw.slice(start+trimmed.length)
}
function translateNode(node){
 if(!node)return;
 if(node.nodeType===3){var out=translateText(node.nodeValue);if(out!==node.nodeValue)node.nodeValue=out;return}
 if(node.nodeType!==1||node.tagName==="SCRIPT"||node.tagName==="STYLE")return;
 if(node.dataset&&node.dataset.i18n)node.textContent=t(node.dataset.i18n);
 if(node.dataset&&node.dataset.i18nHtml)node.innerHTML=t(node.dataset.i18nHtml);
 Array.prototype.slice.call(node.childNodes||[]).forEach(translateNode);
}
function apply(){
 document.documentElement.lang=lang||"uz";
 if(document.body)document.body.setAttribute("data-language",lang||"uz");
 Array.prototype.slice.call(document.querySelectorAll("[data-i18n]")).forEach(function(el){el.textContent=t(el.dataset.i18n)});
 Array.prototype.slice.call(document.querySelectorAll("[data-i18n-html]")).forEach(function(el){el.innerHTML=t(el.dataset.i18nHtml)});
 Array.prototype.slice.call(document.querySelectorAll("[data-language]")).forEach(function(el){
  var active=el.dataset.language===lang;el.classList.toggle("active",active);el.setAttribute("aria-pressed",active?"true":"false");
 });
 translateNode(document.body);
}
function showGate(){var gate=document.getElementById("languageGate");if(gate)gate.classList.add("show")}
function hideGate(){var gate=document.getElementById("languageGate");if(gate)gate.classList.remove("show")}
function setLanguage(code,notify){
 if(supported.indexOf(code)<0)return;
 lang=code;try{localStorage.setItem(storageKey,code)}catch(e){}
 apply();hideGate();
 if(window.requestAnimationFrame)window.requestAnimationFrame(apply);else setTimeout(apply,0);
 if(notify!==false&&typeof window.onFeraLanguageChange==="function")window.onFeraLanguageChange(code);
}
window.FeraI18n={t:t,getLanguage:function(){return lang},setLanguage:setLanguage,showGate:showGate,hideGate:hideGate,apply:apply};
document.addEventListener("click",function(event){
 var target=event.target;
 var button=target&&target.closest?target.closest("[data-language]"):null;
 if(button){event.preventDefault();event.stopPropagation();setLanguage(button.dataset.language,true);return}
 var change=target&&target.closest?target.closest("#changeLanguageBtn"):null;
 if(change){event.preventDefault();showGate()}
});
if(lang){apply();hideGate()}else showGate();
if(window.MutationObserver){new MutationObserver(function(records){records.forEach(function(record){Array.prototype.slice.call(record.addedNodes||[]).forEach(translateNode)})}).observe(document.body,{childList:true,subtree:true})}
})();
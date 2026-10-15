(function(){
"use strict";
var tg=window.Telegram&&window.Telegram.WebApp;
if(tg){tg.ready();tg.expand();try{tg.setHeaderColor("#070b17");tg.setBackgroundColor("#060914")}catch(e){}}
var initData=tg?tg.initData:"";
var user=tg&&tg.initDataUnsafe&&tg.initDataUnsafe.user?tg.initDataUnsafe.user:null;
var profile={name:user?(user.first_name+(user.last_name?" "+user.last_name:"")):"Mehmon",username:user&&user.username?"@"+user.username:"Telegram orqali oching",score:0,wins:0,played:0};
var sound=true,currentGame=null,reflexTimer=null;
var $=function(q){return document.querySelector(q)};
var $$=function(q){return Array.prototype.slice.call(document.querySelectorAll(q))};
function esc(s){return String(s||"").replace(/[&<>"']/g,function(c){return({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c]})}
function haptic(type){if(tg&&tg.HapticFeedback){if(type==="success"||type==="error")tg.HapticFeedback.notificationOccurred(type);else tg.HapticFeedback.impactOccurred(type||"light")}}
function toast(msg){var el=$("#toast");el.textContent=msg;el.classList.add("show");setTimeout(function(){el.classList.remove("show")},1900)}
async function api(path,options){options=options||{};options.headers=Object.assign({"Content-Type":"application/json","X-Telegram-Init-Data":initData},options.headers||{});try{var r=await fetch(path,options);if(!r.ok)throw new Error();return await r.json()}catch(e){return null}}
function showView(name){
  $$(".view").forEach(function(v){v.classList.remove("active")});
  $$(".nav-btn").forEach(function(v){v.classList.toggle("active",v.dataset.view===name)});
  $("#gameView").classList.toggle("active",name==="game");
  if(name!=="game")$("#"+name+"View").classList.add("active");
  $(".bottom-nav").style.display=name==="game"?"none":"flex";
  if(name==="leader")loadLeaderboard();
  if(name==="profile")renderProfile();
  window.scrollTo(0,0);
}
$$(".nav-btn").forEach(function(b){b.onclick=function(){showView(b.dataset.view)}});
$("#backBtn").onclick=function(){if(reflexTimer)clearTimeout(reflexTimer);currentGame=null;showView("home")};
$("#soundBtn").onclick=function(){sound=!sound;this.textContent=sound?"♫":"×";toast(sound?"Ovoz yoqildi":"Ovoz o‘chirildi")};
$$(".game-card").forEach(function(b){b.onclick=function(){openGame(b.dataset.game)}});
function setGame(title,sub,score){$("#gameTitle").textContent=title;$("#gameSub").textContent=sub;$("#gameScore").textContent=score||"0"}
async function loadProfile(){var d=await api("/api/profile");if(d&&d.ok){profile=d.user;renderProfile()}}
function renderProfile(){
  $("#profileName").textContent=profile.name||"O‘yinchi";$("#profileUser").textContent=profile.username||"";
  $("#profileAvatar").textContent=(profile.name||"F").charAt(0).toUpperCase();
  $("#statScore").textContent=profile.score||0;$("#statWins").textContent=profile.wins||0;$("#statGames").textContent=profile.played||0;
  $("#achievementState").textContent=(profile.played?1:0)+"/1";
}
async function record(game,won,score){if(won){profile.wins=(profile.wins||0)+1}profile.played=(profile.played||0)+1;profile.score=(profile.score||0)+(score||0);renderProfile();await api("/api/result",{method:"POST",body:JSON.stringify({game:game,won:!!won,score:Math.max(0,Math.min(5000,score||0))})})}
async function loadLeaderboard(){
 var d=await api("/api/leaderboard"),rows=d&&d.users?d.users:[{name:profile.name,username:profile.username,score:profile.score||0,wins:profile.wins||0}];
 while(rows.length<3)rows.push({name:"Bo‘sh joy",username:"",score:0,wins:0});
 var order=[rows[1],rows[0],rows[2]],classes=["","first",""];
 $("#podium").innerHTML=order.map(function(x,i){var place=[2,1,3][i];return'<div class="podium-item '+classes[i]+'"><div class="p-avatar">'+esc((x.name||"?").charAt(0))+'</div><b>'+esc(x.name)+'</b><span>'+x.score+' ball</span><div class="stand">'+place+'</div></div>'}).join("");
 $("#rankList").innerHTML=rows.slice(3,20).map(function(x,i){return'<div class="rank-row"><span>'+(i+4)+'</span><div class="rank-avatar">'+esc((x.name||"?").charAt(0))+'</div><div><h4>'+esc(x.name)+'</h4><p>'+(x.wins||0)+' g‘alaba</p></div><b class="rank-score">'+(x.score||0)+'</b></div>'}).join("")||'<div class="loader">Hali boshqa o‘yinchilar yo‘q</div>';
}
function openGame(g){currentGame=g;showView("game");if(g==="uno")startUno();else if(g==="mafia")startMafia();else if(g==="rps")startRps();else startReflex()}

/* UNO */
var UCOL={R:"c-red",Y:"c-yellow",G:"c-green",B:"c-blue",W:"c-wild"},UNO=null;
function unoDeck(){var d=[],cs=["R","Y","G","B"];cs.forEach(function(c){d.push({c:c,v:"0"});["1","2","3","4","5","6","7","8","9","⊘","↻","+2"].forEach(function(v){d.push({c:c,v:v},{c:c,v:v})})});for(var i=0;i<4;i++)d.push({c:"W",v:"W"},{c:"W",v:"+4"});return shuffle(d)}
function shuffle(a){for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=a[i];a[i]=a[j];a[j]=t}return a}
function drawUno(p,n){n=n||1;while(n--){if(!UNO.deck.length){var top=UNO.discard.pop();UNO.deck=shuffle(UNO.discard);UNO.discard=[top]}UNO.hands[p].push(UNO.deck.pop())}}
function legalUno(card){var top=UNO.discard[UNO.discard.length-1];return card.c==="W"||card.c===UNO.color||card.v===top.v}
function startUno(){setGame("UNO ARENA","3 BOTGA QARSHI","🏆 120");var deck=unoDeck(),hands=[[],[],[],[]];for(var i=0;i<7;i++)for(var p=0;p<4;p++)hands[p].push(deck.pop());var first=deck.pop();while(first.c==="W"||isNaN(Number(first.v))) {deck.unshift(first);first=deck.pop()}UNO={deck:deck,hands:hands,discard:[first],color:first.c,turn:0,dir:1,log:"Siz boshlaysiz"};renderUno()}
function unoCard(card,index,enabled){return'<button class="uno-card-btn '+UCOL[card.c]+'" '+(enabled?'data-u="'+index+'"':'disabled')+'>'+esc(card.v)+'</button>'}
function renderUno(){
 var top=UNO.discard[UNO.discard.length-1];
 $("#gameStage").innerHTML='<div class="uno-board"><div class="opponents">'+[1,2,3].map(function(p){return'<div class="opponent '+(UNO.turn===p?"turning":"")+'"><div class="face">'+["🤖","👾","🦾"][p-1]+'</div><b>BOT '+p+'</b><span>'+UNO.hands[p].length+' karta</span></div>'}).join("")+'</div><div class="uno-center"><div class="uno-pile uno-deck">UNO<br>'+UNO.deck.length+'</div><div class="uno-pile '+UCOL[top.c]+'">'+esc(top.v)+'</div><div class="uno-log">'+esc(UNO.log)+'</div></div><div class="uno-actions"><span>'+(UNO.turn===0?"Sizning yurishingiz":"Bot o‘ylayapti…")+'</span><button class="btn secondary" id="unoDraw" '+(UNO.turn!==0?"disabled":"")+'>+ KARTA OLISH</button></div><div class="uno-hand">'+UNO.hands[0].map(function(c,i){return unoCard(c,i,UNO.turn===0&&legalUno(c))}).join("")+'</div></div>';
 $$("#gameStage [data-u]").forEach(function(b){b.onclick=function(){playerUno(Number(b.dataset.u))}});
 var dr=$("#unoDraw");if(dr)dr.onclick=function(){drawUno(0);UNO.log="Siz karta oldingiz";UNO.turn=nextUno(0,1);renderUno();setTimeout(botUno,650)};
}
function nextUno(p,step){return(p+UNO.dir*(step||1)+4)%4}
function playerUno(i){var c=UNO.hands[0][i];if(c.c==="W"){haptic("light");$("#gameStage").innerHTML='<div class="game-result"><div class="big">🌈</div><h2>Rangni tanlang</h2><div class="color-pick">'+["R","Y","G","B"].map(function(x){return'<button class="'+UCOL[x]+'" data-color="'+x+'"></button>'}).join("")+'</div></div>';$$("[data-color]").forEach(function(b){b.onclick=function(){commitUno(0,i,b.dataset.color)}})}else commitUno(0,i,c.c)}
function commitUno(p,i,color){
 var card=UNO.hands[p].splice(i,1)[0];UNO.discard.push(card);UNO.color=card.c==="W"?color:card.c;UNO.log=(p===0?"Siz":"Bot "+p)+" "+card.v+" tashladi";
 if(!UNO.hands[p].length)return endUno(p===0);
 if(UNO.hands[p].length===1)UNO.log+=" • UNO!";
 if(card.v==="↻")UNO.dir*=-1;
 var step=1;if(card.v==="⊘")step=2;
 if(card.v==="+2"){var victim=nextUno(p);drawUno(victim,2);step=2}
 if(card.v==="+4"){var victim4=nextUno(p);drawUno(victim4,4);step=2}
 UNO.turn=nextUno(p,step);renderUno();if(UNO.turn!==0)setTimeout(botUno,650);
}
function botUno(){
 if(!UNO||UNO.turn===0)return;var p=UNO.turn,choices=[];UNO.hands[p].forEach(function(c,i){if(legalUno(c))choices.push(i)});
 if(!choices.length){drawUno(p);UNO.log="Bot "+p+" karta oldi";UNO.turn=nextUno(p);renderUno();if(UNO.turn!==0)setTimeout(botUno,650);return}
 choices.sort(function(a,b){return(["+4","+2","⊘","↻"].indexOf(UNO.hands[p][b].v))- (["+4","+2","⊘","↻"].indexOf(UNO.hands[p][a].v))});
 var idx=choices[0],card=UNO.hands[p][idx],counts={R:0,Y:0,G:0,B:0};UNO.hands[p].forEach(function(c){if(counts[c.c]!=null)counts[c.c]++});var color=Object.keys(counts).sort(function(a,b){return counts[b]-counts[a]})[0];commitUno(p,idx,card.c==="W"?color:card.c)
}
function endUno(win){haptic(win?"success":"error");if(win)record("uno",true,120);else record("uno",false,15);$("#gameStage").innerHTML='<div class="game-result"><div class="big">'+(win?"🏆":"🤖")+'</div><h2>'+(win?"Siz yutdingiz!":"Bot g‘alaba qildi")+'</h2><p>'+(win?"+120 ball. Ajoyib yurish!":"Yana urinib ko‘ring — bu safar albatta yutasiz.")+'</p><button class="btn" id="again">QAYTA O‘YNASH</button></div>';$("#again").onclick=startUno}

/* MAFIA */
var MAF=null,ROLEINFO={Mafiya:["🕴️","Tunda qurbon tanlang. Mafiyani saqlab qoling."],Doktor:["💉","Tunda bir o‘yinchini qutqaring."],Detektiv:["🔎","Tunda bir o‘yinchining rolini tekshiring."],Fuqaro:["🏙️","Kunduzi mafiyani topib ovoz bering."]};
function startMafia(){setGame("MAFIA NIGHT","7 O‘YINCHI","🌙 1");var roles=shuffle(["Mafiya","Mafiya","Doktor","Detektiv","Fuqaro","Fuqaro","Fuqaro"]);MAF={roles:roles,alive:[true,true,true,true,true,true,true],phase:"reveal",day:1,log:"Rolingiz sir. Hech kimga aytmang.",known:{}};renderMafia()}
function renderMafia(){
 var role=MAF.roles[0],info=ROLEINFO[role];$("#gameScore").textContent="🌙 "+MAF.day;
 if(MAF.phase==="reveal"){$("#gameStage").innerHTML='<div class="role-card"><div class="role-icon">'+info[0]+'</div><span class="eyebrow">SIZNING ROLINGIZ</span><h2>'+role+'</h2><p>'+info[1]+'</p><button class="btn" id="mafiaBegin">O‘YINNI BOSHLASH</button></div>';$("#mafiaBegin").onclick=function(){MAF.phase="night";renderMafia()};return}
 var night=MAF.phase==="night";var selectable=MAF.alive.map(function(x,i){return x&&i!==0?i:null}).filter(function(x){return x!=null});
 var title=night?"🌙 Tun":"☀️ "+MAF.day+"-kun";var sub=night?(role==="Mafiya"?"Kimni yo‘q qilasiz?":role==="Doktor"?"Kimni qutqarasiz?":role==="Detektiv"?"Kimni tekshirasiz?":"Shahar uxlamoqda…"):"Kim mafiyachi? Ovoz bering.";
 $("#gameStage").innerHTML='<div class="mafia-scene"><div class="phase-banner"><b>'+title+'</b><span>'+sub+'</span></div><div class="players-grid">'+MAF.alive.map(function(alive,i){if(i===0)return'<div class="player-tile"><div class="face">'+ROLEINFO[role][0]+'</div><b>SIZ</b></div>';return'<button class="player-tile '+(!alive?"dead ":"")+(alive?"selectable":"")+'" '+(alive?'data-m="'+i+'"':'')+'><div class="face">'+["🤵","👩","🧔","👨","👩‍🦰","🧑"][i-1]+'</div><b>BOT '+i+'</b></button>'}).join("")+'</div><div class="mafia-log">'+esc(MAF.log)+'</div><div class="mafia-action" id="mafiaAction"></div></div>';
 var canChoose=!night||role!=="Fuqaro";if(canChoose)$$("[data-m]").forEach(function(b){b.onclick=function(){if(night)mafiaNight(Number(b.dataset.m));else mafiaVote(Number(b.dataset.m))}});
 else $("#mafiaAction").innerHTML='<button class="btn" id="waitNight">TONGNI KUTISH</button>';
 var w=$("#waitNight");if(w)w.onclick=function(){mafiaNight(null)};
}
function mafiaNight(target){
 var role=MAF.roles[0],mafia=MAF.alive.map(function(x,i){return x&&MAF.roles[i]==="Mafiya"?i:null}).filter(function(x){return x!=null}),victims=MAF.alive.map(function(x,i){return x&&mafia.indexOf(i)<0?i:null}).filter(function(x){return x!=null});
 var victim=role==="Mafiya"?target:victims[Math.floor(Math.random()*victims.length)];
 var docs=MAF.alive.some(function(x,i){return x&&MAF.roles[i]==="Doktor"}),saved=docs?(role==="Doktor"?target:randomAlive()):null;
 if(role==="Detektiv"&&target!=null){MAF.known[target]=MAF.roles[target]==="Mafiya";MAF.log="🔎 Bot "+target+(MAF.known[target]?" — MAFIYACHI!":" — mafiyachi emas.")}else if(victim===saved)MAF.log="💉 Doktor qurbonni qutqardi. Hech kim o‘lmadi.";else{MAF.alive[victim]=false;MAF.log="🌙 Bot "+victim+" halok bo‘ldi. Uning roli: "+MAF.roles[victim]}
 var win=mafiaWinner();if(win)return endMafia(win);MAF.phase="day";renderMafia()
}
function randomAlive(){var a=MAF.alive.map(function(x,i){return x?i:null}).filter(function(x){return x!=null});return a[Math.floor(Math.random()*a.length)]}
function mafiaVote(target){
 var votes=[target];for(var p=1;p<7;p++){if(!MAF.alive[p])continue;var choices=MAF.alive.map(function(x,i){return x&&i!==p?i:null}).filter(function(x){return x!=null});if(MAF.roles[p]==="Mafiya")choices=choices.filter(function(i){return MAF.roles[i]!=="Mafiya"});votes.push(choices[Math.floor(Math.random()*choices.length)])}
 var count={};votes.forEach(function(v){count[v]=(count[v]||0)+1});var max=Math.max.apply(null,Object.values(count)),leaders=Object.keys(count).filter(function(k){return count[k]===max}).map(Number);
 if(leaders.length===1){var out=leaders[0];MAF.alive[out]=false;MAF.log="🗳️ Bot "+out+" chiqarildi. Roli: "+MAF.roles[out]}else MAF.log="🗳️ Ovozlar teng. Hech kim chiqarilmadi.";
 var win=mafiaWinner();if(win)return endMafia(win);MAF.day++;MAF.phase="night";setTimeout(renderMafia,500);renderMafia()
}
function mafiaWinner(){var m=0,c=0;MAF.alive.forEach(function(x,i){if(x){if(MAF.roles[i]==="Mafiya")m++;else c++}});if(!m)return"Shahar";if(m>=c)return"Mafiya";return null}
function endMafia(side){var playerSide=MAF.roles[0]==="Mafiya"?"Mafiya":"Shahar",win=side===playerSide;haptic(win?"success":"error");record("mafia",win,win?180:20);$("#gameStage").innerHTML='<div class="game-result"><div class="big">'+(win?"🏆":"🎭")+'</div><h2>'+side+" yutdi"+'</h2><p>'+(win?"+180 ball. Sirni ajoyib saqladingiz!":"Bu shaharda hech kimga ishonib bo‘lmaydi…")+'</p><button class="btn" id="againM">YANA O‘YNASH</button></div>';$("#againM").onclick=startMafia}

/* RPS */
function startRps(){setGame("RPS BATTLE","TEZKOR JANG","BO3");$("#gameStage").innerHTML='<div class="rps-arena"><span class="eyebrow">TANLOVINGIZ</span><div class="rps-battle"><div class="rps-choice" id="myRps">?</div><b class="rps-vs">VS</b><div class="rps-choice" id="botRps">🤖</div></div><div class="rps-buttons">'+["✊","✌️","🖐️"].map(function(x,i){return'<button data-rps="'+i+'">'+x+'</button>'}).join("")+'</div><p class="uno-log" id="rpsText">Tosh, qaychi yoki qog‘ozni tanlang</p></div>';$$("[data-rps]").forEach(function(b){b.onclick=function(){playRps(Number(b.dataset.rps))}})}
function playRps(me){var icons=["✊","✌️","🖐️"],bot=Math.floor(Math.random()*3),win=(me-bot+3)%3===2,draw=me===bot;$("#myRps").textContent=icons[me];$("#botRps").textContent=icons[bot];$("#rpsText").textContent=draw?"DURRANG":win?"SIZ YUTDINGIZ! +40 BALL":"BOT YUTDI";haptic(draw?"light":win?"success":"error");record("rps",win,win?40:0);setTimeout(function(){var a=document.createElement("button");a.className="btn";a.textContent="YANA";a.onclick=startRps;$("#rpsText").after(a)},500)}

/* REFLEX */
function startReflex(){setGame("REFLEX","REAKSIYA TESTI","⚡");$("#gameStage").innerHTML='<div class="reflex-box" id="reflexBox"><div class="reflex-content"><div class="bolt">⚡</div><h2>Qanchalik tezsiz?</h2><p>Rang yashil bo‘lganda darhol bosing.</p><button class="btn" id="reflexStart">BOSHLASH</button></div></div>';$("#reflexStart").onclick=armReflex}
function armReflex(){var box=$("#reflexBox");box.className="reflex-box waiting";box.innerHTML='<div class="reflex-content"><div class="bolt pulse">•••</div><h2>Kuting…</h2><p>Hali bosmang</p></div>';var ready=false,start=0;box.onclick=function(){if(!ready){clearTimeout(reflexTimer);box.className="reflex-box early";box.innerHTML='<div class="reflex-content"><div class="bolt">😅</div><h2>Juda erta!</h2><button class="btn" id="retryReflex">QAYTA</button></div>';$("#retryReflex").onclick=function(e){e.stopPropagation();armReflex()}}else{var ms=Math.round(performance.now()-start),score=Math.max(10,Math.min(300,420-ms));record("reflex",ms<350,score);box.onclick=null;box.innerHTML='<div class="reflex-content"><div class="reflex-time">'+ms+' ms</div><h2>'+(ms<220?"CHАQMOQ!":ms<350?"AJOYIB!":"YAXSHI")+'</h2><p>+'+score+' ball</p><button class="btn" id="retryReflex">YANA</button></div>';$("#retryReflex").onclick=armReflex;haptic(ms<350?"success":"light")}};reflexTimer=setTimeout(function(){ready=true;start=performance.now();box.className="reflex-box ready";box.innerHTML='<div class="reflex-content"><div class="bolt">⚡</div><h2>BOSING!</h2></div>'},1500+Math.random()*2600)}
renderProfile();loadProfile();
})();
"""Uzbek Telegram game hub. Standard-library-only long polling worker."""
import json
import logging
import os
import pickle
import random
import secrets
import signal
import sqlite3
import time
import urllib.request
from games import Uno, Mafia, COLORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
ROOT = os.getenv('DATA_DIR', './data')
os.makedirs(ROOT, exist_ok=True)
db = sqlite3.connect(os.path.join(ROOT,'games.db'))
db.executescript('''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, wins INTEGER DEFAULT 0, played INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY, state BLOB);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value INTEGER);
''')
TOKEN = os.getenv('BOT_TOKEN','')
MENU = {'keyboard': [[{'text':'🎮 O‘yinlar'},{'text':'👤 Kabinet'}],[{'text':'🏆 Reyting'},{'text':'📖 Qoidalar'}]], 'resize_keyboard':True}

def api(method, **data):
    req = urllib.request.Request('https://api.telegram.org/bot'+TOKEN+'/'+method,
        json.dumps(data).encode(), {'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=40) as r: result=json.load(r)
    if not result.get('ok'): raise RuntimeError('Telegram API rejected '+method)
    return result['result']

def send(chat,text,buttons=None):
    return api('sendMessage',chat_id=chat,text=text,reply_markup={'inline_keyboard':buttons} if buttons is not None else MENU)

def button(text,data): return {'text':text,'callback_data':data}

def save(uid,s):
    db.execute('INSERT OR REPLACE INTO sessions VALUES(?,?)',(uid,pickle.dumps(s)))
    db.commit()

def load(uid):
    row=db.execute('SELECT state FROM sessions WHERE id=?',(uid,)).fetchone()
    return pickle.loads(row[0]) if row else None

def finish(uid,s,won):
    if s.get('scored'): return
    s['scored']=True
    db.execute('UPDATE users SET wins=wins+?,played=played+1 WHERE id=?',(int(won),uid))

def lobby(chat):
    send(chat,'🎮 GAME HUB\n\nRaqiblar tayyor! O‘yinni tanlang:',[
        [button('🃏 UNO • 3 raqib','new:uno')],
        [button('🎭 Mafia • 6 raqib','new:mafia')],
        [button('✊ Tosh · qaychi · qog‘oz','new:rps')]])

def render(uid,chat,s):
    s['rev']=secrets.token_hex(4)
    tag=s['rev']
    g=s['game']; rows=[]
    def b(text,action): return button(text,tag+':'+action)
    if s['kind']=='uno':
        text='🃏 UNO\nStol: '+''.join(g.discard[-1])+' • Faol rang: '+g.color+'\n'
        text+=' | '.join(f'Bot {p}: {len(g.hands[p])} ta' for p in range(1,4))+'\n\n'
        text+='\n'.join(g.log[-10:])+'\n'
        if g.winner is not None:
            text+='\n🏁 '+('Siz yutdingiz! 🎉' if g.winner==0 else f'Bot {g.winner} yutdi.')
            finish(uid,s,g.winner==0)
        else:
            text+='\nSizning kartalaringiz: '+ ' '.join(''.join(c) for c in g.hands[0])
            if s.get('wild') is not None:
                rows=[[b(c,'color:'+str(i)) for i,c in enumerate(COLORS)]]
            else:
                cards=[b(''.join(c),'play:'+str(i)) for i,c in enumerate(g.hands[0]) if g.legal(0,i)]
                rows=[cards[i:i+4] for i in range(0,len(cards),4)]
                rows.append([b('📥 Karta olish va yurishni yakunlash','draw')])
    elif s['kind']=='mafia':
        role=g.roles[0]
        text=f'🎭 MAFIA • {g.day}-kun\nSizning rolingiz: {role}\n'
        if role=='Mafiya': text+='Sherigingiz: '+', '.join(g.name(p) for p in range(1,7) if g.roles[p]=='Mafiya')+'\n'
        text+='Tiriklar: '+', '.join(g.name(p) for p in g.alive)+'\n\n'+'\n'.join(g.log[-9:])
        if g.winner:
            text+='\n\n🏁 '+g.winner+' g‘alaba qozondi!'
            finish(uid,s,(role=='Mafiya')==(g.winner=='Mafiya'))
        elif 0 not in g.alive:
            text+='\n\nSiz o‘yindan chiqdingiz. Kuzatishni davom ettiring.'
            rows=[[b('⏩ Keyingi bosqich','advance')]]
        elif g.phase=='day':
            text+='\n\n☀️ Kimga ovoz berasiz? Botlar mustaqil ovoz beradi.'
            rows=[[b(g.name(p),'vote:'+str(p))] for p in g.targets()]
        elif role=='Fuqaro':
            text+='\n\n🌙 Shahar uxlamoqda...'
            rows=[[b('☀️ Tongni kutish','night')]]
        else:
            text+='\n\n🌙 '+{'Mafiya':'Kimni yo‘q qilasiz?','Doktor':'Kimni qutqarasiz?','Detektiv':'Kimni tekshirasiz?'}[role]
            rows=[[b(g.name(p),'night:'+str(p))] for p in g.targets()]
    else:
        text='✊ Tosh · qaychi · qog‘oz\nTanlovingizni bosing!'
        if s.get('result'):
            text=s['result']
        else: rows=[[b(c,'rps:'+str(i)) for i,c in enumerate(['✊','✌️','🖐'])]]
    rows.append([button('🎮 O‘yin tanlash','lobby')])
    save(uid,s)
    send(chat,text,rows)

def callback(q):
    uid=q['from']['id']; chat=q['message']['chat']['id']; data=q.get('data','')
    api('answerCallbackQuery',callback_query_id=q['id'])
    if data=='lobby': return lobby(chat)
    if data.startswith('new:'):
        kind=data.split(':')[1]
        if kind not in ['uno','mafia','rps']: return
        s={'kind':kind,'game':Uno() if kind=='uno' else Mafia() if kind=='mafia' else None}
        return render(uid,chat,s)
    s=load(uid)
    parts=data.split(':')
    if not s or parts[0]!=s['rev']:
        return send(chat,'Bu tugma eskirgan. Eng oxirgi o‘yin xabaridagi tugmadan foydalaning.')
    action=parts[1]; n=int(parts[2]) if len(parts)>2 else None; g=s['game']
    if s.get('scored'): return lobby(chat)
    if s['kind']=='uno':
        if action=='play':
            if n is None or not 0<=n<len(g.hands[0]) or not g.legal(0,n): raise ValueError('Yaroqsiz karta.')
            if g.hands[0][n][0]=='🌈': s['wild']=n
            else: g.play(n); g.bots()
        elif action=='color' and s.get('wild') is not None and n in range(4):
            g.play(s.pop('wild'),COLORS[n]); g.bots()
        elif action=='draw' and s.get('wild') is None:
            g.draw(0); g.turn=(g.turn+g.direction)%4; g.bots()
    elif s['kind']=='mafia':
        if n is not None and n not in g.targets(): raise ValueError('Yaroqsiz nishon.')
        if action=='night' and (g.roles[0]=='Fuqaro' or n is not None): g.night(n)
        elif action=='vote': g.vote(n)
        elif action=='advance' and 0 not in g.alive:
            if g.phase=='night': g.night()
            else: g.vote()
    elif action=='rps' and n in range(3):
        bot=random.randrange(3); labels=['✊','✌️','🖐']
        won=(n-bot)%3==2
        result='🤝 Durrang!' if n==bot else '🎉 Siz yutdingiz!' if won else '🤖 Bot yutdi!'
        s['result']=f'Siz: {labels[n]} • Bot: {labels[bot]}\n{result}'
        finish(uid,s,won)
    render(uid,chat,s)

def handle(update):
    q=update.get('callback_query'); m=update.get('message') or (q or {}).get('message')
    if not m: return
    if m['chat']['type']!='private':
        if update.get('message'): send(m['chat']['id'],'O‘ynash uchun botning shaxsiy chatiga yozing.')
        return
    user=(q or m).get('from',{}); uid=user.get('id'); chat=m['chat']['id']
    if not uid: return
    db.execute('INSERT INTO users(id,name) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name', (uid,user.get('first_name','O‘yinchi')[:40]))
    db.commit()
    if q: return callback(q)
    text=m.get('text','')
    if text in ['/start','🎮 O‘yinlar']: return lobby(chat)
    if text=='👤 Kabinet':
        name,wins,played=db.execute('SELECT name,wins,played FROM users WHERE id=?',(uid,)).fetchone()
        return send(chat,f'👤 {name}\n🆔 {uid}\n🎮 Yakunlangan: {played}\n🏆 G‘alabalar: {wins}\n⭐ Ball: {wins*10}')
    if text=='🏆 Reyting':
        rows=db.execute('SELECT name,wins FROM users ORDER BY wins DESC,played ASC LIMIT 10').fetchall()
        return send(chat,'🏆 Eng yaxshi o‘yinchilar\n\n'+'\n'.join(f'{i+1}. {n} — {w*10} ball' for i,(n,w) in enumerate(rows)))
    if text=='/admin' and str(uid)==os.getenv('ADMIN_ID'):
        count=db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        return send(chat,f'🛠 Admin\nFoydalanuvchilar: {count}')
    if text=='/resume':
        s=load(uid)
        return render(uid,chat,s) if s else lobby(chat)
    send(chat,'📖 Qoidalar\n\n🃏 UNO: rang yoki belgi mos kartani tashlang. +2/+4 keyingi raqibni karta olishga majbur qiladi; ustma-ust yig‘ilmaydi. +4 faqat faol rang qolmaganda. Karta olsangiz yurish tugaydi. UNO avtomatik aytiladi. Birinchi bo‘lib kartasini tugatgan yutadi.\n\n🎭 Mafia: siz va 6 bot. 2 mafiyachi, doktor, detektiv, 3 fuqaro. Tunda rol bo‘yicha harakat, kunduzi ovoz berish. Teng ovozda hech kim chiqarilmaydi. Mafiya soni shaharliklarga tenglashsa mafiyachilar yutadi. Botlar oddiy tasodifiy strategiyada o‘ynaydi.\n\n✊ Tosh qaychini, qaychi qog‘ozni, qog‘oz toshni yengadi.\n\n/resume — o‘yinni davom ettirish. Yangi o‘yin boshlasangiz oldingisi almashtiriladi. Ballar faqat o‘yin uchun.')

def main():
    if not TOKEN:
        logging.info('BOT_TOKEN kiritilishini kutmoqda. Railway Variables ga BOT_TOKEN qo‘shing.')
        while True: time.sleep(30)
    api('getMe')
    api('deleteWebhook',drop_pending_updates=False)
    api('setMyCommands',commands=[{'command':'start','description':'O‘yinlar menyusi'},{'command':'resume','description':'O‘yinni davom ettirish'}])
    row=db.execute("SELECT value FROM meta WHERE key='offset'").fetchone(); offset=row[0] if row else 0
    logging.info('GameHub started')
    while True:
        try:
            updates=api('getUpdates',offset=offset,timeout=25,allowed_updates=['message','callback_query'])
            for u in updates:
                try: handle(u)
                except Exception as e:
                    logging.error('Update failed: %s',type(e).__name__)
                offset=u['update_id']+1
                db.execute("INSERT OR REPLACE INTO meta VALUES('offset',?)",(offset,)); db.commit()
        except Exception as e:
            logging.error('Polling failed: %s',type(e).__name__)
            time.sleep(5)

if __name__=='__main__': main()

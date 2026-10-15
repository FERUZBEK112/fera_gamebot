"""Fera GameHub: Telegram bot + secure Mini App web server."""
import hashlib
import hmac
import json
import logging
import mimetypes
import os
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = os.getenv("ADMIN_ID", "")
APP_URL = os.getenv("APP_URL", "").rstrip("/")
BOT_USERNAME = os.getenv("BOT_USERNAME", "fera_gamesbot").lstrip("@")
PORT = int(os.getenv("PORT", "8080"))
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
WEB_DIR = Path(__file__).parent / "web"
DB_PATH = DATA_DIR / "games.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_GAMES = {"uno": 200, "mafia": 250, "rps": 60, "reflex": 350, "math": 200, "quiz": 200}


def db_connect():
    con = sqlite3.connect(DB_PATH, timeout=20)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db_connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, name TEXT NOT NULL DEFAULT 'O‘yinchi',
            wins INTEGER NOT NULL DEFAULT 0, played INTEGER NOT NULL DEFAULT 0
        )""")
        columns = {row["name"] for row in con.execute("PRAGMA table_info(users)")}
        if "username" not in columns:
            con.execute("ALTER TABLE users ADD COLUMN username TEXT NOT NULL DEFAULT ''")
        if "score" not in columns:
            con.execute("ALTER TABLE users ADD COLUMN score INTEGER NOT NULL DEFAULT 0")
        if "stars_milli" not in columns:
            con.execute("ALTER TABLE users ADD COLUMN stars_milli INTEGER NOT NULL DEFAULT 0")
        con.execute("""CREATE TABLE IF NOT EXISTS results(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            game TEXT NOT NULL, won INTEGER NOT NULL, score INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_results_user ON results(user_id)")
        con.execute("""CREATE TABLE IF NOT EXISTS referrals(
            invited_id INTEGER PRIMARY KEY, inviter_id INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_referrals_inviter ON referrals(inviter_id)")
        con.commit()


def telegram_api(method, **data):
    request = urllib.request.Request(
        "https://api.telegram.org/bot" + TOKEN + "/" + method,
        json.dumps(data, ensure_ascii=False).encode(),
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        payload = json.load(response)
    if not payload.get("ok"):
        raise RuntimeError("Telegram rejected " + method)
    return payload["result"]


def upsert_user(user):
    uid = int(user["id"])
    name = (str(user.get("first_name", "")) + (" " + str(user.get("last_name", "")) if user.get("last_name") else "")).strip()[:80] or "O‘yinchi"
    username = ("@" + str(user["username"]))[:80] if user.get("username") else ""
    with db_connect() as con:
        con.execute(
            """INSERT INTO users(id,name,username) VALUES(?,?,?)
               ON CONFLICT(id) DO UPDATE SET name=excluded.name,username=excluded.username""",
            (uid, name, username),
        )
        con.commit()
    return uid


def register_referral(invited_id, inviter_id):
    """Credit one verified Telegram user once. Returns True on a new referral."""
    if invited_id == inviter_id:
        return False
    with db_connect() as con:
        inviter = con.execute("SELECT id FROM users WHERE id=?", (inviter_id,)).fetchone()
        if not inviter:
            return False
        cursor = con.execute(
            "INSERT OR IGNORE INTO referrals(invited_id,inviter_id,created_at) VALUES(?,?,?)",
            (invited_id, inviter_id, int(time.time())),
        )
        if cursor.rowcount != 1:
            return False
        con.execute("UPDATE users SET stars_milli=stars_milli+500 WHERE id=?", (inviter_id,))
        con.commit()
    return True


def validate_init_data(raw):
    if not TOKEN or not raw or len(raw) > 8192:
        return None
    try:
        pairs = dict(urllib.parse.parse_qsl(raw, keep_blank_values=True))
        received_hash = pairs.pop("hash")
        auth_date = int(pairs.get("auth_date", "0"))
        if abs(int(time.time()) - auth_date) > 86400:
            return None
        data_check = "\n".join(key + "=" + pairs[key] for key in sorted(pairs))
        secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
        calculated = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(received_hash, calculated):
            return None
        user = json.loads(pairs.get("user", "{}"))
        if not isinstance(user, dict) or not user.get("id"):
            return None
        return user
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return None


class Handler(BaseHTTPRequestHandler):
    server_version = "FeraGameHub/2.0"

    def log_message(self, fmt, *args):
        logging.info("web %s", fmt % args)

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def current_user(self):
        return validate_init_data(self.headers.get("X-Telegram-Init-Data", ""))

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/health":
            return self.send_json(200, {"ok": True, "service": "fera-gamehub"})
        if path == "/api/profile":
            user = self.current_user()
            if not user:
                return self.send_json(401, {"ok": False})
            uid = upsert_user(user)
            with db_connect() as con:
                row = con.execute(
                    "SELECT id,name,username,score,wins,played,stars_milli FROM users WHERE id=?", (uid,)
                ).fetchone()
                referrals = con.execute(
                    "SELECT COUNT(*) AS c FROM referrals WHERE inviter_id=?", (uid,)
                ).fetchone()["c"]
            data = dict(row)
            data["stars"] = data.pop("stars_milli", 0) / 1000
            data["referrals"] = referrals
            return self.send_json(200, {"ok": True, "user": data})
        if path == "/api/referral":
            user = self.current_user()
            if not user:
                return self.send_json(401, {"ok": False})
            uid = upsert_user(user)
            with db_connect() as con:
                row = con.execute("SELECT stars_milli FROM users WHERE id=?", (uid,)).fetchone()
                friends = con.execute(
                    """SELECT u.name,u.username,r.created_at FROM referrals r
                       JOIN users u ON u.id=r.invited_id
                       WHERE r.inviter_id=? ORDER BY r.created_at DESC LIMIT 30""",
                    (uid,),
                ).fetchall()
            return self.send_json(200, {
                "ok": True,
                "stars": int(row["stars_milli"]) / 1000,
                "count": len(friends),
                "link": "https://t.me/" + BOT_USERNAME + "?start=ref_" + str(uid),
                "friends": [dict(friend) for friend in friends],
            })
        if path == "/api/leaderboard":
            user = self.current_user()
            if not user:
                return self.send_json(401, {"ok": False})
            upsert_user(user)
            with db_connect() as con:
                rows = con.execute(
                    "SELECT name,username,score,wins,played FROM users ORDER BY score DESC,wins DESC,played ASC LIMIT 20"
                ).fetchall()
            return self.send_json(200, {"ok": True, "users": [dict(row) for row in rows]})
        return self.serve_static(path)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path != "/api/result":
            return self.send_json(404, {"ok": False})
        user = self.current_user()
        if not user:
            return self.send_json(401, {"ok": False})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 2 or length > 4096:
                raise ValueError
            payload = json.loads(self.rfile.read(length))
            game = str(payload.get("game", ""))
            won = bool(payload.get("won", False))
            score = int(payload.get("score", 0))
            if game not in ALLOWED_GAMES:
                raise ValueError
            score = max(0, min(score, ALLOWED_GAMES[game]))
        except (ValueError, TypeError, json.JSONDecodeError):
            return self.send_json(400, {"ok": False, "error": "invalid_result"})
        uid = upsert_user(user)
        now = int(time.time())
        with db_connect() as con:
            recent = con.execute(
                "SELECT created_at FROM results WHERE user_id=? AND game=? ORDER BY id DESC LIMIT 1",
                (uid, game),
            ).fetchone()
            if recent and now - int(recent["created_at"]) < 2:
                return self.send_json(429, {"ok": False, "error": "too_fast"})
            con.execute(
                "INSERT INTO results(user_id,game,won,score,created_at) VALUES(?,?,?,?,?)",
                (uid, game, int(won), score, now),
            )
            con.execute(
                "UPDATE users SET score=score+?,wins=wins+?,played=played+1 WHERE id=?",
                (score, int(won), uid),
            )
            row = con.execute("SELECT score,wins,played FROM users WHERE id=?", (uid,)).fetchone()
            con.commit()
        return self.send_json(200, {"ok": True, "stats": dict(row)})

    def serve_static(self, path):
        requested = "index.html" if path in ("", "/") else path.lstrip("/")
        candidate = (WEB_DIR / requested).resolve()
        try:
            candidate.relative_to(WEB_DIR.resolve())
        except ValueError:
            return self.send_json(403, {"ok": False})
        if not candidate.is_file():
            candidate = WEB_DIR / "index.html"
        body = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type + ("; charset=utf-8" if content_type.startswith(("text/", "application/javascript")) else ""))
        self.send_header("Cache-Control", "no-cache" if candidate.name == "index.html" else "public,max-age=3600")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' https://telegram.org; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'; frame-ancestors https://web.telegram.org https://*.telegram.org")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_message(chat_id, first_name="O‘yinchi"):
    if not APP_URL:
        return telegram_api("sendMessage", chat_id=chat_id, text="GameHub hozir sozlanmoqda. Birozdan keyin /start bosing.")
    keyboard = {"inline_keyboard": [[{"text": "🎮 OPEN GAMEHUB", "web_app": {"url": APP_URL}}]]}
    text = (
        "🎮 FERA GAMEHUB\n\n"
        "Salom, " + first_name + "! UNO, Mafia va boshqa o‘yinlar yangi Mini App ichida.\n\n"
        "Pastdagi tugmani bosing 👇"
    )
    return telegram_api("sendMessage", chat_id=chat_id, text=text, reply_markup=keyboard)


def handle_update(update):
    message = update.get("message")
    if not message or message.get("chat", {}).get("type") != "private":
        return
    user = message.get("from", {})
    uid = upsert_user(user) if user.get("id") else None
    text = message.get("text", "")
    chat_id = message["chat"]["id"]
    parts = text.split(maxsplit=1)
    command = parts[0].split("@", 1)[0] if parts else ""
    referral_added = False
    if command == "/start" and len(parts) > 1 and parts[1].startswith("ref_") and uid:
        try:
            inviter_id = int(parts[1][4:])
            referral_added = register_referral(uid, inviter_id)
            if referral_added:
                telegram_api(
                    "sendMessage",
                    chat_id=inviter_id,
                    text="🎉 Yangi do‘stingiz GameHub’ga qo‘shildi!\n\n⭐ +0.5 Game Stars hisobingizga yozildi.",
                )
        except (ValueError, TypeError):
            pass
    if command in ("/start", "/games"):
        first_name = user.get("first_name", "O‘yinchi")
        start_message(chat_id, first_name)
        if referral_added:
            telegram_api("sendMessage", chat_id=chat_id, text="✅ Taklif qabul qilindi. Endi o‘yinlardan birini tanlang!")
    elif command == "/admin" and str(user.get("id")) == ADMIN_ID:
        with db_connect() as con:
            users = con.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
            games = con.execute("SELECT COUNT(*) AS c FROM results").fetchone()["c"]
            referrals = con.execute("SELECT COUNT(*) AS c FROM referrals").fetchone()["c"]
        telegram_api(
            "sendMessage",
            chat_id=chat_id,
            text="🛠 Admin\n\nFoydalanuvchilar: %s\nO‘yinlar: %s\nTakliflar: %s" % (users, games, referrals),
        )
    else:
        start_message(chat_id, user.get("first_name", "O‘yinchi"))


def bot_loop():
    if not TOKEN:
        logging.warning("BOT_TOKEN missing; web-only mode")
        return
    try:
        me = telegram_api("getMe")
        telegram_api("deleteWebhook", drop_pending_updates=False)
        telegram_api(
            "setMyCommands",
            commands=[
                {"command": "start", "description": "GameHub’ni ochish"},
                {"command": "games", "description": "O‘yinlar"},
            ],
        )
        if APP_URL:
            telegram_api(
                "setChatMenuButton",
                menu_button={"type": "web_app", "text": "🎮 Open GameHub", "web_app": {"url": APP_URL}},
            )
        logging.info("Telegram bot ready: @%s", me.get("username", "bot"))
    except Exception as exc:
        logging.error("Telegram setup failed: %s", type(exc).__name__)
        return
    offset = 0
    while True:
        try:
            updates = telegram_api("getUpdates", offset=offset, timeout=25, allowed_updates=["message"])
            for update in updates:
                try:
                    handle_update(update)
                except Exception as exc:
                    logging.error("Update failed: %s", type(exc).__name__)
                offset = update["update_id"] + 1
        except Exception as exc:
            logging.error("Polling retry: %s", type(exc).__name__)
            time.sleep(5)


def main():
    init_db()
    threading.Thread(target=bot_loop, daemon=True, name="telegram-polling").start()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    logging.info("Fera GameHub web server listening on %s", PORT)
    server.serve_forever()


if __name__ == "__main__":
    main()

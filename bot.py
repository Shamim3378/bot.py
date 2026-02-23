import telebot
from telebot import types
import sqlite3
import os

# ===== CONFIG =====
API_TOKEN = "8571582464:AAGo9qpy3txqMFNaJMgqi2pWMardgRy>
ADMIN_ID = 5857683487
BIKASH_NUMBER = "01605653378"
PRICE_PER_MAIL = 1
SUPPORT_URL = "https://t.me/FSBD_ADMIN_2"
MINIMUM_ADD_AMOUNT = 20
LOW_STOCK_ALERT = 10

bot = telebot.TeleBot(API_TOKEN)

# ===== DATABASE =====
def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users(us>
    cursor.execute("CREATE TABLE IF NOT EXISTS stock(ma>
    cursor.execute("CREATE TABLE IF NOT EXISTS waitlist>
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            trx_id TEXT UNIQUE,
            amount REAL,
            status TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS stats(to>

    cursor.execute("INSERT OR IGNORE INTO stats(rowid,t>
    conn.commit()
    conn.close()

init_db()

# ===== MENU =====
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=>
    markup.add("📧 Buy Mail", "💰 Add Balance")
    markup.add("💳 Balance", "📞 Support")
    return markup

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
cursor.execute("INSERT OR IGNORE INTO users(user_id>
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id,
        f"👋 HOTMAIL BUY BOT-এ স্বাগতম!\n\n🔥 প্রতিটি হটম>
        reply_markup=main_menu())

# ===== BUY MAIL =====
@bot.message_handler(func=lambda m: m.text == "📧 Buy M>
def buy_mail(message):
    msg = bot.send_message(message.chat.id, f"প্রতিটি {P>
    bot.register_next_step_handler(msg, process_purchas>

def process_purchase(message):
    try:
        count = int(message.text)
        user_id = message.from_user.id

        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM stock")
        stock = cursor.fetchone()[0]

        if stock < count:
            bot.send_message(user_id, "❌ পর্যাপ্ত স্টক নে>
            conn.close()
            return

        cursor.execute("SELECT balance FROM users WHERE>
        balance = cursor.fetchone()[0]
        total = count * PRICE_PER_MAIL

        if balance < total:
            bot.send_message(user_id, f"❌ ব্যালেন্স নেই।>
            conn.close()
            return

        cursor.execute("SELECT rowid, mail_data FROM st>
        mails = cursor.fetchall()

        file_name = f"mails_{user_id}.txt"
        with open(file_name, "w") as f:
            for m in mails:
                f.write(m[1] + "\n")

        with open(file_name, "rb") as f:
            bot.send_document(user_id, f)

        cursor.execute("UPDATE users SET balance = bala>

        for m in mails:
cursor.execute("DELETE FROM stock WHERE row>

        # Update Profit
        cursor.execute("UPDATE stats SET total_profit =>
                       (total, count))

        # Low Stock Alert
        cursor.execute("SELECT COUNT(*) FROM stock")
        remaining = cursor.fetchone()[0]
        if remaining <= LOW_STOCK_ALERT:
            bot.send_message(ADMIN_ID, f"⚠️ Low Stock Al>

        conn.commit()
        conn.close()
        os.remove(file_name)

    except:
        bot.send_message(message.chat.id, "সঠিক সংখ্যা ল>

# ===== BALANCE =====
@bot.message_handler(func=lambda m: m.text == "💳 Balan>
def balance(message):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE use>
    result = cursor.fetchone()
    conn.close()
    bal = result[0] if result else 0
    bot.send_message(message.chat.id, f"💰 আপনার বর্তমান>

# ===== ADD BALANCE =====
@bot.message_handler(func=lambda m: m.text == "💰 Add B>
def add_balance(message):
    bot.send_message(message.chat.id,
        f"💳 বিকাশ নম্বর: {BIKASH_NUMBER}\n\n"
        f"সেন্ড মানি করে TRX ID দিন।\n"
        f"⚠️ Minimum Add: {MINIMUM_ADD_AMOUNT} টাকা")

    msg = bot.send_message(message.chat.id, "আপনি কত টা>
    bot.register_next_step_handler(msg, process_amount)


def process_amount(message):
    try:
        amount = float(message.text)

        if amount < MINIMUM_ADD_AMOUNT:
            bot.send_message(message.chat.id,
                             f"❌ Minimum {MINIMUM_ADD_>
            return

        user_data = {"amount": amount}
msg = bot.send_message(message.chat.id, "TRX ID>
        bot.register_next_step_handler(msg, process_trx>

    except:
        bot.send_message(message.chat.id, "❌ সঠিক পরিম>


def process_trx(message, user_data):
    trx_id = message.text
    user_id = message.from_user.id
    amount = user_data["amount"]

    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO transactions(user_i>
                       (user_id, trx_id, amount, "pendi>
        conn.commit()

        bot.send_message(message.chat.id,
                         "✅ আপনার রিকোয়েস্ট পাঠানো হয়েছ>

        # Notify Admin
        bot.send_message(ADMIN_ID,
                         f"💰 New Balance Request\n\n"
                         f"User: {user_id}\n"
                         f"Amount: {amount}\n"
                         f"TRX: {trx_id}\n\n"
                         f"/approve {trx_id}\n"
                         f"/decline {trx_id}")

    except:
        bot.send_message(message.chat.id, "❌ এই TRX আগ>

    conn.close()

# ===== APPROVE =====
@bot.message_handler(commands=['approve'])
def approve(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        trx_id = message.text.split()[1]

        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()

        cursor.execute("SELECT user_id,amount FROM tran>
                       (trx_id,))
        data = cursor.fetchone()
if not data:
            bot.send_message(message.chat.id, "❌ TRX প>
            conn.close()
            return

        user_id, amount = data

        cursor.execute("UPDATE users SET balance = bala>
                       (amount, user_id))

        cursor.execute("UPDATE transactions SET status=>
                       (trx_id,))

        conn.commit()
        conn.close()

        bot.send_message(user_id, f"✅ {amount} টাকা ব্য>
        bot.send_message(message.chat.id, "Approved Suc>

    except:
        bot.send_message(message.chat.id, "Usage: /appr>


# ===== DECLINE =====
@bot.message_handler(commands=['decline'])
def decline(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        trx_id = message.text.split()[1]

        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()

        cursor.execute("UPDATE transactions SET status=>
                       (trx_id,))
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, "❌ Declined >

    except:
        bot.send_message(message.chat.id, "Usage: /decl>

# ===== SUPPORT =====
@bot.message_handler(func=lambda m: m.text == "📞 Suppo>
def support(message):
    bot.send_message(message.chat.id,
                     f"📞 Support এর জন্য যোগাযোগ করুন:\n>

# ===== ADMIN PANEL =====
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=>
    markup.add("📦 Stock Count", "➕ Add Stock")
    markup.add("💰 Total Profit", "📜 Transactions")
    markup.add("👥 Total Users")
    markup.add("🔙 Back")

    bot.send_message(message.chat.id, "👑 Admin Panel",>

@bot.message_handler(func=lambda m: m.text == "📦 Stock>
def stock_count(message):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM stock")
    total = cursor.fetchone()[0]
    conn.close()
    bot.send_message(message.chat.id, f"📦 Current Stoc>

# ===== ADD STOCK BUTTON =====
@bot.message_handler(func=lambda m: m.text == "➕ Add S>
def add_stock(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "📂 একটি .txt ফাই>

# ===== RECEIVE TXT FILE =====
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.from_user.id != ADMIN_ID:
        return

    file_info = bot.get_file(message.document.file_id)

    if not file_info.file_path.endswith(".txt"):
        bot.send_message(message.chat.id, "❌ শুধু .txt ফ>
        return

    downloaded_file = bot.download_file(file_info.file_>

    file_name = "uploaded_stock.txt"
    with open(file_name, "wb") as f:
        f.write(downloaded_file)

    added = 0

    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
 with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            mail = line.strip()
            if mail:
                cursor.execute("INSERT INTO stock(mail_>
                added += 1

    conn.commit()
    conn.close()

    os.remove(file_name)

    bot.send_message(message.chat.id, f"✅ সফলভাবে {add>

@bot.message_handler(func=lambda m: m.text == "💰 Total>
def total_profit(message):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT total_profit,total_sales FRO>
    data = cursor.fetchone()
    conn.close()
    bot.send_message(message.chat.id,
        f"💰 Total Profit: {data[0]}\n📦 Total Sales: {>

@bot.message_handler(func=lambda m: m.text == "👥 Total>
def total_users(message):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    conn.close()
    bot.send_message(message.chat.id, f"👥 Total Users:>

@bot.message_handler(func=lambda m: m.text == "📜 Trans>
def transactions(message):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id,trx_id,amount,status>
    rows = cursor.fetchall()
    conn.close()

    text = "📜 Last 10 Transactions:\n\n"
    for r in rows:
        text += f"User: {r[0]}\nTRX: {r[1]}\nAmount: {r>

    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def back(message):
    bot.send_message(message.chat.id, "Main Menu", repl>

bot.polling(none_stop=True)

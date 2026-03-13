import telebot
from telebot import types
import requests
from flask import Flask
from threading import Thread
import os

# --- SERVER AYARI (Render Hatasını Çözen Kısım) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "WROX SYSTEM IS LIVE"

# --- BOT AYARLARI ---
# @BotFather'dan aldığın tokeni buraya yaz
API_TOKEN = '8515085006:AAHXt2yp7cg7DxljLMoAX4FOpw4b_QiwCOk' 
bot = telebot.TeleBot(API_TOKEN)
user_data = {}

# Workers API Linkleri
API_MAP = {
    'tc': 'https://tc.cvarysystem.workers.dev/?tc=',
    'tcpro': 'https://tcpro.cvarysystem.workers.dev/?tc=',
    'adsoyad': 'https://adsoyad.cvarysystem.workers.dev/?ad={ad}&soyad={soyad}',
    'adililce': 'https://adsoyad.cvarysystem.workers.dev/?ad={ad}&soyad={soyad}&il={il}&ilce={ilce}',
    'aile': 'https://aile.cvarysystem.workers.dev/?tc=',
    'ailepro': 'https://ailepro.cvarysystem.workers.dev/?tc=',
    'sulale': 'https://sulale.cvarysystem.workers.dev/?tc=',
    'soyagaci': 'https://soyagaci.cvarysystem.workers.dev/?tc=',
    'cocuk': 'https://cocuk.cvarysystem.workers.dev/?tc=',
    'es': 'https://es.cvarysystem.workers.dev/?tc=',
    'kardes': 'https://kardes.cvarysystem.workers.dev/?tc=',
    'adres': 'https://adres.cvarysystem.workers.dev/?tc=',
    'adrespro': 'https://adrespro.cvarysystem.workers.dev/?tc=',
    'tcgsm': 'https://tcgsm.cvarysystem.workers.dev/?tc=',
    'gsmtc': 'https://gsmtc.cvarysystem.workers.dev/?gsm=',
    'sgk': 'https://sgk.cvarysystem.workers.dev/?tc=',
    'sgk_arkadas': 'https://sgk-arkadas.cvarysystem.workers.dev/?tc=',
    'tapu': 'https://tapu.cvarysystem.workers.dev/?tc='
}

# --- BUTONLAR ---
def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 SORGULARI GÖSTER", callback_data="sorgu_listesi"))
    return markup

def query_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("🆔 TC Sorgu", callback_data="q_tc"),
        types.InlineKeyboardButton("👤 Ad Soyad", callback_data="q_adsoyad"),
        types.InlineKeyboardButton("📍 Ad Soyad İl İlçe", callback_data="q_adililce"),
        types.InlineKeyboardButton("👨‍👩‍👧‍👦 Aile Sorgu", callback_data="q_aile"),
        types.InlineKeyboardButton("📞 GSM -> TC", callback_data="q_gsmtc"),
        types.InlineKeyboardButton("🏢 SGK Sorgu", callback_data="q_sgk"),
        types.InlineKeyboardButton("📜 Tapu Sorgu", callback_data="q_tapu")
    ]
    markup.add(*btns)
    markup.add(types.InlineKeyboardButton("⬅️ ANA MENÜ", callback_data="back_to_main"))
    return markup

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "🔥 𝙒𝙍𝙊𝙓 𝙎𝙔𝙎𝙏𝙀𝙈𝙀 𝙃𝙊𝙎̧ 𝙂𝙀𝙇𝘿𝙄̇𝙉𝙄̇𝙕", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "back_to_main":
        bot.edit_message_text("🔥 𝙒𝙍𝙊𝙓 𝙎𝙔𝙎𝙏𝙀𝙈𝙀 𝙃𝙊𝙎̧ 𝙂𝙀𝙇𝘿𝙄̇𝙉𝙄̇𝙕", chat_id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "sorgu_listesi":
        bot.edit_message_text("👇 Sorgu Seçin:", chat_id, call.message.message_id, reply_markup=query_menu())
    elif call.data.startswith("q_"):
        q_type = call.data.replace("q_", "")
        user_data[chat_id] = {'type': q_type}
        
        if q_type in ["adsoyad", "adililce"]:
            msg = bot.send_message(chat_id, "👤 AD girin:")
            bot.register_next_step_handler(msg, step_ad)
        elif q_type == "gsmtc":
            msg = bot.send_message(chat_id, "📞 GSM No girin:")
            bot.register_next_step_handler(msg, step_final)
        else:
            msg = bot.send_message(chat_id, f"🆔 {q_type.upper()} için TC girin:")
            bot.register_next_step_handler(msg, step_final)

# Adım Adım Fonksiyonları
def step_ad(message):
    user_data[message.chat.id]['ad'] = message.text
    msg = bot.send_message(message.chat.id, "👤 SOYAD girin:")
    bot.register_next_step_handler(msg, step_soyad)

def step_soyad(message):
    chat_id = message.chat.id
    user_data[chat_id]['soyad'] = message.text
    if user_data[chat_id]['type'] == "adililce":
        msg = bot.send_message(chat_id, "📍 İL girin:")
        bot.register_next_step_handler(msg, step_il)
    else:
        d = user_data[chat_id]
        url = API_MAP['adsoyad'].format(ad=d['ad'], soyad=d['soyad'])
        api_call(chat_id, url)

def step_il(message):
    user_data[message.chat.id]['il'] = message.text
    msg = bot.send_message(message.chat.id, "🏙️ İLÇE girin:")
    bot.register_next_step_handler(msg, step_ilce)

def step_ilce(message):
    chat_id = message.chat.id
    d = user_data[chat_id]
    url = API_MAP['adililce'].format(ad=d['ad'], soyad=d['soyad'], il=d['il'], ilce=message.text)
    api_call(chat_id, url)

def step_final(message):
    chat_id = message.chat.id
    url = API_MAP[user_data[chat_id]['type']] + message.text
    api_call(chat_id, url)

def api_call(chat_id, final_url):
    bot.send_message(chat_id, "⏳ Sorgulanıyor...")
    try:
        r = requests.get(final_url, timeout=30)
        bot.send_message(chat_id, f"🔍 *SONUÇLAR:*\n\n`{r.text}`", parse_mode="Markdown", reply_markup=main_menu())
    except:
        bot.send_message(chat_id, "❌ API Hatası.", reply_markup=main_menu())

# --- ÇALIŞTIRMA ---
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()

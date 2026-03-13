import telebot
from telebot import types
import requests
from flask import Flask, render_template_string
from threading import Thread

# --- AYARLAR ---
API_TOKEN = '8515085006:AAHXt2yp7cg7DxljLMoAX4FOpw4b_QiwCOk'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- TÜM API LİSTESİ ---
API_MAP = {
    'tc': 'https://tc.cvarysystem.workers.dev/?tc=',
    'tcpro': 'https://tcpro.cvarysystem.workers.dev/?tc=',
    'adililce': 'https://adsoyad.cvarysystem.workers.dev/?ad={ad}&soyad={soyad}&il={il}&ilce={ilce}',
    'sulale': 'https://sulale.cvarysystem.workers.dev/?tc=',
    'soyagaci': 'https://soyagaci.cvarysystem.workers.dev/?tc=',
    'aile': 'https://aile.cvarysystem.workers.dev/?tc=',
    'ailepro': 'https://ailepro.cvarysystem.workers.dev/?tc=',
    'adres': 'https://adres.cvarysystem.workers.dev/?tc=',
    'adrespro': 'https://adrespro.cvarysystem.workers.dev/?tc=',
    'tcgsm': 'https://tcgsm.cvarysystem.workers.dev/?tc=',
    'gsmtc': 'https://gsmtc.cvarysystem.workers.dev/?gsm=',
    'cocuk': 'https://cocuk.cvarysystem.workers.dev/?tc=',
    'es': 'https://es.cvarysystem.workers.dev/?tc=',
    'kardes': 'https://kardes.cvarysystem.workers.dev/?tc=',
    'sgk': 'https://sgk.cvarysystem.workers.dev/?tc=',
    'sgk_arkadas': 'https://sgk-arkadas.cvarysystem.workers.dev/?tc=',
    'tapu': 'https://tapu.cvarysystem.workers.dev/?tc='
}

user_data = {}

# --- WEB PANEL TASARIMI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WROX SYSTEM PANEL</title>
    <style>
        body { background: #000; color: #ff0000; font-family: 'Courier New', monospace; text-align: center; }
        .box { max-width: 600px; margin: 40px auto; border: 2px solid #ff0000; padding: 20px; border-radius: 10px; box-shadow: 0 0 20px #ff0000; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }
        .item { background: #111; border: 1px solid #444; padding: 10px; color: #fff; font-size: 0.8em; }
        a { color: #000; background: #ff0000; padding: 15px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>WROX SYSTEM</h1>
        <div class="grid">
            <div class="item">🆔 TC & PRO</div><div class="item">📍 AD SOYAD İL İLÇE</div>
            <div class="item">👨‍👩‍👧‍👦 AİLE & PRO</div><div class="item">🌳 SOYAĞACI & SÜLALE</div>
            <div class="item">🏠 ADRES & PRO</div><div class="item">📞 GSM & SGK</div>
        </div>
        <a href="https://t.me/WROXSYSTEMBOT">BOTU BAŞLAT</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

# --- BOT İŞLEMLERİ ---

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 SORGULAR", callback_data="sorgu_listesi"))
    bot.send_message(m.chat.id, "𝙒𝙍𝙊𝙓 𝙎𝙔𝙎𝙏𝙀𝙈𝙀 𝙃𝙊𝙎̧ 𝙂𝙀𝙇𝘿𝙄̇𝙉𝙄̇𝙕", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    cid = c.message.chat.id
    if c.data == "sorgu_listesi":
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            types.InlineKeyboardButton("🆔 TC", callback_data="b_tc"),
            types.InlineKeyboardButton("💎 TC PRO", callback_data="b_tcpro"),
            types.InlineKeyboardButton("📍 AD SOYAD İL/İLÇE", callback_data="b_adililce"),
            types.InlineKeyboardButton("🌳 SÜLALE", callback_data="b_sulale"),
            types.InlineKeyboardButton("📜 SOYAĞACI", callback_data="b_soyagaci"),
            types.InlineKeyboardButton("👨‍👩‍👧‍👦 AİLE", callback_data="b_aile"),
            types.InlineKeyboardButton("🔥 AİLE PRO", callback_data="b_ailepro"),
            types.InlineKeyboardButton("🏠 ADRES", callback_data="b_adres"),
            types.InlineKeyboardButton("🏰 ADRES PRO", callback_data="b_adrespro"),
            types.InlineKeyboardButton("📲 TC -> GSM", callback_data="b_tcgsm"),
            types.InlineKeyboardButton("📞 GSM -> TC", callback_data="b_gsmtc"),
            types.InlineKeyboardButton("👶 ÇOCUK", callback_data="b_cocuk"),
            types.InlineKeyboardButton("💍 EŞ", callback_data="b_es"),
            types.InlineKeyboardButton("👫 KARDEŞ", callback_data="b_kardes"),
            types.InlineKeyboardButton("🏢 SGK", callback_data="b_sgk"),
            types.InlineKeyboardButton("👥 SGK ARKADAŞ", callback_data="b_sgk_arkadas"),
            types.InlineKeyboardButton("📑 TAPU", callback_data="b_tapu")
        )
        bot.edit_message_text("👇 Sorgu Kategorisi Seçiniz:", cid, c.message.message_id, reply_markup=m)
    
    elif c.data.startswith("b_"):
        act = c.data.split("_")[1]
        user_data[cid] = {'action': act, 'step': 1}
        
        # Her sorgunun kendine özel ilk sorusu
        sorular = {
            'tc': "🆔 Sorgulanacak *TC NUMARASI* giriniz:",
            'tcpro': "💎 Sorgulanacak *PRO TC NUMARASI* giriniz:",
            'adililce': "👤 Sorgulama başladı.\n\nLütfen kişinin **ADINI** giriniz:",
            'sulale': "🌳 Sülale sorgusu için *TC NUMARASI* giriniz:",
            'soyagaci': "📜 Soyağacı sorgusu için *TC NUMARASI* giriniz:",
            'aile': "👨‍👩‍👧‍👦 Aile sorgusu için *TC NUMARASI* giriniz:",
            'ailepro': "🔥 Aile PRO sorgusu için *TC NUMARASI* giriniz:",
            'adres': "🏠 Adres sorgusu için *TC NUMARASI* giriniz:",
            'adrespro': "🏰 Adres PRO sorgusu için *TC NUMARASI* giriniz:",
            'tcgsm': "📲 GSM bulmak için *TC NUMARASI* giriniz:",
            'gsmtc': "📞 TC bulmak için *GSM NUMARASI* giriniz (Örn: 505...):",
            'cocuk': "👶 Çocuk sorgusu için *TC NUMARASI* giriniz:",
            'es': "💍 Eş sorgusu için *TC NUMARASI* giriniz:",
            'kardes': "👫 Kardeş sorgusu için *TC NUMARASI* giriniz:",
            'sgk': "🏢 SGK sorgusu için *TC NUMARASI* giriniz:",
            'sgk_arkadas': "👥 SGK Arkadaş sorgusu için *TC NUMARASI* giriniz:",
            'tapu': "📑 Tapu sorgusu için *TC NUMARASI* giriniz:"
        }
        bot.send_message(cid, sorular[act], parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle(m):
    cid = m.chat.id
    if cid not in user_data: return
    d = user_data[cid]
    
    # AD SOYAD İL İLÇE SIRALI SORU SİSTEMİ
    if d['action'] == "adililce":
        if d['step'] == 1:
            user_data[cid]['ad'] = m.text
            user_data[cid]['step'] = 2
            bot.send_message(cid, "👤 Şimdi kişinin **SOYADINI** giriniz:")
        elif d['step'] == 2:
            user_data[cid]['soyad'] = m.text
            user_data[cid]['step'] = 3
            bot.send_message(cid, "🏙️ Şimdi kişinin yaşadığı **İLİ** giriniz:")
        elif d['step'] == 3:
            user_data[cid]['il'] = m.text
            user_data[cid]['step'] = 4
            bot.send_message(cid, "🏘️ Son olarak kişinin yaşadığı **İLÇEYİ** giriniz:")
        elif d['step'] == 4:
            user_data[cid]['ilce'] = m.text
            run_q(cid)
    else:
        # Diğer tek adımlı sorgular
        user_data[cid]['val'] = m.text
        run_q(cid)

def run_q(cid):
    bot.send_message(cid, "🔄 *WROX Verileri Çekiyor...*", parse_mode="Markdown")
    d = user_data[cid]
    try:
        if d['action'] == "adililce":
            url = API_MAP['adililce'].format(ad=d['ad'], soyad=d['soyad'], il=d['il'], ilce=d['ilce'])
        else:
            url = API_MAP[d['action']] + d['val']
        
        res = requests.get(url, timeout=15).json()
        out = "✅ *𝙎𝙊𝙉𝙐𝘾̧𝙇𝘼𝙍*\n" + "─" * 15 + "\n"
        
        if isinstance(res, list):
            if len(res) == 0:
                bot.send_message(cid, "❌ Sonuç bulunamadı.")
                return
            for i in res:
                for k, v in i.items(): out += f"🔹 *{k.upper()}:* `{v}`\n"
                out += "─" * 10 + "\n"
        elif isinstance(res, dict):
            for k, v in res.items(): out += f"🔹 *{k.upper()}:* `{v}`\n"
        else:
            out += f"📝 *VERİ:* `{res}`"

        bot.send_message(cid, out + "\n👑 *WROX SYSTEM*", parse_mode="Markdown")
    except:
        bot.send_message(cid, "❌ Bir hata oluştu veya sonuç bulunamadı.")
    
    del user_data[cid]

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()

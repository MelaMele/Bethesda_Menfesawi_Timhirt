import os
import json
import random
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
CRON_SECRET = os.environ.get("CRON_SECRET")

# ዌብሳይቱን ዝም ብለን ስንከፍተው የሚመጣ ገጽ (ለሰላምታ)
@app.route('/')
def home():
    return jsonify({"status": "healthy", "message": "ቤተሳይዳ መንፈሳዊ አገልግሎት በሰላም እየሰራ ነው!"})

# ክሮን ጆቡ የሚጠራው ዋናው የትምህርት መለቀቂያ መስመር
@app.route('/api/post_scheduler', methods=['GET', 'POST'])
def post_to_channel():
    auth_header = request.headers.get('Authorization')
    if CRON_SECRET and auth_header != f"Bearer {CRON_SECRET}":
        return jsonify({"status": "unauthorized", "message": "ደህንነትዎ አልተረጋገጠም!"}), 401

    try:
        with open('contents.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        lesson = random.choice(data['teachings'])
        
        telegram_message = (
            f"⛪️ **{lesson['category']}** ⛪️\n\n"
            f"📖 **{lesson['title']}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"{lesson['body']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"✨ *{lesson['closing']}*\n\n"
            f"🔔 ይቀላቀሉ፦ {CHANNEL_ID}"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": telegram_message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "ትምህርቱ በስኬት ተለጥፏል!"}), 200
        else:
            return jsonify({"status": "failed", "error": response.text}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()

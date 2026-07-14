import os
import json
import random
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# ከVercel Environment Variables የሚነበቡ ሚስጥራዊ ቁልፎች
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID") # ለምሳሌ፡ @Bethesda_Menfesawi

@app.route('/api/post_scheduler', methods=['GET', 'POST'])
def post_to_channel():
    try:
        # የJSON ፋይሉን ማንበብ
        with open('contents.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # አንድ ትምህርት በዘፈቀደ መምረጥ (በኋላ ላይ እንደ ቀኑ መቁጠሪያ እንዲመርጥ እናደርገዋለን)
        lesson = random.choice(data['teachings'])
        
        # መልእክቱን በኦርቶዶክሳዊ ውበት ማዘጋጀት
        telegram_message = (
            f"⛪️ **{lesson['category']}** ⛪️\n\n"
            f"📖 **{lesson['title']}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"{lesson['body']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"✨ *{lesson['closing']}*\n\n"
            f"🔔 ይቀላቀሉ፦ {CHANNEL_ID}"
        )
        
        # ወደ ቴሌግራም መላክ
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

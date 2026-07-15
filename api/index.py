import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

# የቴሌግራም ተለዋዋጮች
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
CHANNEL_USERNAME = os.environ.get("TELEGRAM_CHANNEL_USERNAME", "@Bethesda_Menfesawi")

def get_sermon_from_json():
    """ 
    በጊትሃብ ካለው 'sermons.json' ፋይል ውስጥ እንደ ሰዓቱ አቆጣጠር 
    የተለያየውን ትምህርት መርጦ የሚያወጣ ቀመር
    """
    try:
        # የፋይሉን መገኛ በትክክል መፈለግ
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'sermons.json')
        # ፋይሉ በ root directory ውስጥ ካለ ደግሞ ወደ ላይ አንድ ደረጃ ወጥቶ እንዲፈልግ
        if not os.path.exists(json_path):
            json_path = os.path.join(os.path.dirname(base_dir), 'sermons.json')
            
        # ፋይሉን ከፍቶ ማንበብ (በ UTF-8 አማርኛ እንዳይበላሽ)
        with open(json_path, 'r', encoding='utf-8') as f:
            sermons = json.load(f)
            
        if not sermons:
            return None
            
        # በየ 30 ደቂቃው የተለያየ ኢንዴክስ (Index) ማስላት
        now = datetime.utcnow() + timedelta(hours=3) # የኢትዮጵያ ሰዓት
        slot_index = (now.hour * 2) + (1 if now.minute >= 30 else 0)
        sermon_idx = slot_index % len(sermons)
        
        return sermons[sermon_idx]
    except Exception as e:
        print(f"JSON Loading Error: {e}")
        return None

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # -------------------------------------------------------------
    # ፩. የቦቱ ዌብሁክ (ለሰዎች የግል ጥያቄ መልስ ለመስጠት)
    # -------------------------------------------------------------
    if 'webhook' in path or path == 'api/webhook':
        try:
            update = request.get_json(force=True, silent=True) or {}
            if "message" in update:
                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text.startswith("/start"):
                    welcome = (
                        "⛪️ **እንኳን ወደ ቤተሳይዳ መንፈሳዊ ቦት በደህና መጡ!** ⛪️\n\n"
                        "ይህ ቦት የግል መንፈሳዊ ጥያቄዎችን ለመመለስ የተዘጋጀ ረዳት ነው። "
                        "የሚፈልጉትን ማንኛውንም ጥያቄ እዚህ መጻፍ ይችላሉ።\n\n"
                        "📢 **ማሳሰቢያ፦** ዕለታዊ ሰፊ ትምህርቶችንና ስብከቶችን ለማንበብ እባክዎ ዋናውን ቻናላችንን ይቀላቀሉ!"
                    )
                    
                    if CHANNEL_USERNAME.startswith("http"):
                        channel_url = CHANNEL_USERNAME
                    else:
                        channel_url = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"

                    reply_markup = {
                        "inline_keyboard": [[{"text": "🔔 ቻናላችንን ለመቀላቀል", "url": channel_url}]]
                    }
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                        "chat_id": chat_id, "text": welcome, "parse_mode": "Markdown", "reply_markup": reply_markup
                    })
                
                elif text:
                    reply_text = (
                        "✨ **የእውቀትና የጥያቄ ማዕድ** ✨\n"
                        "━━━━━━━━━━━━━━━━━━━\n"
                        f"ስለ ጠየቁት ርዕስ (*{text}*) በጥናቱ ላይ እንገኛለን።\n\n"
                        "ጥያቄዎ እጅግ ጠቃሚና የሚያንጽ ነው። በቅርቡ በሊቃውንት አንድምታ አደራጅተን እንልክልዎታለን።"
                    )
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                        "chat_id": chat_id, "text": reply_text, "parse_mode": "Markdown"
                    })
            return jsonify({"status": "success"}), 200
        except:
            return jsonify({"status": "error"}), 500

    # -------------------------------------------------------------
    # ፪. የሰዓት መቆጣጠሪያ መስመር (Cron Job) -> ለቻናሉ ብቻ ፖስት ያደርጋል
    # -------------------------------------------------------------
    elif 'post_scheduler' in path or path == 'api/post_scheduler':
        return post_to_channel_only()
    
    return jsonify({"status": "active", "engine": "Bethesda Serverless JSON Engine"})

def post_to_channel_only():
    """ በየ 30 ደቂቃው ከ JSON ፋይል እየሳበ ቻናሉ ላይ ብቻ ይለጥፋል """
    try:
        sermon = get_sermon_from_json()
        if not sermon:
            return jsonify({"status": "error", "message": "No sermons found in JSON file"}), 404
        
        channel_message = (
            f"⛪️ **{sermon['category']}** ⛪️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📖 **{sermon['title']}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{sermon['body']}\n\n"
            f"{sermon['theological_depth']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{sermon['quote']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔔 ለማንበብና ለመማር ቻናላችንን ይቀላቀሉ፦ {"@BeenteSmaMariam_bot}"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": channel_message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        res = requests.post(url, json=payload)
        return jsonify({"status": "channel_posted_successfully", "telegram_response": res.json()}), 200
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()

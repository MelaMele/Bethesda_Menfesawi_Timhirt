import os
import json
import html  # የኤችቲኤምኤል ምልክቶችን ሴፍ ለማድረግ
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
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'sermons.json')
        
        if not os.path.exists(json_path):
            json_path = os.path.join(os.path.dirname(base_dir), 'sermons.json')
            
        with open(json_path, 'r', encoding='utf-8') as f:
            sermons = json.load(f)
            
        if not sermons:
            return None
            
        # በየ 30 ደቂቃው የተለያየ ኢንዴክስ (Index) ማስላት
        now = datetime.utcnow() + timedelta(hours=3) # የኢትዮጵያ ሰዓት
        
        # 🔄 በየቀኑ ተመሳሳይ ሰዓት ላይ ተመሳሳይ ፖስት እንዳይደገም ቀኑንም ማካተት ይቻላል (አማራጭ)
        # slot_index = (now.day * 48) + (now.hour * 2) + (1 if now.minute >= 30 else 0)
        
        slot_index = (now.hour * 2) + (1 if now.minute >= 30 else 0)
        sermon_idx = slot_index % len(sermons)
        
        return sermons[sermon_idx]
    except Exception as e:
        print(f"JSON Loading Error: {e}")
        return None

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # አካባቢ ተለዋዋጮችን ቀድሞ ማረጋገጥ
    if not TOKEN:
        return jsonify({"status": "error", "message": "Bot token is missing in server configuration"}), 500

    # -------------------------------------------------------------
    # ፩. የቦቱ ዌብሁክ (ለሰዎች የግል ጥያቄ መልስ ለመስጠት)
    # -------------------------------------------------------------
    if 'webhook' in path or path == 'api/webhook':
        try:
            update = request.get_json(force=True, silent=True) or {}
            if "message" in update:
                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "").strip()

                if text.startswith("/start"):
                    welcome = (
                        "⛪️ <b>እንኳን ወደ ቤተሳይዳ መንፈሳዊ ቦት በደህና መጡ!</b> ⛪️\n\n"
                        "ይህ ቦት የግል መንፈሳዊ ጥያቄዎችን ለመመለስ የተዘጋጀ ረዳት ነው። "
                        "የሚፈልጉትን ማንኛውንም ጥያቄ እዚህ መጻፍ ይችላሉ።\n\n"
                        "📢 <b>ማሳሰቢያ፦</b> ዕለታዊ ሰፊ ትምህርቶችንና ስብከቶችን ለማንበብ እባክዎ ዋናውን ቻናላችንን ይቀላቀሉ!"
                    )
                    
                    if CHANNEL_USERNAME.startswith("http"):
                        channel_url = CHANNEL_USERNAME
                    else:
                        channel_url = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"

                    reply_markup = {
                        "inline_keyboard": [[{"text": "🔔 ቻናላችንን ለመቀላቀል", "url": channel_url}]]
                    }
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                        "chat_id": chat_id, "text": welcome, "parse_mode": "HTML", "reply_markup": reply_markup
                    })
                
                elif text:
                    # የተጠቃሚውን ጽሑፍ HTML ደህንነቱ የተጠበቀ ማድረግ (escape)
                    safe_text = html.escape(text)
                    reply_text = (
                        "✨ <b>የእውቀትና የጥያቄ ማዕድ</b> ✨\n"
                        "━━━━━━━━━━━━━━━━━━━\n"
                        f"ስለ ጠየቁት ርዕስ (<b>{safe_text}</b>) በጥናቱ ላይ እንገኛለን።\n\n"
                        "ጥያቄዎ እጅግ ጠቃሚና የሚያንጽ ነው። በቅርቡ በሊቃውንት አንድምታ አደራጅተን እንልክልዎታለን።"
                    )
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                        "chat_id": chat_id, "text": reply_text, "parse_mode": "HTML"
                    })
            return jsonify({"status": "success"}), 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return jsonify({"status": "error"}), 500

    # -------------------------------------------------------------
    # ፪. የሰዓት መቆጣጠሪያ መስመር (Cron Job)
    # -------------------------------------------------------------
    elif 'post_scheduler' in path or path == 'api/post_scheduler':
        return post_to_channel_only()
    
    return jsonify({"status": "active", "engine": "Bethesda Serverless JSON Engine"})

def post_to_channel_only():
    """ በየ 30 ደቂቃው ከ JSON ፋይል እየሳበ ቻናሉ ላይ ብቻ ይለጥፋል """
    if not TOKEN or not CHANNEL_ID:
        return jsonify({"status": "error", "message": "Telegram Token or Channel ID config missing"}), 500

    try:
        sermon = get_sermon_from_json()
        if not sermon:
            return jsonify({"status": "error", "message": "No sermons found in JSON file"}), 404
        
        clean_channel = CHANNEL_USERNAME if CHANNEL_USERNAME.startswith("@") else f"@{CHANNEL_USERNAME}"
        
        # ⚠️ HTML parse mode በመጠቀማችን ፅሁፉ እንዳይበላሽ Bold ማድረጊያዎችን ወደ <b> ቀይረናል
        channel_message = (
            f"⛪️ <b>{html.escape(sermon['category'])}</b> ⛪️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📖 <b>{html.escape(sermon['title'])}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{sermon['body']}\n\n"  # በስብከቱ ውስጥ የራሱ HTML ካለ እንዳለ ያልፋል
            f"{sermon['theological_depth']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>{html.escape(sermon['quote'])}</i>\n"  # ጥቅሱን በ Italic (ማዘንበያ) አድርገነዋል
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📢 ቻናላችንን ይቀላቀሉ፦ {clean_channel}\n"
            f"💬 ለግል ጥያቄና አስተያየት ቦቱን ያነጋግሩ፦ @BeenteSmaMariam_bot"
        )
        
        payload = {
            "chat_id": CHANNEL_ID,
            "text": channel_message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        if "button_text" in sermon and "button_url" in sermon:
            payload["reply_markup"] = {
                "inline_keyboard": [[
                    {"text": sermon["button_text"], "url": sermon["button_url"]}
                ]]
            }
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        res = requests.post(url, json=payload)
        
        # ምላሹን ሎግ ማድረግ ችግሮችን ለመለየት ይረዳል
        telegram_res = res.json()
        if not telegram_res.get("ok"):
            print(f"Telegram API Error: {telegram_res}")
            return jsonify({"status": "failed_to_post", "telegram_response": telegram_res}), 400
            
        return jsonify({"status": "channel_posted_successfully", "telegram_response": telegram_res}), 200
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()

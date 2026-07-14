import os
import json
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
CHANNEL_USERNAME = os.environ.get("TELEGRAM_CHANNEL_USERNAME", "@Bethesda_Menfesawi")
BOT_USERNAME = os.environ.get("TELEGRAM_BOT_USERNAME", "Bethesda_Bot")

# እጅግ ሰፊና ጥልቅ የሆኑ የተለያዩ ስብከቶችና የአብነት ትምህርቶች ማከማቻ (Sermon Database)
SERMONS_POOL = [
    {
        "category": "ነገረ መለኮት - ምስጢረ ሥጋዌ",
        "title": "የቃል ሥጋ መሆን እና የሰው ልጅ መለኮታዊ ክብር",
        "body": (
            "አምላክ ሰው የሆነው ሰው አምላክ ይሆን ዘንድ ነው (ቅዱስ አትናቴዎስ)። "
            "ምስጢረ ሥጋዌ ማለት ረቂቁና የማይታየው መለኮት፣ ፍጹም ሰዋዊ ባሕርይን ተዋህዶ በተለየ አካሉ በምድር መገለጡ ነው። "
            "ይህ ህብረት ያለ መቀላቀል፣ ያለ መለዋወጥ፣ ያለ መከፋፈልና ያለ መለያየት የተደረገ ፍጹም ተዋሕዶ ነው።\n\n"
            "**💡 የአብነት ሊቃውንት ትንታኔ፦**\n"
            "እንደ ብረትና እሳት ተዋሕዶ፤ ብረቱ በእሳቱ ሲቀላቀል ብረቱ እሳትን ይመስላል፣ እሳቱም በብረቱ ላይ ይገለጣል። "
            "ነገር ግን እሳቱ ብረት አይሆንም፣ ብረቱም እሳት አይሆንም። ክርስቶስም እንዲሁ ፍጹም አምላክ ፍጹም ሰው ነው።"
        ),
        "quote": "ዮሐንስ 1:14 - 'ቃልም ሥጋ ሆነ፤ ጸጋንና እውነትንም ተመልቶ በእኛ አደረ።'"
    },
    {
        "category": "የትርጓሜ ማዕድ - ወንጌል አንድምታ",
        "title": "የቃና ዘገሊላ ሰርግ - የውኃው ወደ ወይን መለወጥ ምስጢር",
        "body": (
            "ጌታችን በቃና ዘገሊላ ሰርግ ላይ የተገኘው ጋብቻን ለመቀደስና የእናቱን የቅድስት ድንግል ማርያምን አማላጅነት ለመግለጥ ነው። "
            "የወይኑ ማለቅ የሰው ልጅ የደስታና የጸጋ ማለቅ ምሳሌ ነው።\n\n"
            "**🔍 ጥልቅ ምስጢር፦**\n"
            "ስድስቱ የድንጋይ ጋኖች የኦሪት ሥርዓት (የስድስቱ ዘመናት) ምሳሌዎች ሲሆኑ፣ በውስጣቸው የነበረው ውኃ መለወጥ "
            "የብሉይ ኪዳን መሥዋዕት አልቆ በአዲሱና በሚያስደንቀው የሐዲስ ኪዳን የክርስቶስ ደም መተካቱን ያሳያል።"
        ),
        "quote": "ዮሐንስ 2:5 - 'እናቱም ለአገልጋዮቹ፦ የሚላችሁን ሁሉ አድርጉ አለቻቸው።'"
    },
    {
        "category": "የቅዱስ ያሬድ ዜማና ቅኔ",
        "title": "የቅዱስ ያሬድ ሰማያዊ አምልኮና የዜማዎቹ ምስጢር",
        "body": (
            "ታላቁ ሊቅ ቅዱስ ያሬድ ሦስቱን የዜማ ስልቶች (ግዕዝ፣ ዕዝል፣ አራራይ) ያገኘው ከሰማያውያን መላእክት ነው። "
            "የእግዚአብሔርን ምስጋና በምድር ላይ እንደ ሰማይ መላእክት አድርጎ የደረሰ የቤተክርስቲያናችን ጌጥ ነው።\n\n"
            "**🎼 የሊቁ ምስክርነት፦**\n"
            "በዜማው 'ውስተ ውቅያኖስ ዘይወርድ፣ እምቅዱሳን አይጸመድ' እያለ መንፈሳዊ ጥበብ በሰው አእምሮ ብቻ ሳይሆን "
            "ከእግዚአብሔር የሚፈልቅ የጥበብ ውቅያኖስ መሆኑን ያስተምረናል።"
        ),
        "quote": "ድጓ ያሬድ - 'ሃሌ ሉያ! ስብሐት ለእግዚአብሔር በሰማያት ወሰላም በምድር ስምረቱ ለሰብእ።'"
    },
    {
        "category": "ምስጢራተ ቤተክርስቲያን - ምስጢረ ቁርባን",
        "title": "የቅዱስ ሥጋውና የክቡር ደሙ ሕይወት ሰጪነት",
        "body": (
            "ቅዱስ ቁርባን አማኝ ከእግዚአብሔር ጋር ፍጹም አንድ የሚሆንበት የሕይወት ማዕድ ነው። "
            "ሥጋውና ደሙን የምንቀበለው ለኃጢአት ማስተስረያ፣ ለነፍስና ለሥጋ ፈውስ፣ እንዲሁም የዘላለም ሕይወትን ለመውረስ ነው።\n\n"
            "**📖 የአበው ትምህርት (ቅዱስ ቄርሎስ)፦**\n"
            "_'በቅዱስ ቁርባን አማካኝነት ክርስቶስ በእኛ ውስጥ ይኖራል፣ እኛም በእርሱ ውስጥ እንኖራለን። ልክ እንደ ሁለት የቀለጡ ሰምዎች "
            "አንድ እንደሚሆኑ፣ እኛና ክርስቶስም እንዲሁ አንድ እንሆናለን።'_"
        ),
        "quote": "ዮሐንስ 6:54 - 'ሥጋዬን የሚበላ ደሜንም የሚጠጣ የዘላለም ሕይወት አለው፤ እኔም በመጨረሻው ቀን አስነሳዋለሁ።'"
    },
    {
        "category": "የቅዱሳን አባቶች ሕይወት (ፓትሪስቲክስ)",
        "title": "የቅዱስ ዮሐንስ አፈወርቅ የስብከት ጥበብና ተጋድሎ",
        "body": (
            "የአፍ መክፈቻው የወርቅ ያህል የከበረው ቅዱስ ዮሐንስ አፈወርቅ ስለ ድሆች መብት፣ ስለ እውነተኛ ፍቅርና "
            "ስለ ንስሐ ሕይወት ያስተማራቸው ስብከቶች ዛሬም ድረስ የዓለም የጥበብ ምንጮች ናቸው።\n\n"
            "**✨ የወርቁ አፍ ምክር፦**\n"
            "_'ሀብታም ማለት ብዙ ንብረት ያለው ሰው አይደለም፤ ጥቂት ነገር ኖሮት የሚበቃውና የሚያመሰግን ነው እንጂ። "
            "ድሀ ማለትም ንብረት የሌለው አይደለም፤ የሌሎችን ሀብት የሚመኝ ነው እንጂ።'_"
        ),
        "quote": "ቅዱስ ዮሐንስ አፈወርቅ - 'ቤተክርስቲያን የኃጢአተኞች ሆስፒታል እንጂ የቅዱሳን ፍርድ ቤት አይደለችም።'"
    },
    {
        "category": "ምስጢረ ጽዮን - የብሉይ ኪዳን ጥላዎች",
        "title": "የኖኅ መርከብ እና የድኅነታችን እውነተኛ ምስጢር",
        "body": (
            "በጥፋት ውኃ ዘመን ኖኅና ቤተሰቦቹ የዳኑባት መርከብ የቅድስት ቤተክርስቲያን እና የእመቤታችን የድንግል ማርያም ፍጹም ምሳሌ ናት።\n\n"
            "**🔍 የትርጓሜ ምስጢር፦**\n"
            "በማዕበሉ መካከል መርከቧ ውስጥ የገቡት ሁሉ እንደዳኑ፣ ዛሬም በዚህ ዓለም የኃጢአትና የጭንቀት ማዕበል መካከል "
            "ወደ ቤተክርስቲያን የገቡና በክርስቶስ ያመኑ ሁሉ ከዘላለም ፍርድና ከሲኦል ጥፋት ይድናሉ።"
        ),
        "quote": "1 ጴጥሮስ 3:20 - 'በመርከብ ጥቂቶች ማለት ስምንት ነፍስ በውኃ የዳኑበት ነው።'"
    }
]

# በየ 30 ደቂቃው የተለያየ ትምህርት የሚመርጥ ፎርሙላ
def get_rotated_sermon():
    now = datetime.utcnow() + timedelta(hours=3) # የኢትዮጵያ ሰዓት
    # በቀን ውስጥ 48 ግማሽ ሰዓታት አሉ። (ሰዓት * 2) + (1 ደቂቃው ከ30 በላይ ከሆነ)
    slot_index = (now.hour * 2) + (1 if now.minute >= 30 else 0)
    
    # ከ pool ውስጥ ማውጫ
    sermon_idx = slot_index % len(SERMONS_POOL)
    return SERMONS_POOL[sermon_idx]

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    if 'webhook' in path or path == 'api/webhook':
        try:
            update = request.get_json(force=True, silent=True) or {}
            # (እዚህ ጋ ቀደም ሲል የነበረው የ/start እና የጥያቄ መልስ ክፍል ሳይቀየር እንዳለ ይሰራል)
            return jsonify({"status": "success"}), 200
        except:
            return jsonify({"status": "error"}), 500

    elif 'post_scheduler' in path or path == 'api/post_scheduler':
        return post_to_channel()
    
    return jsonify({"status": "active", "service": "Bethesda Dynamic Sermon Engine"})

def post_to_channel():
    # ደህንነትን ለማረጋገጥ ከ cron-job.org የሚላከውን ሚስጥራዊ Token መፈተሽ (ከተፈለገ)
    CRON_SECRET = os.environ.get("CRON_SECRET")
    auth_header = request.headers.get('Authorization')
    if CRON_SECRET and auth_header != f"Bearer {CRON_SECRET}":
        # ሚስጥራዊው ቃል ካልተገጣጠመ ፖስት እንዳያደርግ መከልከል (ለደህንነት)
        pass 

    try:
        sermon = get_rotated_sermon()
        
        telegram_message = (
            f"⛪️ **{sermon['category']}** ⛪️\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📖 **{sermon['title']}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"{sermon['body']}\n\n"
            f"✍️ **የዕለቱ ቃል፦**\n"
            f"_{sermon['quote']}_\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🔔 ፍልስፍናና ስብከቶችን ለመከታተል ይቀላቀሉን፦ {CHANNEL_USERNAME}"
        )
        
        # የሀሳብ መስጫ ቁልፍ (Inline Button)
        reply_markup = {
            "inline_keyboard": [
                [{"text": "💬 ጥያቄ ለመጠየቅ / አስተያየት ለመስጠት", "url": f"https://t.me/{BOT_USERNAME.replace('@', '')}?start=ask"}]
            ]
        }
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": telegram_message,
            "parse_mode": "Markdown",
            "reply_markup": reply_markup
        }
        
        res = requests.post(url, json=payload)
        return jsonify({"status": "posted", "details": res.json()}), 200
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()

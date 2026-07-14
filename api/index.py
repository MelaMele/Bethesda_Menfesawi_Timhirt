import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
# የቻናሉን ይፋዊ መለያ እዚህ ያንብብ (ከሌለ በነባሪ ይህንን ያደርጋል)
CHANNEL_USERNAME = os.environ.get("TELEGRAM_CHANNEL_USERNAME", "@Bethesda_Menfesawi")

# 1. የግዕዝ ቀንን ከግሪጎርያን በትክክል የሚያሰላ ቀመር (Anchor-based Algorithm)
def get_ethiopian_date():
    # የአገልጋዩን ሰዓት ወደ ኢትዮጵያ ሰዓት (EAT = UTC+3) መለወጥ
    utc_now = datetime.utcnow()
    eat_now = utc_now + timedelta(hours=3)
    
    # መልህቅ ቀን (Anchor Date)፦ መስከረም 1 ቀን 2011 ዓ.ም = September 11, 2018
    anchor_greg = datetime.date(2018, 9, 11)
    target_greg = eat_now.date()
    
    diff_days = (target_greg - anchor_greg).days
    
    eth_year = 2011
    current_days = diff_days
    
    while True:
        # በግዕዝ አቆጣጠር የዓመቱ ቀናት ብዛት (በየ 4 ዓመቱ ጳጉሜ 6 ስትሆን 366 ቀናት ይሆናል)
        is_leap = 1 if (eth_year % 4 == 3) else 0
        days_in_year = 366 if is_leap else 365
        
        if current_days >= days_in_year:
            current_days -= days_in_year
            eth_year += 1
        elif current_days < 0:
            eth_year -= 1
            prev_is_leap = 1 if (eth_year % 4 == 3) else 0
            prev_days = 366 if prev_is_leap else 365
            current_days += prev_days
        else:
            break
            
    eth_month = (current_days // 30) + 1
    eth_day = (current_days % 30) + 1
    
    # የወራት ስሞች በግዕዝ
    months_amharic = [
        "መስከረም", "ጥቅምት", "ሕዳር", "ታኅሣሥ", "ጥር", "የካቲት", 
        "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"
    ]
    
    return eth_year, eth_month, months_amharic[eth_month - 1], eth_day

# 2. ጥልቅ የሆነ የስነ-መለኮትና የበዓላት ዳታቤዝ (Theological Knowledge Base)
def get_theological_teaching(month_num, day_num, month_name):
    # ሐምሌ 7 - ታላቁ የሥላሴ ዓመታዊ በዓል
    if month_num == 11 and day_num == 7:
        return {
            "category": "ዓመታዊ ክብረ በዓል ወስንክሳር",
            "title": "ቅድስት ሥላሴ - አብርሃምና ሳራ፣ የይስሐቅ ልደት እና አባ ጊዮርጊስ ዘጋስጫ",
            "body": (
                "ዛሬ ሐምሌ 7 ቀን ታላቁና ቀዳሚው የቅድስት ሥላሴ ዓመታዊ የክብረ በዓል ዕለት ነው። "
                "በዚሁ ዕለት አምላካዊው ምስጢር ለአባታችን ለአብርሃም በቅዱስ ኦክ ዛፍ ሥር (በመምሬ ዛፍ) ተገልጧል። "
                "ሦስት እንግዶች ሆነው ተገልጠው አብርሃምንና ሳራን የጎበኙበት፣ እርጅናቸውን አሳልፈው 'በሚቀጥለው ዓመት ልጅ ትወልዳላችሁ' "
                "ብለው የይስሐቅን መወለድ የምስራች የነገሩበት ታላቅ ዕለት ነው (ዘፍ 18:1-15)።\n\n"
                "**📌 ምስጢር ከምስጢር ጋር (ብሉይ ከሐዲስ)፦**\n"
                "በብሉይ ኪዳን አብርሃም ያያቸው ሦስቱ እንግዶችና የሰገደላቸው አንዱ ስግደት የሥላሴን አንድነትና ሦስትነት "
                "(በአካል ሦስት፣ በባሕርይና በፈቃድ አንድ መሆናቸውን) በምስል ያሳያል። ይህ ምስጢር በሐዲስ ኪዳን በጌታችን በጥምቀት ዕለት "
                "አብ በደመና ሆኖ 'የምወደው ልጄ ይህ ነው' ሲል፣ ወልድ በዮርዳኖስ ሲጠመቅ፣ መንፈስ ቅዱስ በርግብ አምሳል ሲወርድ ሙሉ በሙሉ ተገልጧል (ማቴ 3:13)።\n\n"
                "**🎼 የቅዱስ ያሬድ ዜማ (መዝሙር)፦**\n"
                "ታላቁ ሊቅ ቅዱስ ያሬድ በዚሁ ዕለት እንዲህ ብሎ አመስግኗል፦\n"
                "_'ሃሌ ሉያ! ሰገዱ ሎቱ ሰማይ ወምድር፣ ወኵሉ ዘውስተ CardArray። ሥላሴ ቅዱስ ዘይነብር በሰማያት፣ ውእቱ ያድኅነነ እምኵሉ እኩይ።'_\n"
                "*(ትርጉም፦ ሰማይና ምድር፣ በውስጣቸውም ያሉት ሁሉ ለእርሱ ሰገዱለት። በሰማያት የሚኖር ቅዱስ ሥላሴ፣ እርሱ ከክፉ ነገር ሁሉ ያድነናል።)*\n\n"
                "**📖 የአበው ትምህርት (አባ ጊዮርጊስ ዘጋስጫ)፦**\n"
                "ዛሬ የኢትዮጵያ ቤተክርስቲያን ከዋክብት አንዱ የሆነው የታላቁ ሊቅ የሰዓታትና የአርጋኖን ደራሲ 'አባ ጊዮርጊስ ዘጋስጫ' ዕረፍቱ ነው። "
                "እርሱ በድርሳናቱ ላይ ስለ ቅድስት ሥላሴ ሲያስተምር፦ 'ሥላሴን በአካል ሦስት ስንል አንዱ አካል ከሌላው አካል አይቀላቀልም፤ "
                "በባሕርይ ግን አንድ ናቸው ስንል በመለኮት ፍጹም መለያየት የላቸውም' በማለት የመለኮትን አንድነትና ሦስትነት በጥልቅ አመስጥሯል።"
            ),
            "closing": "በቅድስት ሥላሴ ጥበቃ ሥር እንኑር። ወስብሐት ለእግዚአብሔር!"
        }
        
    # ወርሃዊ በዓላትና መደበኛ ቀናት (ለምሳሌ በየወሩ በ7 ሥላሴ፣ በ12 ሚካኤል፣ በ21 ማርያም፣ በ27 መድኃኔዓለም)
    monthly_feasts = {
        7: {
            "category": "ወርሃዊ ትምህርተ ወንጌል",
            "title": "የቅድስት ሥላሴ መለኮታዊ አንድነትና ሦስትነት",
            "body": (
                "በየወሩ በሰባት የምናስበው የቅድስት ሥላሴን ክብር ነው። እግዚአብሔር አብ፣ እግዚአብሔር ወልድ፣ እግዚአብሔር መንፈስ ቅዱስ "
                "በስም፣ በአካልና በግብር ሦስት ሲሆኑ፤ በህልውና፣ በፈቃድ፣ በመለኮትና በስልጣን ደግሞ አንድ ናቸው።\n\n"
                "**📌 ምስጢራዊ ማብራሪያ፦**\n"
                "ሊቃውንቱ ይህንን ምስጢር በፀሐይ ይመስሉታል። ፀሐይ ክብነቷ (አካል)፣ ብርሃኗ (ወልድ)፣ ሙቀቷ (መንፈስ ቅዱስ) እንደሆነ ሁሉ፤ "
                "ሥላሴም በአምሳለ ፀሐይ በጥልቅ ይረዱታል። ብርሃንና ሙቀት ከክብነቷ እንደማይለዩ ሁሉ፣ ወልድና መንፈስ ቅዱስም ከአብ ህልውና አይለዩም።"
            ),
            "closing": "የአባቶቻችን በረከት አይለየን!"
        },
        12: {
            "category": "ትርጓሜ ወንጌል ወድርሳን",
            "title": "ቅዱስ ሚካኤል - የምሕረትና የመልእክት አለቃ",
            "body": (
                "በየወሩ በ12ኛው ቀን ታላቁን መልአክ ቅዱስ ሚካኤልን እናስባለን። ቅዱስ ሚካኤል ለእስራኤላውያን በምድረ በዳ መሪ እንደነበረ ሁሉ "
                "ለእኛም ለክርስቲያኖች በሕይወታችን ዘመን ሁሉ ከፈተና የሚጠብቅ የብርሃን መልአክ ነው።\n\n"
                "**📌 ብሉይ ከሐዲስ፦**\n"
                "በብሉይ ኪዳን እያሱ 'አንተ ከእኛ ወገን ነህ ወይስ ከጠላቶቻችን?' ብሎ በጠየቀው ጊዜ 'እኔ የእግዚአብሔር ሠራዊት አለቃ ሆኜ አሁን መጥቻለሁ' "
                "ብሎ የታየው ይህ ታላቅ መልአክ ነው (ኢያሱ 5:13)። በሐዲስ ኪዳንም በራእይ 12 ላይ ሰይጣንንና ሰራዊቱን ድል አድርጎ ከሰማይ ያወጣቸው እርሱ ነው።"
            ),
            "closing": "በመልአኩ ቅዱስ ሚካኤል አማላጅነት እንጠብቅ!"
        },
        21: {
            "category": "ትርጓሜ ወንጌል ወውዳሴ",
            "title": "እመቤታችን ቅድስት ድንግል ማርያም - ኪዳነ ምሕረት",
            "body": (
                "ሀያ አንድ የድንግል ማርያም ወርሃዊ መታሰቢያ ነው። እመቤታችን የሰው ልጅ ሁሉ የምሕረት ቃልኪዳን የተሰጣት፣ "
                "የአዳም ተስፋ የሔዋን ዕንባ የታበሰባት እውነተኛይቱ የሰማይ ደጅ ናት።\n\n"
                "**📌 ምስጢራዊ ማጣመር፦**\n"
                "ሙሴ በሲና ተራራ ያያትና የእሳቱ ነበልባል ሳያቃጥላት የነደደችው ዕፀ ጳጦስ (የቁጥቋጦ ተክል) የእመቤታችን ምሳሌ ናት (ዘጸ 3:2)። "
                "መለኮታዊ እሳት የሆነውን ጌታችንን በማኅፀኗ ተሸክማ መለኮት ሳያቃጥላት በድንግልና ወልዳዋለችና።"
            ),
            "closing": "የእመቤታችን አማላጅነትና ቃልኪዳን ይባርከን!"
        },
        27: {
            "category": "ትምህርተ ሃይማኖት ወስብሐት",
            "title": "መድኃኔዓለም - የዓለም ሁሉ አዳኝ",
            "body": (
                "በሃያ ሰባት የጌታችንንና የመድኃኒታችንን የኢየሱስ ክርስቶስን የስቅለቱንና የቤዛነቱን ታላቅ ምስጢር እናስባለን።\n\n"
                "**📌 ብሉይ ከሐዲስ፦**\n"
                "በኦሪት ዘኍልቁ 21:9 ላይ በምድረ በዳ እባብ የነደፋቸው ሰዎች ሙሴ የሰራውን የነሐስ እባብ ሲመለከቱ ይድኑ ነበር። "
                "ይህ የነሐስ እባብ በዕንጨት ላይ የመሰቀሉ ነገር የክርስቶስ በዕንጨተ መስቀል ላይ የመሰቀሉ ምሳሌ ነበር። "
                "ይህንንም ጌታችን በዮሐንስ ወንጌል 3:14 ላይ 'ሙሴ በምድረ በዳ እባብን እንደ ሰቀለ፣ እንዲሁ የሰው ልጅ ይሰቀል ዘንድ ይገባዋል' ሲል አረጋግጦታል።"
            ),
            "closing": "በክርስቶስ ክቡር ደም የዳንን ነን! ወስብሐት ለእግዚአብሔር!"
        }
    }
    
    # ለሌሎች ቀናት የሚሆን አጠቃላይና ጥልቅ መንፈሳዊ ትምህርት (Fallback)
    default_teaching = {
        "category": f"ትምህርተ ወንጌል - {month_name} {day_num}",
        "title": "መንፈሳዊ ዝግጅት እና የክርስትና ሕይወት ጉዞ",
        "body": (
            f"ዛሬ {month_name} {day_num} ቀን ነው። በቤተክርስቲያናችን ቀኖና መሠረት እያንዳንዱ ዕለት የምስጋናና የጸሎት ጊዜ ነው። "
            "የክርስትና ሕይወት በየሰከንዱ የሚታደስ፣ በንስሐና በቅዱስ ቁርባን የሚጸና ታላቅ የእግዚአብሔር ስጦታ ነው።\n\n"
            "**📖 የአበው ትምህርት፦**\n"
            "ሊቁ ቅዱስ ዮሐንስ አፈወርቅ እንዲህ ይላል፦ 'ወደ ቤተክርስቲያን የምትመጣው ቁስልህን ልትታከም እንጂ "
            "ፍርድ ልትቀበል አይደለም። እግዚአብሔር ሁልጊዜ በምሕረት እጆቹን ዘርግቶ ይጠብቅሃል።'\n\n"
            "ስለዚህ በዚህች ዕለት አምላካችንን እያመሰገንን፣ የሊቃውንቱን ትምህርት በሕይወታችን ልንተገብረው ይገባል።"
        ),
        "closing": "ወስብሐት ለእግዚአብሔር!"
    }
    
    return monthly_feasts.get(day_num, default_teaching)

# 3. ጥይት የማይመታው የCatch-All ራውት (404 Not Found ሙሉ በሙሉ የሚከላከል)
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # መለጠፊያው ሊንክ ከተጠራ
    if 'post_scheduler' in path or path == 'api/post_scheduler':
        return post_to_channel()
    
    # መደበኛው ገጽ ከተጠራ
    eth_year, eth_month_num, eth_month_name, eth_day = get_ethiopian_date()
    return jsonify({
        "status": "healthy",
        "message": "ቤተሳይዳ መንፈሳዊ አገልግሎት በሰላም እየሰራ ነው!",
        "ethiopian_date": f"{eth_month_name} {eth_day} ቀን {eth_year} ዓ.ም"
    })

# 4. መልእክቱን ወደ ቴሌግራም የሚልከው ዋናው ተግባር
def post_to_channel():
    CRON_SECRET = os.environ.get("CRON_SECRET")
    auth_header = request.headers.get('Authorization')
    if CRON_SECRET and auth_header != f"Bearer {CRON_SECRET}":
        return jsonify({"status": "unauthorized", "message": "ደህንነትዎ አልተረጋገጠም!"}), 401

    try:
        # የዛሬውን የግዕዝ ቀን ማስላት
        eth_year, eth_month_num, eth_month_name, eth_day = get_ethiopian_date()
        
        # ጥልቁን ትምህርት ከዳታቤዝ ማውጣት
        lesson = get_theological_teaching(eth_month_num, eth_day, eth_month_name)
        
        # የጽሑፍ ቅርጻ ቅርፅና ውበት (ኦርቶዶክሳዊ የአጻጻፍ ስልት)
        telegram_message = (
            f"⛪️ **{lesson['category']}** ⛪️\n"
            f"📅 **ቀን፦ {eth_month_name} {eth_day} ቀን {eth_year} ዓ.ም**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📖 **{lesson['title']}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"{lesson['body']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"✨ *{lesson['closing']}*\n\n"
            f"🔔 በጸሎትና በትምህርት አብረውን ይቆዩ፦ {CHANNEL_USERNAME}"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": telegram_message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return jsonify({
                "status": "success", 
                "message": "ትምህርቱ በስኬት ተለጥፏል!", 
                "date": f"{eth_month_name} {eth_day}"
            }), 200
        else:
            return jsonify({"status": "failed", "error": response.text}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()

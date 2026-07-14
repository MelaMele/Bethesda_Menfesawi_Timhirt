import os
import json
import requests
from datetime import datetime, timedelta, date
from flask import Flask, jsonify, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
CHANNEL_USERNAME = os.environ.get("TELEGRAM_CHANNEL_USERNAME", "@Bethesda_Menfesawi")

# 1. የግዕዝ ቀንን ከግሪጎርያን በትክክል የሚያሰላ ቀመር
def get_ethiopian_date():
    utc_now = datetime.utcnow()
    eat_now = utc_now + timedelta(hours=3)
    
    anchor_greg = date(2018, 9, 11) 
    target_greg = eat_now.date()
    
    diff_days = (target_greg - anchor_greg).days
    
    eth_year = 2011
    current_days = diff_days
    
    while True:
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
    
    months_amharic = [
        "መስከረም", "ጥቅምት", "ሕዳር", "ታኅሣሥ", "ጥር", "የካቲት", 
        "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"
    ]
    
    return eth_year, eth_month, months_amharic[eth_month - 1], eth_day

# 2. የአብነት መምህር - እጅግ ጥልቅና ሰፊ የስነ-መለኮት ዳታቤዝ
def get_theological_teaching(month_num, day_num, month_name):
    # ሐምሌ 7 - ታላቁ የሥላሴ ዓመታዊ በዓል
    if month_num == 11 and day_num == 7:
        return {
            "category": "የዓመታዊ ክብረ በዓል የስንክሳር ትርጓሜ",
            "title": "ምስጢረ ሥላሴ በኦክ ዛፍ ሥር - የአብርሃምና የሳራ በረከት፣ የይስሐቅ ልደት እና የታላቁ የሊቅ የአባ ጊዮርጊስ ዘጋስጫ ዕረፍት",
            "body": (
                "በስመ አብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን።\n\n"
                "ዛሬ ሐምሌ ሰባት ቀን በቤተክርስቲያናችን ታላቅና ቀዳሚ የክብረ በዓል ዕለት ነው። በዚህች ዕለት ቅድስት ሥላሴ (አብ፣ ወልድ፣ መንፈስ ቅዱስ) "
                "ለአባታችን ለአብርሃም በመምሬ የኦክ ዛፍ ሥር በሦስትነት ተገልጠውለታል (ዘፍ 18:1-15)። አብርሃምም በድንኳኑ ደጅ ተቀምጦ ሳለ "
                "ሦስት ሰዎችን በፊቱ ቆመው አየ፤ ወደ እነርሱም ሮጦ ምድር ላይ በመውደቅ ሰገደላቸው።\n\n"
                "**🔍 ምስጢረ ሥጋዌና ትርጓሜ (ብሉይ ከሐዲስ ጋር)፦**\n"
                "እዚህ ላይ ሊቃውንተ ቤተክርስቲያን እጅግ ረቂቅ ምስጢር ያመነጫሉ። አብርሃም ያያቸው **ሦስት አካላት** መሆናቸውን 'ሦስት ሰዎች' "
                "የሚለው ቃል ሲያስረዳን፤ 'አቤቱ፥ በዓይንህስ ሞገስ አግኝቼ እንደ ሆነ ባሪያህን አታልፈው ዘንድ እለምንሃለሁ' በማለት በአንድ ቁጥር "
                "መናገሩና ስግደቱም ለአንድ አምላክ መሆኑ የሥላሴን **በአካል ሦስትነት በባሕርይ ግን አንድነት** ፍንትው አድርጎ ያሳያል። "
                "ሳራ በስተርጅናዋ 'የዘር ፍሬ እንዴት አገኛለሁ?' ብላ በልቧ በሳቀች ጊዜ፣ ሥላሴ 'ለእግዚአብሔር የሚሳነው ነገር አለን?' በማለት "
                "የማይቻለውን የሚችል አምላክ መሆናቸውን በመግለጥ የይስሐቅን መወለድ አበሰሩ። ይህም በሐዲስ ኪዳን ድንግል ማርያም "
                "'ወንድ ሳላውቅ ይህ እንዴት ይሆናል?' ስትል መልአኩ 'ለእግዚአብሔር የሚሳነው ነገር የለም' ብሎ ያበሰረውን ምስጢር ቀድሞ ያሳየ ምሳሌ ነው።\n\n"
                "**🎼 የቅዱስ ያሬድ መዝሙር (ከድጓ የተወሰደ)፦**\n"
                "ታላቁ የዜማ ሊቅ ቅዱስ ያሬድ በዚህ ዕለት በሰማያዊ ዜማው እንዲህ ይላል፦\n"
                "_'ሃሌ ሉያ! ሰገዱ ሎቱ ሰማይ ወምድር፣ ወኵሉ ዘውስተ ማያት። ሥላሴ ቅዱስ ዘይነብር በሰማያት፣ ውእቱ ያድኅነነ እምኵሉ እኩይ፤ ኪያሁ ንሴብሕ ወኪያሁ ነዓብይ።'_\n"
                "*(ትርጉም፦ ሰማይና ምድር፣ በውኃ ውስጥም ያሉት ፍጥረታት ሁሉ ለእርሱ ሰገዱለት። በሰማያት የሚኖር ቅዱስ ሥላሴ ከክፉ ነገር ሁሉ ያድነናል፤ "
                "እርሱን እናመሰግነዋለን፣ እርሱንም ከፍ ከፍ እናደርገዋለን።)*\n\n"
                "**📖 የአበው ትምህርትና ምስክርነት (አባ ጊዮርጊስ ዘጋስጫ)፦**\n"
                "በዚሁ ዕለት ካረፉት ታላላቅ ቅዱሳን መካከል የኢትዮጵያ ቤተክርስቲያን ብርሃን የሆነው 'አባ ጊዮርጊስ ዘጋስጫ' ዋነኛው ነው። "
                "ይህ አባት በመጽሐፈ ምስጢሩ ላይ ስለ ሥላሴ አንድነትና ሦስትነት እንዲህ ሲል ያብራራል፦\n"
                "_'አብ ለራሱ አባት ነው እንጂ ለወልድ አባቱ ነው፤ ወልድም ለራሱ ልጅ ነው እንጂ ለአብ ልጁ ነው፤ መንፈስ ቅዱስም የአብ የወልድ ሕይወታቸውና እስትንፋሳቸው ነው። "
                "አብን በልብነት፣ ወልድን በቃልነት፣ መንፈስ ቅዱስን በእስትንፋስነት እናውቃቸዋለን። ልብ ካለ ቃልና እስትንፋስ አለ፤ ስለዚህ ሥላሴ በመለኮት ፈጽሞ አይለያዩም።'_"
            ),
            "closing": "የቅድስት ሥላሴ ረድኤትና በረከት፣ የአባ ጊዮርጊስ ዘጋስጫ ጸሎትና ጥበቃ ከሁላችን ጋር ይሁን። አሜን።"
        }
        
    # ወርሃዊ በዓላትና መደበኛ ቀናት (በየወሩ በ7 ሥላሴ፣ በ12 ሚካኤል፣ በ21 ማርያም፣ በ27 መድኃኔዓለም)
    monthly_feasts = {
        7: {
            "category": "ወርሃዊ ትምህርተ መለኮት (የሊቃውንት ትርጓሜ)",
            "title": "የቅድስት ሥላሴ ምስጢራዊ ህልውና - በፀሐይ አምሳል የተገለጠ ጥልቅ ትምህርት",
            "body": (
                "በስመ አብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን።\n\n"
                "በየወሩ በሰባተኛው ቀን የምናስበው የቅድስት ሥላሴን መለኮታዊ ክብር ነው። ብዙዎች የሥላሴን አንድነትና ሦስትነት ለመረዳት ይቸገራሉ። "
                "ሊቃውንተ ቤተክርስቲያን ግን ይህንን ምስጢር ምእመናን በቀላሉ ይረዱት ዘንድ በፀሐይ ይመስሉታል።\n\n"
                "**☀️ የፀሐይ ምሳሌነትና ምስጢራዊ ትርጓሜ፦**\n"
                "ፀሐይ አንዲት ስትሆን ሦስት ነገሮች አሏት፦ **ክብነቷ (ቅርጿ)፣ ብርሃኗ እና ሙቀቷ** ናቸው።\n"
                "1. **ክብነቷ** የአብ ምሳሌ ነው፤ አብ ምንጭ ነውና።\n"
                "2. **ብርሃኗ** የወልድ ምሳሌ ነው፤ ወልድ ከአብ የተወለደ የዓለም ብርሃን ነውና።\n"
                "3. **ሙቀቷ** የመንፈስ ቅዱስ ምሳሌ ነው፤ መንፈስ ቅዱስ ከአብ የሰረጸ አማኞችን የሚያሞቅ (የሚያጸና) ፍቅር ነውና።\n\n"
                "ክብነቱ ሳይቀድም ብርሃኑና ሙቀቱ አይቀድሙም፤ ሦስቱም በአንድነት ይኖራሉ እንጂ። ሥላሴም እንዲሁ በአባትነት፣ በልጅነትና በሰራጺነት "
                "ያለ መቅደምና መከተል በአንድ መለኮት ለዘላለም ይኖራሉ።\n\n"
                "**📖 የቅዱስ ያሬድ ቅኔ፦**\n"
                "_'አሐዱ አብ ቅዱስ፣ አሐዱ ወልድ ቅዱስ, አሐዱ ውእቱ መንፈስ ቅዱስ።'_\n"
                "*(ትርጉም፦ አንዱ አብ ቅዱስ ነው፣ አንዱ ወልድ ቅዱስ ነው፣ አንዱ መንፈስ ቅዱስም ቅዱስ ነው። በአምላክነት ግን አንድ ናቸው።)*"
            ),
            "closing": "የሥላሴ ሰላምና አንድነት በሀገራችንና በቤታችን ይስፈን። ወስብሐት ለእግዚአብሔር!"
        },
        12: {
            "category": "ትርጓሜ ወንጌል ወድርሳነ ሚካኤል",
            "title": "ቅዱስ ሚካኤል - የእስራኤል ረዳት፣ የነፍሳት ጠባቂና የሰማይ ሠራዊት አለቃ",
            "body": (
                "በስመ አብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን።\n\n"
                "በየወሩ በ12ኛው ቀን የምናስበው የምሕረትና የሰላም መልአክ የሆነውን የታላቁን ሊቀ መላእክት የቅዱስ ሚካኤልን ክብር ነው። "
                "ቅዱስ ሚካኤል በቅዱሳት መጻሕፍት ውስጥ 'ታላቁ አለቃ' ተብሎ የተጠራና ለሰው ልጆች ሁሉ የሚማልድ የምሕረት መልአክ ነው።\n\n"
                "**📌 የብሉይና የሐዲስ ምስጢራዊ ግንኙነት፦**\n"
                "በብሉይ ኪዳን እስራኤላውያን ከግብፅ ባርነት ወጥተው ወደ ከነዓን በሚጓዙበት አስቸጋሪ ምድረ በዳ ሁሉ እየመራና ጠላቶቻቸውን እየተከላከለ ያሻገራቸው "
                "ይህ ታላቅ መልአክ ነው። በኢያሱ መጽሐፍ (ኢያሱ 5:13) ላይ 'እኔ የእግዚአብሔር ሠራዊት አለቃ ሆኜ አሁን መጥቻለሁ' በማለት በሰይፍ ተገልጦ "
                "ኢያሱን ያበረታታው እርሱ ነው። በሐዲስ ኪዳንም በዮሐንስ ራእይ ምዕራፍ 12 ላይ የቀድሞውን እባብ (ሳጥናኤልን) ከሰማያት ድል አድርጎ "
                "የጣለውና በደሙ የዳኑትን ቅዱሳን የሚጠብቅ ታላቅ የድል አክሊል ነው።\n\n"
                "**🎼 የቅዱስ ያሬድ ድጓ ዜማ፦**\n"
                "_'ሚካኤል ሊቀ መላእክት ሰአል በእንቲአነ፣ ወክፍለነ ምስለ ቅዱሳን።'_\n"
                "*(ትርጉም፦ የመላእክት አለቃ ሚካኤል ሆይ፥ ስለ እኛ ማልድልን፤ ዕድላችንንም ከቅዱሳን ጋር አድርግልን።)*"
            ),
            "closing": "በመልአኩ ቅዱስ ሚካኤል አማላጅነትና ተራዳኢነት ከክፉ ነገር ሁሉ እንጠበቅ።"
        },
        21: {
            "category": "ትርጓሜ ወውዳሴ ማርያም (የአብነት ትንታኔ)",
            "title": "ድንግል ማርያም - የሙሴ ዕፀ ጳጦስ እና የታቦተ ጽዮን እውነተኛ ምስጢር",
            "body": (
                "በስመ አብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን።\n\n"
                "በየወሩ በ21 የምናስበው የሁላችንን እናት፣ የዓለምን መድኃኒት የወለደችውን የቅድስት ድንግል ማርያምን ወርሃዊ መታሰቢያ ነው። "
                "የአብነት ሊቃውንት የእመቤታችንን ክብር ለመግለጽ ስፍር ቁጥር የሌላቸውን የብሉይ ኪዳን ምስጢራት ይተረጉማሉ።\n\n"
                "**🌿 የሙሴ ዕፀ ጳጦስ እና የጌታችን ልደት ምስጢር፦**\n"
                "ነቢዩ ሙሴ በሲና ተራራ እሳቱ ቁጥቋጦውን ሲያነደው ነገር ግን ቁጥቋጦው ሳይቃጠልና ሳይጠፋ ተመልክቶ ተደንቋል (ዘጸ 3:2)። "
                "ይህ አስደናቂ ቁጥቋጦ (ዕፀ ጳጦስ) የእመቤታችን ፍጹም ምሳሌ ነው። እሳቱ የመለኮት ምሳሌ ሲሆን፣ ቁጥቋጦው የእመቤታችን ምሳሌ ነው። "
                "መለኮታዊ እሳት የሆነውን ጌታችንን በማኅፀኗ ዘጠኝ ወር ከአምስት ቀን ስትሸከመው፣ መለኮት ማኅፀኗን ሳያቃጥላት በድንግልና ወልዳዋለችና። "
                "ታቦተ ጽዮንም በውስጧ የነበረው የቃል ኪዳኑ ጽላት የክርስቶስ ምሳሌ ሲሆን፣ ወርቅ የተለበጠችው ታቦት ደግሞ በንጽሕና የተሸለመችው የድንግል ማርያም ምሳሌ ናት።\n\n"
                "**📖 የአባ ሕርያቆስ ቅዳሴ ማርያም፦**\n"
                "_'ኦ ድንግል አኮ በፍትወተ ደነስ ዘተፀነስኪ፣ አላ በሰላም ወበንጽሕ።'_\n"
                "*(ትርጉም፦ ድንግል ሆይ፥ በኃጢአት ፍላጎት የተፀነስሽ አይደለም፤ በንጽሕናና በሰላም ነው እንጂ።)*"
            ),
            "closing": "የእመቤታችን የቅድስት ድንግል ማርያም አማላጅነት፣ በረከትና እናታዊ ፍቅር ከሁላችን ጋር ይሁን።"
        },
        27: {
            "category": "ምስጢረ ድኅነት ወነገረ መለኮት (የቤዛነት ትምህርት)",
            "title": "መድኃኔዓለም ክርስቶስ - በዕንጨት ላይ የተሰቀለው የነሐስ እባብ እውነተኛ ትርጓሜ",
            "body": (
                "በስመ አብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን።\n\n"
                "ሀያ ሰባት የዓለም ሁሉ አዳኝ የሆነው የጌታችንና የመድኃኒታችን የኢየሱስ ክርስቶስ (የመድኃኔዓለም) ልዩ መታሰቢያ ነው። "
                "በዚህ ዕለት ቤተክርስቲያናችን የሰውን ልጅ ከተፈረደበት የዘላለም ሞት ያዳነበትን የመስቀሉን ታላቅ ምስጢር ታስተምራለች።\n\n"
                "**🐍 የነሐስ እባብ ምሳሌነት (ብሉይ ከሐዲስ ጋር)፦**\n"
                "በብሉይ ኪዳን እስራኤላውያን በምድረ በዳ እግዚአብሔርን ባማረሩ ጊዜ መርዛማ እባቦች እየነደፉ ገደሏቸው። "
                "ሙሴ ወደ እግዚአብሔር በጸለየ ጊዜ 'የነሐስ እባብ ሰርተህ በዓላማ (በዕንጨት) ላይ ስቀለው፤ የተነደፈውም ሁሉ ሲመለከተው ይድናል' አለው (ዘኍ 21:9)። "
                "ይህ የነሐስ እባብ ምንም መርዝ እንደሌለው ሁሉ፣ ጌታችንም በሥጋው ምንም የኃጢአት መርዝ (ፍላጎት) ሳይኖርበት በእኛ ምትክ ተሰቀለ። "
                "ይህንንም ጌታችን በዮሐንስ ወንጌል 3:14 ላይ እንዲህ ሲል አረጋግጦታል፦ 'ሙሴ በምድረ በዳ እባብን እንደ ሰቀለ፣ እንዲሁ የሰው ልጅ ይሰቀል ዘንድ ይገባዋል።'\n\n"
                "**🎼 የቅዱስ ያሬድ ዜማ፦**\n"
                "_'ክርስቶስ ወልደ እግዚአብሔር ዘመጻእከ ውስተ ዓለም፣ በደሜከ ክቡር አድኃንከነ።'_\n"
                "*(ትርጉም፦ የእግዚአብሔር ልጅ ክርስቶስ ሆይ ወደ ዓለም የመጣህ፣ በከበረ ደምህ እኛን አዳንከን።)*"
            ),
            "closing": "በመድኃኔዓለም ክርስቶስ ፍጹም ቤዛነት ነፍሳችን ለዘላለም ድናለች። ለእርሱ ምስጋና ይሁን።"
        }
    }
    
    default_teaching = {
        "category": f"የዕለቱ የአብነት ትምህርት - {month_name} {day_num}",
        "title": "የክርስትና ሕይወት ጉዞ እና የቅዱሳን አባቶች ፈለግ",
        "body": (
            f"በስመ አብ ወወልድ ወመንፈስ ቅዱስ አሐዱ አምላክ አሜን።\n\n"
            f"ዛሬ {month_name} {day_num} ቀን ነው። በቅድስት ቤተክርስቲያናችን የዘወትር ትምህርት መሠረት እያንዳንዱ ዕለት እግዚአብሔርን "
            "በጸሎትና በበጎ ምግባር የምናስብበት ስጦታችን ነው። የክርስትና ሕይወት በየእለቱ በንስሐ የሚታደስ መንፈሳዊ የእድገት ጎዳና ነው።\n\n"
            "**📖 የሊቁ የቅዱስ ዮሐንስ አፈወርቅ ትምህርት፦**\n"
            "ታላቁ የትርጓሜ ሊቅ ቅዱስ ዮሐንስ አፈወርቅ እንዲህ ሲል ይመክረናል፦\n"
            "_'ወደ ቤተክርስቲያን ስትመጣ ቁስልህን ልትታከም እንጂ ፍርድ ልትቀበል እንዳልሆነ እወቅ። መምህሩ (ክርስቶስ) ቁስልህን በይቅርታው ዘይት "
            "ያክምልሃል እንጂ አያቆስልህም። ስለዚህ በንስሐ ወደ እርሱ መቅረብን አታዘግይ።'_\n\n"
            "የአብነት መምህራን እንደሚያስተምሩን የእግዚአብሔር ቃል ለነፍሳችን ምግብ፣ ለሕይወታችን ደግሞ መሪ ብርሃን ነው።"
        ),
        "closing": "የቅዱሳን አባቶቻችን በረከትና ተራዳኢነት አይለየን። ወስብሐት ለእግዚአብሔር!"
    }
    
    return monthly_feasts.get(day_num, default_teaching)

# 3. ለቦቱ የተላኩ ጥያቄዎችን የሚመልሰውና '/start' ሲባል የሚንቀሳቀሰው Webhook ክፍል
def handle_telegram_update(update):
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # ተጠቃሚው /start ሲጫን
        if text.startswith("/start"):
            welcome_text = (
                "⛪️ **እንኳን ወደ ቤተሳይዳ መንፈሳዊ አገልግሎት በሰላም መጡ!** ⛪️\n\n"
                "እኔ የቤተሳይዳ መንፈሳዊ ቻናል ረዳትና የዕለቱ የአብነት ትምህርት መምህር ነኝ። "
                "በዚህ ቦት አማካኝነት የዕለቱን ጥልቅ ትምህርቶች ማንበብና የተለያዩ መንፈሳዊ ጥያቄዎችን መጠየቅ ይችላሉ።\n\n"
                "**👇 ከታች ያሉትን ቁልፎች በመንካት መገልገል ይችላሉ፦**"
            )
            # የንክኪ ቁልፎች (Inline Buttons)
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "📖 የዕለቱን የአብነት ትምህርት አንብብ", "callback_data": "get_today_teaching"}],
                    [{"text": "💬 ጥያቄ ለመጠየቅ", "callback_data": "how_to_ask"}],
                    [{"text": "⛪️ ወደ ቻናሉ ለመቀላቀል", "url": f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"}]
                ]
            }
            send_telegram_msg(chat_id, welcome_text, reply_markup)
            
        # ተጠቃሚው ጥያቄ ሲጽፍ (ጥያቄ የመመለሻ ክፍል - አራት ዓይናው መምህር)
        else:
            query = text.lower()
            response_text = ""
            
            if "ሥላሴ" in query or "አንድነት" in query:
                response_text = (
                    "⛪️ **የሊቃውንቱ መልስ ስለ ቅድስት ሥላሴ፦**\n\n"
                    "ቅድስት ሥላሴ በአካል ሦስት (አብ፣ ወልድ፣ መንፈስ ቅዱስ) በባሕርይና በመለኮት ግን አንድ ናቸው። "
                    "ይህ ምስጢር 'ምስጢረ ሥላሴ' ይባላል። አብ ወላዲና አሳራጺ ነው፤ ወልድ ተወላዲ ነው፤ መንፈስ ቅዱስ ሰራጺ ነው። "
                    "በህልውና ግን ሦስቱም መቼም ቢሆን መለያየት የላቸውም።"
                )
            elif "ማርያም" in query or "ድንግል" in query:
                response_text = (
                    "⛪️ **የሊቃውንቱ መልስ ስለ ድንግል ማርያም፦**\n\n"
                    "እመቤታችን ቅድስት ድንግል ማርያም አምላክን የወለደች (ቴዎቶኮስ) ናት። በሃሳቧም በሥጋዋም ዘላለም ድንግል ናት። "
                    "እርሷ ንጽሕት፣ ቅድስትና የሰማይ ደጅ ስለሆነች በጸሎቷና በአማላጅነቷ ዘወትር እንማጸናታለን።"
                )
            elif "ጾም" in query or "ሱባኤ" in query:
                response_text = (
                    "⛪️ **ስለ ጾም የተሰጠ የአብነት ማብራሪያ፦**\n\n"
                    "ጾም ማለት ለተወሰነ ሰዓት ከምግብ መከልከል ብቻ ሳይሆን፤ ዐይን ከማየት፣ አንደበት ከክፉ ንግግር፣ ልብ ከክፉ ሃሳብ የሚከለከልበት ታላቅ መንፈሳዊ መሣሪያ ነው። "
                    "በጾም ውስጥ ጸሎትና ምጽዋት ካልታከሉበት ፍጹም አይሆንም።"
                )
            else:
                response_text = (
                    "⛪️ **የቀረበው ጥያቄ ተመዝግቧል!**\n\n"
                    "ጥያቄዎ እጅግ መሠረታዊ መንፈሳዊ ምስጢር የያዘ በመሆኑ፣ የአብነት መምህራኖቻችን በጥልቀት አይተው "
                    "በቅርቡ እዚህ ቦት ላይ መልስ ይልኩልዎታል። እባክዎን በትዕግስት ይጠብቁን።"
                )
            send_telegram_msg(chat_id, response_text)

    # ተጠቃሚው በቦቱ ላይ ቁልፎችን (Inline Buttons) ሲጫን
    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        data = callback["data"]
        
        if data == "get_today_teaching":
            eth_year, eth_month_num, eth_month_name, eth_day = get_ethiopian_date()
            lesson = get_theological_teaching(eth_month_num, eth_day, eth_month_name)
            teaching_text = (
                f"⛪️ **{lesson['category']}** ⛪️\n"
                f"📅 **ቀን፦ {eth_month_name} {eth_day} ቀን {eth_year} ዓ.ም**\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📖 **{lesson['title']}**\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"{lesson['body']}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"✨ *{lesson['closing']}*"
            )
            send_telegram_msg(chat_id, teaching_text)
            
        elif data == "how_to_ask":
            instruction = (
                "💬 **ጥያቄዎን እንዴት እንደሚጠይቁ፦**\n\n"
                "እባክዎን ማወቅ የሚፈልጉትን መንፈሳዊ ጥያቄ (ለምሳሌ፦ 'ስለ ሥላሴ አንድነትና ሦስትነት አብራራልኝ' ወይም 'የጾም ጥቅም ምንድነው?') "
                "ብለው እዚህ ጽፈው ይላኩልኝ። ቦቱ በቀጥታ ከሊቃውንቱ መጻሕፍት መልሱን ያቀርብልዎታል።"
            )
            send_telegram_msg(chat_id, instruction)

# የቴሌግራም መልእክት መላኪያ ረዳት ተግባር
def send_telegram_msg(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

# 4. ጥይት የማይመታው የCatch-All ራውት (ሁለቱንም Webhook እና Scheduler ያስተናግዳል)
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # ቴሌግራም የዌብሁክ ጥያቄ ሲልክ
    if 'webhook' in path or path == 'api/webhook':
        try:
            update = request.get_json(force=True, silent=True) or {}
            handle_telegram_update(update)
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # መለጠፊያው (Scheduler) ሊንክ ሲጠራ
    elif 'post_scheduler' in path or path == 'api/post_scheduler':
        return post_to_channel()
    
    # መደበኛው ገጽ ሲጠራ
    eth_year, eth_month_num, eth_month_name, eth_day = get_ethiopian_date()
    return jsonify({
        "status": "healthy",
        "message": "ቤተሳይዳ መንፈሳዊ አገልግሎት በሰላም እየሰራ ነው!",
        "ethiopian_date": f"{eth_month_name} {eth_day} ቀን {eth_year} ዓ.ም"
    })

# 5. መልእክቱን ወደ ቴሌግራም ቻናል የሚልከው ዋናው ተግባር
def post_to_channel():
    CRON_SECRET = os.environ.get("CRON_SECRET")
    auth_header = request.headers.get('Authorization')
    if CRON_SECRET and auth_header != f"Bearer {CRON_SECRET}":
        return jsonify({"status": "unauthorized", "message": "ደህንነትዎ አልተረጋገጠም!"}), 401

    try:
        eth_year, eth_month_num, eth_month_name, eth_day = get_ethiopian_date()
        lesson = get_theological_teaching(eth_month_num, eth_day, eth_month_name)
        
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
        
        # በቻናሉ መልእክት ስር "ጥያቄ ለመጠየቅ" የሚል የንክኪ ቁልፍ መጨመር
        bot_username = os.environ.get("TELEGRAM_BOT_USERNAME", "YOUR_BOT_USERNAME") # ለምሳሌ @Bethesda_Bot
        reply_markup = {
            "inline_keyboard": [
                [{"text": "💬 ጥያቄ ለመጠየቅ / አስተያየት ለመስጠት", "url": f"https://t.me/{bot_username.replace('@', '')}?start=ask"}]
            ]
        }
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": telegram_message,
            "parse_mode": "Markdown",
            "reply_markup": reply_markup
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return jsonify({
                "status": "success", 
                "message": "ሰፊው የአብነት ትምህርት በስኬት ተለጥፏል!", 
                "date": f"{eth_month_name} {eth_day}"
            }), 200
        else:
            return jsonify({"status": "failed", "error": response.text}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()

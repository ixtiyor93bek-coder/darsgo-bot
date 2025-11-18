import os
import json
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Log sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables
BOT_TOKEN = "8293432727:AAEB5fQ5NkzhGWjKTeD2yNIzQRGUusXqyIQ"
GEMINI_API_KEY = "AIzaSyBm6VXej3TcecAbQhlELtiqmc0t1q3Hfy0"

# Gemini API sozlash
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Saqlash papkasi
STORAGE_DIR = "storage"
LESSONS_DIR = os.path.join(STORAGE_DIR, "lessons")
os.makedirs(LESSONS_DIR, exist_ok=True)

# Asosiy keyboard
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["📚 Dars Rejasi", "🔄 Mashq Yaratish"],
        ["📊 Test Tuzish", "🎨 Vizual Material"],
        ["👤 Mening Profilim", "ℹ️ Yordam"]
    ], resize_keyboard=True)

# Dars saqlash funksiyasi
def save_lesson(fan, mavzu, content):
    try:
        fan_dir = os.path.join(LESSONS_DIR, fan.lower())
        os.makedirs(fan_dir, exist_ok=True)
        
        filename = f"{mavzu.lower().replace(' ', '_')}.json"
        filepath = os.path.join(fan_dir, filename)
        
        lesson_data = {
            'fan': fan,
            'mavzu': mavzu,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'used_count': 0
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(lesson_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        logging.error(f"Dars saqlashda xato: {e}")
        return False

# AI dars rejasi yaratish
def generate_lesson_plan(fan, mavzu, sinf="9-sinf"):
    if not GEMINI_API_KEY:
        return "⚠️ AI xizmati hozir mavjud emas. Keyinroq urinib ko'ring."
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        {sinf} {fan} darsi uchun "{mavzu}" mavzusida 45 daqiqalik dars rejasi yarat.
        O'zbekiston o'quv dasturiga mos.
        Dars rejasi quyidagi strukturada bo'lsin:
        1. Dars maqsadi
        2. Dars turi  
        3. O'quv usullari
        4. Dars jarayoni
        5. Mustaqil ish
        6. Baholash
        
        O'zbek tilida javob bering.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        return f"⚠️ Dars rejasi yaratishda xato. Keyinroq urinib ko'ring."

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🚀 *Assalomu alaykum {user.first_name}!*\n\n"
        "🤖 *DarsGo Bot* - O'qituvchilarning aqlli yordamchisi\n\n"
        "📝 AI yordamida dars rejalari yarating\n"
        "🎯 Vaqtingizni tejang\n"
        "💡 Professional materiallar\n\n"
        "Quyidagi knopkalardan foydalaning:",
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )

# Knopkalarni qayta ishlash
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📚 Dars Rejasi":
        context.user_data['waiting_for_subject'] = True
        await update.message.reply_text(
            "📚 *Dars Rejasi Yaratish*\n\n"
            "Qaysi fan uchun dars rejasi kerak?\n"
            "Fan nomini yozing:\n"
            "*Masalan:* Matematika, Informatika, Fizika...",
            parse_mode='Markdown'
        )
    
    elif 'waiting_for_subject' in context.user_data:
        fan = text
        context.user_data['subject'] = fan
        context.user_data['waiting_for_subject'] = False
        context.user_data['waiting_for_topic'] = True
        await update.message.reply_text(
            f"✅ *{fan}* fanini tanladingiz!\n\n"
            f"Endi dars mavzusini yozing:\n"
            f"*Masalan:* 'Algebraik ifodalar', 'Photoshop asoslari'...",
            parse_mode='Markdown'
        )
    
    elif 'waiting_for_topic' in context.user_data:
        mavzu = text
        fan = context.user_data['subject']
        
        await update.message.reply_text("🔄 AI dars rejasini yaratmoqda... 10-20 soniya kuting ⏳")
        
        dars_rejasi = generate_lesson_plan(fan, mavzu)
        
        # Saqlash
        save_lesson(fan, mavzu, dars_rejasi)
        
        await update.message.reply_text(
            f"📚 *{fan}* - *{mavzu}*\n\n{dars_rejasi}",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
        # Tozalash
        context.user_data.clear()
    
    elif text == "👤 Mening Profilim":
        total_lessons = 0
        try:
            for fan in os.listdir(LESSONS_DIR):
                fan_path = os.path.join(LESSONS_DIR, fan)
                if os.path.isdir(fan_path):
                    total_lessons += len([f for f in os.listdir(fan_path) if f.endswith('.json')])
        except:
            total_lessons = 0
        
        await update.message.reply_text(
            f"👤 *Sizning Profilingiz*\n\n"
            f"📊 Saqlangan darslar: {total_lessons} ta\n"
            f"🆓 Holat: Bepul\n"
            f"🎯 Platforma: Kompyuter\n\n"
            f"*DarsGo* - O'qituvchilar uchun aqlli yordamchi!",
            parse_mode='Markdown'
        )
    
    elif text == "ℹ️ Yordam":
        await update.message.reply_text(
            "ℹ️ *DarsGo Bot Yordami*\n\n"
            "📚 *Dars Rejasi* - AI yordamida dars rejasi\n"
            "🔄 *Mashq Yaratish* - O'quvchilar uchun mashqlar\n"
            "📊 *Test Tuzish* - Test va savollar\n"
            "🎨 *Vizual Material* - Diagramma va rasmlar\n\n"
            "🚀 *Tez kunda yangi funksiyalar qo'shiladi!*",
            parse_mode='Markdown'
        )

# Asosiy dastur
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    print("🤖 Bot kompyuterda ishga tushdi!")
    application.run_polling()

if __name__ == "__main__":
    main()

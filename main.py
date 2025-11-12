import os
import json
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Log sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8443))

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
        # Fan papkasini yaratish
        fan_dir = os.path.join(LESSONS_DIR, fan.lower())
        os.makedirs(fan_dir, exist_ok=True)
        
        # Fayl nomi
        filename = f"{mavzu.lower().replace(' ', '_')}.json"
        filepath = os.path.join(fan_dir, filename)
        
        # Ma'lumotlarni saqlash
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

# Dars o'qish funksiyasi
def get_lesson(fan, mavzu):
    try:
        fan_dir = os.path.join(LESSONS_DIR, fan.lower())
        filename = f"{mavzu.lower().replace(' ', '_')}.json"
        filepath = os.path.join(fan_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        logging.error(f"Dars o'qishda xato: {e}")
        return None

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
        await update.message.reply_text(
            "📚 *Dars Rejasi Yaratish*\n\n"
            "Qaysi fan uchun dars rejasi kerak?\n"
            "Fan nomini yozing:\n"
            "*Masalan:* Matematika, Informatika, Fizika...",
            parse_mode='Markdown'
        )
    
    elif text == "👤 Mening Profilim":
        # Saqlangan darslar sonini hisoblash
        total_lessons = 0
        for fan in os.listdir(LESSONS_DIR):
            fan_path = os.path.join(LESSONS_DIR, fan)
            if os.path.isdir(fan_path):
                total_lessons += len([f for f in os.listdir(fan_path) if f.endswith('.json')])
        
        await update.message.reply_text(
            f"👤 *Sizning Profilingiz*\n\n"
            f"📊 Saqlangan darslar: {total_lessons} ta\n"
            f"🆓 Holat: Bepul\n"
            f"🎯 Platforma: Railway\n\n"
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
            "🚀 *Tez kunda yangi funksiyalar qo'shiladi!*\n\n"
            "📞 Admin: @sizning_username",
            parse_mode='Markdown'
        )
    
    else:
        # Saqlash tizimini test qilish
        if text in ["Matematika", "Informatika", "Fizika"]:
            test_content = f"Bu {text} faniga test dars rejasi"
            if save_lesson(text, "Test Mavzusi", test_content):
                await update.message.reply_text(
                    f"✅ '{text}' faniga test dars saqlandi!\n"
                    f"Saqlash tizimi ishlayapti! 🎉",
                    reply_markup=get_main_keyboard()
                )
        else:
            await update.message.reply_text(
                f"🔧 *{text}* funksiyasi tez orada qo'shiladi!\n\n"
                f"Hozircha dars rejasi yaratish uchun:\n"
                f"1. 📚 *Dars Rejasi* knopkasini bosing\n"
                f"2. Fan nomini yozing\n"
                f"3. AI yordamida dars tayyorlanadi!",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )

# Asosiy dastur
def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN topilmadi! Environment variable ni tekshiring.")
        return
    
    # Botni yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    # Webhook sozlash (Railway uchun)
    webhook_url = os.environ.get('RAILWAY_STATIC_URL')
    if webhook_url:
        logging.info(f"Webhook mode: {webhook_url}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{webhook_url}/{BOT_TOKEN}"
        )
    else:
        # Polling mode (development)
        logging.info("Polling mode ishga tushdi...")
        application.run_polling()

if __name__ == "__main__":
    main()

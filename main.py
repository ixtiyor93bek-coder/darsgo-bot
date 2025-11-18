import os
from telegram.ext import Application

BOT_TOKEN = "8293432727:AAEB5fQ5NkzhGWjKTeD2yNIzQRGUusXqyIQ"

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # ... sizning kodlaringiz ...
    
    print("🤖 Bot Render da ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()

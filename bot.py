from telegram.ext import ApplicationBuilder, CallbackQueryHandler, MessageHandler, filters
from handlers.message_handler import handle_user_message
from handlers.callback_handler import callback_handler_func  # твой callback handler
from handlers.start import start_handler 
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(start_handler)
app.add_handler(CallbackQueryHandler(callback_handler_func))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

print("Bot started")
app.run_polling()

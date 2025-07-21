# handlers/start.py
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from keyboards.main_keyboard import build_main_keyboard

async def start(update, context):
    keyboard = build_main_keyboard()
    await update.message.reply_text("Выберите категорию книг:", reply_markup=keyboard)

start_handler = CommandHandler("start", start)

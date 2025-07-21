from telegram import ReplyKeyboardMarkup, KeyboardButton

def build_main_keyboard():
    keyboard = [
        [KeyboardButton("📖 Прочитано"),KeyboardButton("🔄 В процессе")],
        [KeyboardButton("🕓 В планах"),KeyboardButton("➕ Добавить книгу")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

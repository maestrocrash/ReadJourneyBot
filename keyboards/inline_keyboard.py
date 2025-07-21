from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.parsing import get_title, get_year

def build_year_buttons(books):
    all_years = []
    for b in books:
        y = get_year(b)
        if isinstance(y, list):
            all_years.extend(y)
        elif y:
            all_years.append(y)
    years = sorted(set(all_years))
    buttons = [[InlineKeyboardButton(str(year), callback_data=f"year_{year}")] for year in years]
    return InlineKeyboardMarkup(buttons)

def build_book_buttons(books):
    buttons = [
        [InlineKeyboardButton(get_title(book), callback_data=f"book_{book['id']}")]
        for book in books
    ]
    return InlineKeyboardMarkup(buttons)

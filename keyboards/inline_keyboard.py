from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.parsing import get_title

def build_year_buttons(books):
    years = set()
    for book in books:
        props = book.get("properties", {})
        years_prop = props.get("Год", {}).get("multi_select", [])
        for year in years_prop:
            years.add(year.get("name"))
    buttons = [
        [InlineKeyboardButton(year, callback_data=f"year_{year}")]
        for year in sorted(years, reverse=True)
    ]
    return InlineKeyboardMarkup(buttons)

def build_book_buttons(books):
    buttons = [
        [InlineKeyboardButton(get_title(book), callback_data=f"book_{book['id']}")]
        for book in books
    ]
    return InlineKeyboardMarkup(buttons)

def build_author_buttons(authors):
    buttons = [
        [InlineKeyboardButton(author, callback_data=f"author_{author}")]
        for author in authors
    ]
    return InlineKeyboardMarkup(buttons)
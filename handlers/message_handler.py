from telegram import Update
from telegram.ext import ContextTypes
from notion.fetch_books import fetch_books_by_status
from keyboards.inline_keyboard import build_year_buttons, build_book_buttons
from utils.parsing import get_status_from_text
import logging
from notion.update_book import update_book_in_notion
from notion.create_book import create_book_in_notion  # Импорт функции создания книги

logger = logging.getLogger(__name__)

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    state = context.user_data.get("state")

    # Обработка ввода оценки книги
    if state == "awaiting_rating":
        try:
            rating = int(text)
            if rating < 1 or rating > 10:
                raise ValueError
            context.user_data["rating"] = rating
            context.user_data["state"] = "awaiting_comment"
            await update.message.reply_text("Оставьте комментарий к книге:")
        except ValueError:
            await update.message.reply_text("Введите число от 1 до 10 в качестве оценки.")
        return

    # Обработка ввода комментария к книге
    if state == "awaiting_comment":
        comment = text
        book_id = context.user_data.get("selected_book_id")
        rating = context.user_data.get("rating")

        await update_book_in_notion(book_id, {
            "Score": {"select": {"name": str(rating)}},
            "Comments": {"rich_text": [{"text": {"content": comment}}]},
            "Status": {"select": {"name": "Done"}}
        })

        await update.message.reply_text("Спасибо! Книга обновлена ✅")

        context.user_data.clear()
        return

    # Начало добавления новой книги — ввод названия
    if state == "awaiting_new_book_title":
        context.user_data["new_book_title"] = text
        context.user_data["state"] = "awaiting_new_book_author"
        await update.message.reply_text("Введите автора книги:")
        return

    # Ввод автора новой книги и создание в Notion
    if state == "awaiting_new_book_author":
        title = context.user_data.get("new_book_title")
        author = text

        success = await create_book_in_notion(
            title=title,
            author=author,
            status="Not started",
            year=2025
        )

        context.user_data.clear()

        if success:
            await update.message.reply_text(
                f"Книга «{title}» добавлена со статусом «Not started» и годом 2025."
            )
        else:
            await update.message.reply_text(
                "Произошла ошибка при добавлении книги. Попробуйте позже."
            )
        return

    # Обработка нажатия на кнопку "➕ Добавить книгу"
    if text == "➕ Добавить книгу":
        context.user_data["state"] = "awaiting_new_book_title"
        await update.message.reply_text("Введите название книги:")
        return

    # Обработка выбора статуса книг
    status = get_status_from_text(text)
    if not status:
        await update.message.reply_text("Пожалуйста, выберите одну из кнопок меню.")
        return

    books = await fetch_books_by_status(status)
    context.user_data["all_books"] = books

    if status == "Done":
        keyboard = build_year_buttons(books)
        await update.message.reply_text("Выберите год прочтения:", reply_markup=keyboard)
    else:
        keyboard = build_book_buttons(books)
        await update.message.reply_text("Список книг:", reply_markup=keyboard)

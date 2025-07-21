from telegram import Update
from telegram.ext import ContextTypes
from notion.fetch_books import fetch_books_by_status, fetch_authors
from keyboards.inline_keyboard import build_year_buttons, build_book_buttons, build_author_buttons
from utils.parsing import get_status_from_text
from notion.create_book import create_book_in_notion
from notion.update_book import update_book_in_notion
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # --- Добавляем обработку оценки ---
    if state == "awaiting_rating":
        try:
            rating = int(text)
            if not 1 <= rating <= 10:
                await update.message.reply_text("Оценка должна быть от 1 до 10.")
                return
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите число от 1 до 10.")
            return

        context.user_data["rating"] = rating
        context.user_data["state"] = "awaiting_comment"
        await update.message.reply_text("✍️ Введите ваш комментарий к книге:")
        return

    # --- Добавляем обработку комментария ---
    if state == "awaiting_comment":
        comment = text
        book_id = context.user_data.get("selected_book_id")
        rating = context.user_data.get("rating")

        success = await update_book_in_notion(book_id, {
            "Score": {"select": {"name": str(rating)}},
            "Comments": {"rich_text": [{"text": {"content": comment}}]},
            "Status": {"select": {"name": "Done"}}
        })

        context.user_data.clear()

        if success:
            await update.message.reply_text("✅ Оценка и комментарий сохранены.")
        else:
            await update.message.reply_text("❗ Ошибка при сохранении данных.")
        return

    # --- Начало добавления новой книги ---
    if text == "➕ Добавить книгу":
        context.user_data.clear()
        context.user_data["state"] = "awaiting_new_book_title"
        await update.message.reply_text("Введите название книги:")
        return

    # Ввод названия книги
    if state == "awaiting_new_book_title":
        context.user_data["new_book_title"] = text
        context.user_data["state"] = "awaiting_new_book_author"

        authors = await fetch_authors()
        context.user_data["available_authors"] = authors

        keyboard = build_author_buttons(authors)
        await update.message.reply_text(
            "Выберите автора из списка ниже или введите нового автора вручную:",
            reply_markup=keyboard
        )
        return

    # Ввод автора книги (текст или после выбора кнопки)
    if state == "awaiting_new_book_author":
        title = context.user_data.get("new_book_title")
        author = text
        year = datetime.now().year

        success = await create_book_in_notion(
            title=title,
            author=author,
            status="Not started",
            year=year
        )

        context.user_data.clear()

        if success:
            await update.message.reply_text(
                f"Книга «{title}» добавлена со статусом «Not started» и годом {year}."
            )
        else:
            await update.message.reply_text(
                "Произошла ошибка при добавлении книги. Попробуйте позже."
            )
        return

    # --- Обработка выбора статуса книг ---
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

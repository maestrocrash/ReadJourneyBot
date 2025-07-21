from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from notion.update_book import update_book_in_notion
from notion.create_book import create_book_in_notion
from keyboards.inline_keyboard import build_book_buttons
from utils.parsing import get_year, get_title

async def callback_handler_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    books = context.user_data.get("all_books", [])

    if data.startswith("year_"):
        year = data.split("_", 1)[1]
        filtered = [b for b in books if year in get_year(b)]
        count = len(filtered)
        keyboard = build_book_buttons(filtered)
        await query.edit_message_text(
            text=f"Книги за {year} год: всего прочитано {count} книг.",
            reply_markup=keyboard
        )
        return

    if data.startswith("book_"):
        book_id = data.split("_", 1)[1]
        book = next((b for b in books if b['id'] == book_id), None)
        if not book:
            await query.edit_message_text("Книга не найдена.")
            return

        status = book['properties'].get("Status", {}).get("select", {}).get("name", "")

        if status == "Not started":
            today = datetime.now().strftime("%Y-%m-%d")
            updated = await update_book_in_notion(book_id, {
                "Status": {"select": {"name": "In progress"}},
                "Date start": {"date": {"start": today}}
            })
            if updated:
                await query.edit_message_text("📚 Книга переведена в статус «В процессе».")
            else:
                await query.edit_message_text("❗ Ошибка при обновлении книги.")
            return

        if status == "In progress":
            today = datetime.now().strftime("%Y-%m-%d")
            updated = await update_book_in_notion(book_id, {
                "Status": {"select": {"name": "Done"}},
                "Date finished": {"date": {"start": today}}
            })
            if updated:
                context.user_data["selected_book_id"] = book_id
                context.user_data["state"] = "awaiting_rating"
                await query.edit_message_text(
                    "📚 Книга отмечена как прочитанная.\nВведите вашу оценку (от 1 до 10):"
                )
            else:
                await query.edit_message_text("❗ Ошибка при обновлении книги.")
            return

        # Детали книги
        title = get_title(book)
        author = book['properties'].get('Author', {}).get('select', {}).get('name', 'Неизвестен')
        score = book['properties'].get('Score', {}).get('select', {}).get('name', 'Нет оценки')
        comments_list = book['properties'].get('Comments', {}).get('rich_text', [])
        comments = "".join([c['plain_text'] for c in comments_list])
        years = [y['name'] for y in book['properties'].get('Год', {}).get('multi_select', [])]
        year_str = ", ".join(years)

        msg = (
            f"📚 <b>{title}</b>\n"
            f"✍️ Автор: {author}\n"
            f"⭐ Оценка: {score}\n"
            f"📅 Год: {year_str}\n"
            f"📝 Комментарий: {comments}"
        )
        await query.edit_message_text(msg, parse_mode="HTML")
        return

    if data.startswith("author_"):
        author = data[len("author_"):]  # Получаем автора из callback_data
        context.user_data["selected_author"] = author

        if context.user_data.get("state") == "awaiting_new_book_author":
            title = context.user_data.get("new_book_title")
            year = datetime.now().year

            success = await create_book_in_notion(
                title=title,
                author=author,
                status="Not started",
                year=year
            )

            context.user_data.clear()

            if success:
                await query.edit_message_text(f"Книга «{title}» добавлена ✅")
            else:
                await query.edit_message_text("Произошла ошибка. Попробуйте позже.")
        else:
            # Если не в режиме добавления книги, просто показываем выбранного автора
            await query.edit_message_text(f"Выбран автор: {author}")
        return

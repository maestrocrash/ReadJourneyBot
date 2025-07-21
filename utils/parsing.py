def get_year(book):
    years = book['properties'].get('Год', {}).get('multi_select', [])
    return [y['name'] for y in years]

def get_status_from_text(text):
    mapping = {
        "📖 Прочитано": "Done",
        "🔄 В процессе": "In progress",
        "🕓 В планах": "Not started"
    }
    return mapping.get(text)

def get_title(book):
    title_prop = book['properties'].get('Name', {}).get('title', [])
    if title_prop:
        # Собираем plain_text из всех частей и объединяем в одну строку
        return "".join(part['plain_text'] for part in title_prop)
    return "Без названия"
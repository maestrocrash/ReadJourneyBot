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
    title_parts = book['properties']['Name']['title']
    full_title = "".join(part['plain_text'] for part in title_parts)
    return full_title

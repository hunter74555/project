from vk_parser import VKParser
import time


def main():
    TOKEN = "..."
    GROUP_ID = "sushi74kop"

    parser = VKParser(TOKEN)

    print("Получаем ID группы...")
    group_data = parser._get_vk_data('groups.getById', {'group_id': GROUP_ID})
    if not group_data or 'error' in group_data:
        print("Ошибка получения ID группы")
        return

    numeric_id = group_data['response']['groups'][0]['id']
    print(f"ID группы: {numeric_id}")

    print("Загружаем товары...")
    items = parser.get_market_items(numeric_id, count=1000)  # Пробуем получить до 1000 товаров
    print(f"Всего получено товаров: {len(items)}")

    for i, item in enumerate(items, 1):
        parser.save_market_item(numeric_id, item)
        print(f"Сохранён товар {i}/{len(items)}: {item['title'][:50]}...")
        time.sleep(0.3)


if __name__ == "__main__":
    main()

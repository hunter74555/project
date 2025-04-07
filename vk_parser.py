import sqlite3
import requests
import time  # Добавлен импорт модуля time
from pathlib import Path


class VKParser:
    def __init__(self, token):
        self.token = token
        self.db_path = Path("db/vk_groups.db")
        self.db_path.parent.mkdir(exist_ok=True)
        Path("img").mkdir(exist_ok=True)
        self._create_tables()

    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS market_items")
            cursor.execute('''
            CREATE TABLE market_items (
                id INTEGER PRIMARY KEY,
                group_id INTEGER,
                title TEXT,
                description TEXT,
                price REAL,
                currency TEXT,
                photo_path TEXT
            )''')

    def _get_vk_data(self, method, params):
        params.update({'access_token': self.token, 'v': '5.199'})
        try:
            response = requests.get(f"https://api.vk.com/method/{method}", params=params, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return None

    def get_market_items(self, group_id, count=200):
        all_items = []
        offset = 0

        while len(all_items) < count:
            data = self._get_vk_data('market.get', {
                'owner_id': f"-{group_id}",
                'count': min(200, count - len(all_items)),
                'offset': offset,
                'extended': 0
            })

            if not data or 'error' in data:
                error_msg = data.get('error', {}).get('error_msg', 'Unknown error') if data else 'No data received'
                print(f"Ошибка API: {error_msg}")
                break

            items = data.get('response', {}).get('items', [])
            if not items:
                break  # Больше нет товаров

            all_items.extend(items)
            offset += len(items)
            print(f"Получено {len(items)} товаров (всего: {len(all_items)})")

            if len(items) < 200:
                break  # Это была последняя порция товаров

            time.sleep(1)  # Задержка между запросами

        return all_items

    def save_market_item(self, group_id, item):
        try:
            price = float(item['price']['amount']) / 100
        except (ValueError, KeyError, TypeError):
            price = 0.0

        photo_path = ""
        if 'photos' in item and item['photos']:
            try:
                photo_url = item['photos'][0]['sizes'][-1]['url']
                photo_path = f"img/item_{item['id']}.jpg"
                response = requests.get(photo_url, timeout=10)
                with open(photo_path, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Ошибка загрузки фото: {e}")
                photo_path = ""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO market_items VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'],
                group_id,
                item['title'],
                item.get('description', ''),
                price,
                item['price']['currency']['name'],
                photo_path
            ))
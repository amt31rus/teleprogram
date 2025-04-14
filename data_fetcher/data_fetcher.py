import requests
import random
from typing import Optional, List
import logging


class DataFetcher:
    """Класс для безопасной загрузки HTML-страниц с ротацией User-Agent"""

    def __init__(self, timeout: int = 15, user_agents: Optional[List[str]] = None):
        self.session = requests.Session()
        self.timeout = timeout
        self.user_agents = user_agents or [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        ]
        self._setup_session()

    def _setup_session(self):
        """Настройка HTTP-сессии со случайным User-Agent"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        self.session.headers.update(headers)

    def fetch_data(self, url: str) -> Optional[str]:
        """Безопасная загрузка HTML-контента с обработкой ошибок"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Проверяем, что получили HTML, а не страницу с ошибкой
            if 'text/html' not in response.headers.get('Content-Type', ''):
                logging.warning(f"Получен не HTML-контент от {url}")
                return None

            return response.text
        except requests.RequestException as e:
            logging.warning(f"Ошибка запроса к {url}: {str(e)}")
            return None
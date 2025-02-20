import requests
from abc import ABC, abstractmethod

class BaseHTTPClient(ABC):
    '''Базовый класс для HTTP-клиентов, работающих с API'''

    BASE_URL = ''  # КАЖДЫЙ ПОДКЛАСС ЗАДАЁТ СВОЮ ССЫЛКУ

    HEADERS = {
        'Content-Type': 'application/json'
    }

    def __init__(self, api_key: str = None):
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['X-Master-Key'] = api_key

    def _request(self, method: str, endpoint: str, data=None):
        """Универсальный метод для отправки HTTP-запросов."""
        url = f'{self.BASE_URL}{endpoint}'
        response = requests.request(method, url, json=data, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Ошибка {response.status_code}: {response.text}')

    @abstractmethod
    def process_request(self, *args, **kwargs):
        """Абстрактный метод, который должны реализовать наследники"""
        pass


class CloudflareAI(BaseHTTPClient):
    """Клиент для работы с LLM API Cloudflare."""
    BASE_URL = "https://api.cloudflare.com/v1/ai"

    def __init__(self, api_key: str, account_id: str, model_name: str):
        super().__init__(api_key)  # Передаём API-ключ в базовый класс
        self.account_id = account_id
        self.model_name = model_name

    def get_task_solution(self, question: str) -> str:
        """Отправляет вопрос в Cloudflare AI и получает ответ."""
        endpoint = f"/{self.account_id}/ai/{self.model_name}/chat"
        data = {"messages": [{"role": "user", "content": question}]}
        response = self._request("POST", endpoint, data)
        return response.get("result", "Решение не найдено")

    def process_request(self, question: str):
        return self.get_task_solution(question)


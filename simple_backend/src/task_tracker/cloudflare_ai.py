import requests

# Кастомные исключения с переопределёнными сообщениями
class CloudflareAIError(Exception):
    """Базовое исключение для CloudflareAI"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class CloudflareAPIError(CloudflareAIError):
    """Ошибка при запросе к Cloudflare API (сетевая ошибка, недоступность API и тд)"""
    def __init__(self, message: str = "Ошибка при запросе к Cloudflare API"):
        super().__init__(message)

class CloudflareAuthError(CloudflareAPIError):
    """Ошибка авторизации (неверный токен, недостаточно прав)"""
    def __init__(self, message: str = "Ошибка авторизации: неверный токен или недостаточно прав"):
        super().__init__(message)

class CloudflareRateLimitError(CloudflareAPIError):
    """Ошибка превышения лимитов запросов"""
    def __init__(self, message: str = "Превышен лимит запросов к Cloudflare AI"):
        super().__init__(message)

class CloudflareServerError(CloudflareAPIError):
    """Ошибка сервера Cloudflare (5xx ошибки)"""
    def __init__(self, message: str = "Ошибка сервера Cloudflare (5xx ошибки)"):
        super().__init__(message)

class CloudflareResponseError(CloudflareAIError):
    """Ошибка обработки ответа от Cloudflare (некорректные данные)"""
    def __init__(self, message: str = "Ответ от Cloudflare некорректен или не содержит ожидаемые данные"):
        super().__init__(message)

class CloudflareTimeoutError(CloudflareAPIError):
    """Ошибка тайм-аута запроса"""
    def __init__(self, message: str = "Запрос к Cloudflare AI превысил время ожидания"):
        super().__init__(message)


# Класс для работы с Cloudflare AI
class CloudflareAI:
    API_TOKEN = "961nKVFFc-G_OTnKFNXoKiU3e2eB0t2I6fNMyeQx"
    ACCOUNT_ID = "6c0d918e2fc93460e26747bf43f6d7c9"
    MODEL_NAME = "@cf/meta/llama-2-7b-chat-int8"
    URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL_NAME}"
    HEADERS = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    @classmethod
    def get_task_solution(cls, task_text: str) -> str:
        """Отправляет задачу в LLM и получает объяснение."""
        data = {
            "messages": [
                {"role": "system", "content": "Ты помощник, который объясняет, как решать задачи."},
                {"role": "user", "content": f"Как решить задачу: {task_text}?"}
            ]
        }

        try:
            # Отправка запроса к API
            response = requests.post(cls.URL, json=data, headers=cls.HEADERS, timeout=10)
            response.raise_for_status()  # Проверка статуса ответа

            result = response.json().get("result", {}).get("response")
            if not result:
                raise CloudflareResponseError("Ответ от AI не содержал ожидаемого результата.")

            return result

        except requests.exceptions.Timeout:
            raise CloudflareTimeoutError("Запрос к Cloudflare AI превысил время ожидания.")

        except requests.exceptions.HTTPError as e:
            status_code = response.status_code

            if status_code == 401 or status_code == 403:
                raise CloudflareAuthError(f"Ошибка авторизации: {status_code} (Проверь API-токен).")
            elif status_code == 429:
                raise CloudflareRateLimitError("Превышен лимит запросов к Cloudflare AI.")
            elif 500 <= status_code < 600:
                raise CloudflareServerError(f"Ошибка сервера Cloudflare: {status_code}. Попробуйте позже.")
            else:
                raise CloudflareAPIError(f"Неизвестная ошибка API: {status_code}.")

        except requests.exceptions.RequestException as e:
            raise CloudflareAPIError(f"Ошибка при запросе к Cloudflare: {e}")



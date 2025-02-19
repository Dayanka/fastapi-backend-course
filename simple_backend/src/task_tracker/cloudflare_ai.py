import requests

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
            response = requests.post(cls.URL, json=data, headers=cls.HEADERS)
            # Проверка статуса ответа от Cloudflare
            if response.status_code == 200:
                result = response.json().get("result", {}).get("response")
                if result:
                    return result
                else:
                    return "Ответ от AI не содержал ожидаемого результата."
            else:
                return f"Ошибка API: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            # Логирование ошибки, если запрос не удался
            return f"Ошибка при запросе к Cloudflare: {e}"



from cloudflare_ai import CloudflareAI
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Константы для работы с jsonbin.io
BIN_ID = "67b382a8ad19ca34f8076668"
API_KEY = "$2a$10$uVthqN2OueSJ8FOe/QGTJOMq3mnvf5qNFM7hNcrNI7ub8YE4MYTuW"
BASE_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

app = FastAPI()

class Task(BaseModel):
    title: str
    status: str
    solution: str = ""  # По умолчанию пустое, если AI не ответил

class TaskStorage:
    """Клиент для работы с задачами (JSON-хранилище)."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _fetch_tasks(self):
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json()["record"].get("tasks", [])
        raise HTTPException(status_code=500, detail="Ошибка при получении данных")

    def _update_tasks(self, tasks):
        response = requests.put(BASE_URL, json={"tasks": tasks}, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка при обновлении данных")

    def get_all_tasks(self) -> List[dict]:
        return self._fetch_tasks()

    def add_task(self, task: dict) -> dict:
        tasks = self._fetch_tasks()
        task["id"] = len(tasks) + 1
        tasks.append(task)
        self._update_tasks(tasks)
        return task

    def update_task(self, task_id: int, updated_task: dict) -> dict:
        tasks = self._fetch_tasks()
        for task in tasks:
            if task["id"] == task_id:
                task.update(updated_task)
                self._update_tasks(tasks)
                return task
        raise HTTPException(status_code=404, detail="Задача не найдена")

    def delete_task(self, task_id: int) -> dict:
        tasks = self._fetch_tasks()
        new_tasks = [task for task in tasks if task["id"] != task_id]

        if len(new_tasks) == len(tasks):
            raise HTTPException(status_code=404, detail="Задача не найдена")

        self._update_tasks(new_tasks)
        return {"message": "Задача удалена"}

# Создаём объект для работы с задачами
task_storage = TaskStorage(API_KEY)

# Создаём объект CloudflareAI
cloudflare_ai = CloudflareAI(api_key=API_KEY, account_id="your_account_id", model_name="text-generation")

@app.get('/tasks', response_model=List[Task])
def get_tasks():
    return task_storage.get_all_tasks()

@app.post('/task', response_model=Task)
def create_task(task: Task):
    solution = cloudflare_ai.get_task_solution(task.title)  # Вызываем метод у объекта
    task_dict = task.dict()
    task_dict["solution"] = solution
    return task_storage.add_task(task_dict)

@app.put('/tasks/{task_id}', response_model=Task)
def update_task(task_id: int, task: Task):
    task_dict = task.dict()
    task_dict["solution"] = cloudflare_ai.get_task_solution(task.title)  # Вызываем метод у объекта
    return task_storage.update_task(task_id, task_dict)

@app.delete('/tasks/{task_id}')
def delete_task(task_id: int):
    return task_storage.delete_task(task_id)

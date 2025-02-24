from cloudflare_ai import CloudflareAI  # Импортируем наш класс
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


BIN_ID = os.getenv("BIN_ID")
API_KEY = os.getenv("API_KEY")
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
    """Класс для работы с удалённым JSON-хранилищем."""

    @staticmethod
    def _fetch_tasks():
        """Получить список задач из jsonbin.io."""
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json()["record"].get("tasks", [])
        raise HTTPException(status_code=500, detail="Ошибка при получении данных")

    @staticmethod
    def _update_tasks(tasks):
        """Обновить список задач в jsonbin.io."""
        data = {"tasks": tasks}
        response = requests.put(BASE_URL, json=data, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка при обновлении данных")

    def get_all_tasks(self) -> List[dict]:
        return self._fetch_tasks()

    def add_task(self, task: dict) -> dict:
        tasks = self._fetch_tasks()
        task_id = len(tasks) + 1
        task["id"] = task_id
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

        if len(new_tasks) == len(tasks):  # Если длина не изменилась — задачи не было
            raise HTTPException(status_code=404, detail="Задача не найдена")

        self._update_tasks(new_tasks)
        return {"message": "Задача удалена"}

# Создаём объект для работы с задачами
task_storage = TaskStorage()

@app.get('/tasks', response_model=List[Task])
def get_tasks():
    return task_storage.get_all_tasks()

@app.post('/task', response_model=Task)
def create_task(task: Task):
    # Получаем решение через CloudflareAI
    solution = CloudflareAI.get_task_solution(task.title)
    task_dict = task.dict()
    task_dict["solution"] = solution  # Добавляем решение в задачу
    return task_storage.add_task(task_dict)  # Сохраняем задачу с решением

@app.put('/tasks/{task_id}', response_model=Task)
def update_task(task_id: int, task: Task):
    # Получаем решение через CloudflareAI
    task_dict = task.dict()
    task_dict["solution"] = CloudflareAI.get_task_solution(task.title)
    return task_storage.update_task(task_id, task_dict)  # Обновляем задачу с решением

@app.delete('/tasks/{task_id}')
def delete_task(task_id: int):
    return task_storage.delete_task(task_id)


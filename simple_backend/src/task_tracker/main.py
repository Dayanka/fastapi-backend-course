
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from pathlib import Path

TASKS_FILE = Path("tasks.json")

app = FastAPI()

# Класс для работы с задачами
class TaskStorage:
    def __init__(self, file_path: Path = TASKS_FILE):
        self.file_path = file_path

    def _read_tasks(self) -> List[dict]:
        #Чтение задач из файла
        if self.file_path.exists():
            with open(self.file_path, "r") as file:
                return json.load(file)
        return []

    def _write_tasks(self, tasks: List[dict]):
        #Запись задач в файл
        with open(self.file_path, "w") as file:
            json.dump(tasks, file, indent=4)

    def get_all_tasks(self) -> List[dict]:
        #Возвращает все задачи
        return self._read_tasks()

    def add_task(self, task: dict) -> dict:
        #Добавление новой задачи
        tasks = self._read_tasks()
        task_id = len(tasks) + 1
        task["id"] = task_id
        tasks.append(task)
        self._write_tasks(tasks)
        return task

    def update_task(self, task_id: int, updated_task: dict) -> dict:
        #Обновление существующей задачи
        tasks = self._read_tasks()
        for task in tasks:
            if task["id"] == task_id:
                task.update(updated_task)
                self._write_tasks(tasks)
                return task
        return {"error": "task not found"}

    def delete_task(self, task_id: int) -> dict:
        #Удаление задачи
        tasks = self._read_tasks()
        tasks = [task for task in tasks if task["id"] != task_id]
        self._write_tasks(tasks)
        return {"message": "task deleted successfully"}

# Создаем объект для работы с задачами
task_storage = TaskStorage()

class Task(BaseModel):
    title: str
    status: str

@app.get('/tasks', response_model=List[Task])
def get_tasks():
    tasks = task_storage.get_all_tasks()  # Получаем все задачи
    return tasks

@app.post('/task', response_model=Task)
def create_task(task: Task):
    new_task = task.dict()  # Преобразуем Pydantic объект в обычный словарь
    created_task = task_storage.add_task(new_task)  # Добавляем задачу в хранилище
    return created_task

@app.put('/tasks/{task_id}', response_model=Task)
def update_task(task_id: int, task: Task):
    updated_task = task.dict()  # Преобразуем Pydantic объект в обычный словарь
    result = task_storage.update_task(task_id, updated_task)  # Обновляем задачу
    if "error" in result:
        return result  # Если ошибка, возвращаем её
    return result

@app.delete('/tasks/{task_id}')
def delete_task(task_id: int):
    result = task_storage.delete_task(task_id)  # Удаляем задачу
    return result



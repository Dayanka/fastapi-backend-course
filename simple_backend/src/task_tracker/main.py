import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from pathlib import Path

app = FastAPI()

TASKS_FILE = Path("tasks.json")

class Task(BaseModel):
    title: str
    status: str


def read_tasks_from_file():
    if TASKS_FILE.exists():
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    return []

def write_tasks_to_file(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

@app.get('/tasks', response_model=List[Task])
def get_tasks():
    tasks = read_tasks_from_file()
    return tasks


@app.post('/task', response_model=Task)
def create_task(task: Task):
    tasks = read_tasks_from_file()
    task_id = len(tasks) + 1
    new_task = task.dict()
    new_task['id'] = task_id
    tasks.append(new_task)
    write_tasks_to_file(tasks)  
    return new_task


@app.put('/tasks/{task_id}', response_model=Task)
def update_task(task_id: int, task: Task):
    tasks = read_tasks_from_file()
    for t in tasks:
        if t['id'] == task_id:
            t['title'] = task.title
            t['status'] = task.status
            write_tasks_to_file(tasks)  
            return t
    return {'error': 'task not found'}


@app.delete('/tasks/{task_id}')
def delete_task(task_id: int):
    tasks = read_tasks_from_file()
    tasks = [t for t in tasks if t['id'] != task_id]
    write_tasks_to_file(tasks)
    return {'message': 'task deleted successfully'}

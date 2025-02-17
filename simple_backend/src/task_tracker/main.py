

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

tasks = []

class Task(BaseModel):
    title: str
    status: str

@app.get('/tasks', response_model=List[Task])
def get_tasks():
    return tasks


@app.post('/task', response_model=Task)
def create_task(task: Task):
    task_id = len(tasks) +1
    new_task = task.dict()
    new_task['id'] = task_id
    tasks.append(new_task)
    return new_task

@app.put('/tasks/{task_id}', response_model=Task)
def update_task(task_id: int, task: Task):
    for t in tasks:
        if t['id']==task_id:
            t['title'] = task.title
            t['status'] = task.status
            return t
    return {'error': 'task not found'}

@app.delete('/tasks/{task_id}')
def delete_task(task_id:int):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return {'message': 'task deleted successfully'}




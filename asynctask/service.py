from asynctask.model import Task, TaskResponse
from storage.service import StorageService


class TaskStorage(StorageService):

    def __init__(self, directory):
        super().__init__(directory)

    def store_task(self, task: Task):
        self.store(task, task.id)

    def list_tasks(self):
        return [t.replace(".json", "") for t in self.list()]

    def load_task(self, id):
        data = self.load(id)
        if data:
            return TaskResponse.from_dict(data)
        else:
            return None

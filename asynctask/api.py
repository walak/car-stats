import logging
from threading import Thread, RLock
from time import sleep

from asynctask.model import Task, TaskExecution, ExecutedTask
from asynctask.service import TaskStorage


class TaskExecutor(Thread):

    def __init__(self, number_of_threads=5, task_storage: TaskStorage = None):
        super().__init__()
        self.task_storage = task_storage
        self.threads = [WorkerThread(i + 1, task_storage) for i in range(0, number_of_threads)]
        self.task_queue = []
        self.queue_lock = RLock()
        self.stopped = False
        self.log = logging.getLogger("TaskExecutor")

    def start(self) -> None:
        [w.start() for w in self.threads]
        super().start()
        self.log.info("TaskExecutor started with [ %d ] threads" % len(self.threads))

    def execute(self, task: Task):
        self.queue_lock.acquire()
        task_execution = TaskExecution(task)
        self.task_queue.append(task_execution)
        self.log.info("Queued task [ %s ] to execution. Queue length [ %d ]" % (task.id, len(self.task_queue)))
        self.queue_lock.release()
        if self.task_storage:
            self.task_storage.store_task(task)
        return task_execution

    def run(self):
        while not self.stopped:
            self.queue_lock.acquire()
            if self.task_queue and self.find_free_executor():
                executor = self.find_free_executor()
                task_to_execute = self.task_queue.pop(0)
                executor.execute_task(task_to_execute)
                self.log.info("Task [ %s ] was passed to worker thread" % task_to_execute.task.id)
                self.queue_lock.release()
            else:
                self.queue_lock.release()
                sleep(0.1)

    def find_free_executor(self):
        for worker in self.threads:
            if not worker.task_execution:
                return worker
        return None

    def get_stats(self):
        return {
            "threads": len(self.threads),
            "queue-size": len(self.task_queue),
            "workers": [w.get_worker_stats() for w in self.threads]
        }


class WorkerThread(Thread):

    def __init__(self, id, task_storage: TaskStorage = None):
        super().__init__()
        self.task_storage = task_storage
        self.lock = RLock()
        self.log = logging.getLogger("WorkerThread-%d" % id)
        self.setName("WorkerThread-%d" % id)
        self.task_execution = None
        self.finished = False
        self.daemon = True

    def execute_task(self, task: TaskExecution):
        self.lock.acquire()
        self.task_execution = task
        self.log.info("Received task [ %s ]", task.task.id)
        self.lock.release()

    def run(self):
        while not self.finished:
            self.lock.acquire()
            if self.task_execution is not None:
                try:
                    self.log.info("Executing task [ %s ]" % self.task_execution.task.id)
                    result = self.task_execution.task.execute()
                    self.log.info("Task [ %s ] executed succesfully " % self.task_execution.task.id)
                    executed_task = ExecutedTask(result=result,
                                                 success=True,
                                                 id=self.task_execution.task.id,
                                                 type=self.task_execution.task.__class__.__name__)
                    self.task_execution.set_task(executed_task)
                except Exception as e:
                    self.log.error("Error executing task [ %s ]!" % self.task_execution.task.id, exc_info=1)
                    executed_task = ExecutedTask(result=e,
                                                 success=False,
                                                 id=self.task_execution.task.id,
                                                 type=self.task_execution.task.__class__.__name__)
                    self.task_execution.set_task(executed_task)
                finally:
                    if self.task_storage:
                        self.task_storage.store_task(self.task_execution.task)
                    self.task_execution = None
                    self.lock.release()
            else:
                self.lock.release()
                sleep(0.1)

    def get_worker_stats(self):
        return {
            "name": self.name,
            "busy": True if self.task_execution else False,
            "task-type": self.task_execution.task.type if self.task_execution else "None",
            "task": self.task_execution.task.id if self.task_execution else "None",
            "progress": self.__get_task_progress() if self.task_execution else "None"
        }

    def __get_task_progress(self):
        if hasattr(self.task_execution.task, 'progress'):
            return self.task_execution.task.progress
        else:
            return "(progress not reported)"


class ArtificialTask(Task):
    TASK_ID = 1

    def __init__(self, i):
        super().__init__()
        self.i = i
        self.j = ArtificialTask.TASK_ID
        ArtificialTask.TASK_ID += 1

    def execute(self):
        sleep(self.i)
        print("Task [ %s ] %d executed (%d)" % (self.id, self.j, self.i))
        return self.i

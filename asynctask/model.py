from _thread import RLock
from random import randint
from time import sleep


class Task:
    def __init__(self):
        self.result = None
        self._success = False
        self._finished = False
        self.type = self.__class__.__name__
        self.id = self.__generate_id()
        self.progress = None

    def execute(self):
        # Dummy implementation, override
        return self.result

    def is_success(self):
        return self._success

    def is_finished(self):
        return self._finished

    def __generate_id(self):
        name = "%s-%s-%s"
        parts = []
        for i in range(0, 3):
            parts.append("%d%d%d%d" % (randint(0, 9), randint(0, 9), randint(0, 9), randint(0, 9)))

        return name % tuple(parts)

    def __getstate__(self):
        return {
            "result": self.result,
            "_success": self._success,
            "_finished": self._finished,
            "type": self.type,
            "id": self.id,
            "progress": self.progress
        }


class TaskInfo:
    def __init__(self, task):
        self.result = task.result
        self.success = task.is_success()
        self.finished = task.is_finished()
        self.type = task.type
        self.id = task.id


class InterruptibleTask(Task):

    def __init__(self):
        super().__init__()
        self.interrupted = False
        self.interruption_lock = RLock()

    def try_interrupt(self):
        self.interruption_lock.acquire()
        self.interrupted = True
        self.interruption_lock.release()

    def should_interrupt(self):
        try:
            self.interruption_lock.acquire()
            return self.interrupted
        finally:
            self.interruption_lock.release()

    def __getstate__(self):
        d = super().__getstate__()
        d.update({
            "interrupted": self.interrupted
        })

        return d


class FunctionCallTask(Task):

    def __init__(self, func, **kwargs):
        super().__init__()
        self.function = func
        self.args = kwargs

    def execute(self):
        return self.function(**self.args)

    def __getstate__(self):
        d = super().__getstate__()
        d.update({
            "function": self.function.__name__,
            "args": self.args
        })


class TaskResponse:

    def __init__(self, id, type, result, success, finished):
        self.id = id
        self.type = type
        self.result = result
        self.success = success
        self.finished = finished

    @staticmethod
    def from_dict(dct):
        return TaskResponse(
            id=dct['id'],
            type=dct['type'],
            result=dct['result'],
            success=dct['_success'],
            finished=dct['_finished']
        )


class ExecutedTask(Task):

    def __init__(self, result, success, id, type):
        super().__init__()
        self.result = result
        self._success = success
        self._finished = True
        self.id = id
        self.type = type

    def execute(self):
        return self.result


class TaskExecution:

    def __init__(self, task: Task):
        self.task = task
        self.lock = RLock()

    def get_task(self):
        try:
            self.lock.acquire()
            return self.task
        finally:
            self.lock.release()

    def set_task(self, task):
        self.lock.acquire()
        self.task = task
        self.lock.release()

    def get_task_or_wait(self):
        while True:
            self.lock.acquire()
            if self.task.is_finished():
                self.lock.release()
                return self.task
            else:
                self.lock.release()
                sleep(0.1)

    def is_finished(self):
        try:
            self.lock.acquire()
            return self.task.is_finished()
        finally:
            self.lock.release()

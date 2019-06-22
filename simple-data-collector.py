import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, Response

from asynctask.api import TaskExecutor
from asynctask.service import TaskStorage
from carstats.api import GetCarsToXls, CarBlotterTask
from files.service import FileService
from httpapi.methods import get_json_response, get_binary_response

logFormatter = logging.Formatter('%(asctime)-15s [ %(name)s ] %(message)s')
logging.basicConfig(level=logging.INFO)
rootLogger = logging.getLogger()
rootLogger.handlers.clear()

fileHandler = TimedRotatingFileHandler("simple-data.log", when='midnight')
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.INFO)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

app = Flask(__name__)

TASK_STORE = TaskStorage("resources/data/task")

TASK_EXECUTOR = TaskExecutor(task_storage=TASK_STORE)

FILE_SERVICE = FileService("resources/data/files")


@app.route("/car/scrap/<brand>/<model>")
def get_car_stats(brand, model):
    task = GetCarsToXls(brand, model, TASK_EXECUTOR, FILE_SERVICE)
    task_execution = TASK_EXECUTOR.execute(task)
    return get_json_response(task_execution.task)


@app.route("/task")
def list_tasks():
    return get_json_response(TASK_STORE.list_tasks())


@app.route("/task/<task>")
def get_task(task):
    task = TASK_STORE.load_task(task)
    if task:
        return get_json_response(task)
    else:
        return Response(status=404)


@app.route("/task/<task>/result")
def get_task_result(task):
    task = TASK_STORE.load_task(task)
    if task and task.finished:
        return get_json_response(task.result)
    else:
        return Response(status=404)


@app.route("/download/<file_id>")
def get_file(file_id):
    file_stream = FILE_SERVICE.get_open_file_handle(file_id)
    return get_binary_response(file_stream, file_id)


@app.route("/async/status")
def async_stats():
    return get_json_response(TASK_EXECUTOR.get_stats())


if __name__ == "__main__":
    CAR_SAVE_TASK = CarBlotterTask()
    TASK_EXECUTOR.start()
    TASK_EXECUTOR.execute(CAR_SAVE_TASK)
    app.run(host="0.0.0.0", port=8080, threaded=True)

    TASK_EXECUTOR.stop()

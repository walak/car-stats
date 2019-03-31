import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, Response
from jsonpickle import dumps
from werkzeug.wsgi import FileWrapper

from asynctask.api import TaskExecutor
from asynctask.service import TaskStorage
from carstats.api import GetCarsToXls
from files.service import FileService

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

LOG = logging.getLogger("webapp")

app = Flask(__name__)


TASK_STORE = TaskStorage("resources/data/task")

TASK_EXECUTOR = TaskExecutor(task_storage=TASK_STORE)

FILE_SERVICE = FileService("resources/data/files")


def get_json_response(response_body):
    json = dumps(response_body, False)
    return Response(response=json,
                    mimetype="application/json")


def get_xlsx_response(response_body, filename):
    response_body.seek(0)
    wrapped = FileWrapper(response_body)
    return Response(response=wrapped,
                    direct_passthrough=True,
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "inline; filename=\"%s\"" % filename}
                    )


def get_binary_response(response_stream, filename):
    wrapped = FileWrapper(response_stream)
    return Response(response=wrapped,
                    direct_passthrough=True,
                    mimetype="application/octet-stream",
                    headers={"Content-Disposition": "attachment; filename=\"%s\"" % filename}
                    )


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
    TASK_EXECUTOR.start()

    app.run(host="0.0.0.0", port=8080, threaded=True)

    TASK_EXECUTOR.stop()
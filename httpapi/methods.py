from flask import Response
from jsonpickle import dumps
from werkzeug.wsgi import FileWrapper


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

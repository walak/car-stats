import logging
from http.client import HTTPConnection, HTTPSConnection

LOG = logging.getLogger("httpapi")


def create_http_connection(host, port=None):
    return HTTPConnection(host, port)


def create_https_connection(host, port=None):
    return HTTPSConnection(host, port)


def build_params(params):
    return "&".join(["%s=%s" % (k, str(v)) for k, v in params.items()])


def raw(connection: HTTPConnection, url, method, headers, body, **parameters):
    params = ""
    if parameters:
        params = "?" + build_params(parameters)

    connection.request(method, url + params, body=body, headers=headers)
    return connection.getresponse()


def raw_get(connection, url, headers={}, **parameters):
    return raw(connection, url, "GET", headers, None, **parameters)


def raw_post(connection, url, headers={}, body=None, **parameters):
    return raw(connection, url, "POST", headers, body, **parameters)


def get(connection: HTTPConnection, url, **parameters):
    response = raw_get(connection, url, **parameters)
    if response.status == 200:
        data = response.read()
        return data
    if response.status == 301:
        redirected_url = response.headers.get('Location')
        LOG.info("Redirected to [ %s ]" % redirected_url)
        response.read()
        return get(connection, redirected_url)
    else:
        LOG.error("Error on HTTP call: %d %s" % (response.status, response.reason))
        return None

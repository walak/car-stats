from sqlite3 import connect, Connection
from threading import RLock

CONNECTION = None
LOCK = RLock()


def synchronized(func):
    def guard(*args, **kwargs):
        try:
            LOCK.acquire()
            return func(*args, **kwargs)
        finally:
            LOCK.release()

    return guard


@synchronized
def open_connection(database):
    global CONNECTION
    CONNECTION = connect(database)


@synchronized
def close_connection():
    global CONNECTION
    CONNECTION.close()
    CONNECTION = None


@synchronized
def execute(query, expected_return=False):
    cursor = CONNECTION.cursor()
    cursor.execute(query)
    if expected_return:
        return cursor.fetchall()
    return None


@synchronized
def execute_many(queries):
    crs = CONNECTION.cursor()
    for query in queries:
        crs.execute(query)


@synchronized
def execute_file(sql_file):
    with open(sql_file) as file:
        csr = CONNECTION.cursor()
        csr.executescript(file.read())


if __name__ == "__main__":
    open_connection("test")
    execute_file("../cars.sql")
    close_connection()

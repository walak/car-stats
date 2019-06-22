INSERT_QUERY = "INSERT INTO `%s`(%s) VALUES (%s)"


def wrap_value(val):
    return '\'%s\'' % str(val) if val is not None else 'NULL'


def wrap_column(name):
    return '`%s`' % name


def create_insert(table, values: dict):
    cols = []
    vals = []
    for it in values.items():
        cols.append(it[0])
        vals.append(it[1])
    columns_string = ", ".join([wrap_column(c) for c in cols])
    values_string = ", ".join([wrap_value(v) for v in vals])
    return INSERT_QUERY % (table, columns_string, values_string)


def create_insert_for_object(table, obj):
    return create_insert(table, obj.__dict__)

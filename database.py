# coding:utf-8
from collections import defaultdict
import psycopg2
import sys
import traceback
import random

__author__ = '4ikist'

db_name = db_user = db_pass = 'test'
min_node_count = 100
max_node_count = 200

connection = None




def _create_connection():
    global connection
    if connection and connection.closed == 0:
        return connection
    else:
        try:
            connection = psycopg2.connect(database=db_name, user=db_user, password=db_pass)
        except psycopg2.DatabaseError as e:
            print 'Error %s' % e
            print traceback.format_exc()
            sys.exit(1)
    return connection


def _transact(func):
    def wrap(*args, **kwargs):
        conn = _create_connection()
        try:
            result = func(*args, **kwargs)
            conn.commit()
            return result
        except psycopg2.DatabaseError as e:
            print 'Error %s' % e
            print traceback.format_exc()
            conn.rollback()


    return wrap


@_transact
def fill_data():
    conn = _create_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS Nodes")
    cursor.execute(
        'CREATE TABLE Nodes(id integer PRIMARY KEY, parent_id integer REFERENCES Nodes (id), label varchar(256), level integer)')
    cursor.execute('CREATE INDEX levels_idx ON Nodes (level)')
    conn.commit()
    levels = {}
    for i in xrange(random.randint(min_node_count, max_node_count)):
        id = i
        # get parent_id in less than random from 1 to 6 of id
        parent_id = random.choice(map(lambda x: i - x if i > x else None, range(1, 6)))
        if parent_id == None:
            levels[id] = 0
        else:
            levels[id] = levels[parent_id] + 1
        label = random.choice(['node_%s' % id, 'test', 'foo', 'bar'])
        print 'INSERT INTO Nodes (id, parent_id, label, level) VALUES (%s,%s,%s,%s)' % (
            id, parent_id, label, levels[id])
        cursor.execute('INSERT INTO Nodes (id, parent_id, label, level) VALUES (%s,%s,%s,%s)',
                       (id, parent_id, label, levels[id]))

def __form_element(element):
    return {'id': element[0], 'label': element[2], 'level': element[3], 'parent_id': element[1]}


@_transact
def get_children(element_id):
    cursor = _create_connection().cursor()
    if element_id is None:
        sql = 'SELECT * FROM Nodes WHERE parent_id is null'
    else:
        sql = 'SELECT * FROM Nodes WHERE parent_id = %s' % element_id
    cursor.execute(sql)
    result = []
    for element in cursor.fetchall():
        result.append(__form_element(element))

    return result


def get_elements_by_level(level_number):
    '''
    creating array of paths for any element in input level
    :param level_number:
    :return:
    '''
    cursor = _create_connection().cursor()
    sql = 'SELECT * FROM Nodes where level <= %s ORDER BY level DESC;' % level_number
    cursor.execute(sql)

    levels_container = defaultdict(list)  # level:[elements_id...]
    buff = {}  # element_id:element_container
    for element in cursor.fetchall():
        levels_container[element[3]].append(element[0])
        buff[element[0]] = __form_element(element)
    levels = levels_container.keys()
    levels.sort()
    accumulator = []
    for i, end_element_id in enumerate(levels_container[levels[-1]]):
        element = buff.pop(end_element_id)
        accumulator.append([element])
        for _, _ in levels_container.iteritems():
            if element['parent_id'] is not None:
                parent = buff.get(element['parent_id'])
                accumulator[i].append(parent)
                element = parent
    return accumulator


def get_elements_by_label(string):
    """
    forming paths for any element which have label equals input string
    :param string:
    :return: array of paths
    """
    cursor = _create_connection().cursor()
    sql = '''
        WITH RECURSIVE tree(id, parent_id, level, label, key) AS (
        SELECT id, parent_id, level, label, id
        FROM Nodes where label = '%s'
        UNION
        SELECT nd.id, nd.parent_id, nd.level, nd.label, tr.key
        FROM Nodes nd, tree tr
        WHERE tr.parent_id = nd.id
        )
        ,
        group_nodes as (
        SELECT array(select x from unnest(array_agg(id)) x order by x desc) arr, key
        FROM tree
        group by key
        )

        select array_length(gn.arr,1) ln, gn.arr, gn.key, n.label, n.level
        from group_nodes gn, nodes n
        where gn.key = n.id
        union
        select 0, array[0], id, label, level
        from tree
        where label != '%s'
        order by ln
    ''' % (string, string)
    cursor.execute(sql)
    path_elements = {}
    paths = []
    for path_el in cursor.fetchall():
        if path_el[0] != 0:
            paths.append(path_el[1])
        path_elements[path_el[2]] = {'id': path_el[2], 'label': path_el[3], 'level': path_el[4]}

    result = []
    for i, path in enumerate(paths):
        result.append([])
        for id in path:
            result[i].append(path_elements[id])

    return result


@_transact
def delete_element(id):
    '''
    Delete element and all his child
    :param id:
    :return:
    '''
    sql = """
    WITH RECURSIVE tree(id, parent_id) AS (
	SELECT id, parent_id
	FROM Nodes where id=%s
	UNION
	SELECT nd.id, nd.parent_id
	FROM Nodes nd, tree tr
	WHERE tr.id = nd.parent_id
    )
    delete from nodes where id in ( select id from tree);
    """%id
    cursor = _create_connection().cursor()
    cursor.execute(sql)


@_transact
def change_element_label(id, new_label):
    sql = """
    update nodes set label = '%s' WHERE id = %s;
    """ % (new_label, id)
    cursor = _create_connection().cursor()
    cursor.execute(sql)


if __name__ == '__main__':
    fill_data()
    # get_children(None)
    # get_elements_on_level(3)
    # get_elements_by_label('foo')
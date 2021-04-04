import psycopg2

def connect():
    params = {
    'database': 'group_22',
    'user': 'group_22',
    'password': 'NKyjO7dPvQufB',
    'host': '10.17.50.232',
    'port': 5432
    }
    c = psycopg2.connect(**params)
    # c = psycopg2.connect("dbname=group_22")
    return c

def commit(query, params):
    c = connect()
    cur = c.cursor()
    cur.execute(query, params)
    c.commit()
    cur.close()
    c.close()

def fetch(query, params):
    c = connect()
    cur = c.cursor()
    cur.execute(query, params)
    result = cur.fetchall()
    cur.close()
    c.close()
    return result
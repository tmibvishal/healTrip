import psycopg2

def connect():
    c = psycopg2.connect("dbname=db_group_22")
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
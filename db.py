import psycopg2

def fill_database():
    conn = psycopg2.connect("dbname=flask-sql")
    cur = conn.cursor()
    cur.execute("CREATE TABLE toys (id serial PRIMARY KEY, name text);")
    # let's add some starter data
    cur.execute("INSERT INTO toys (name) VALUES (%s)", ("duplo",))
    cur.execute("INSERT INTO toys (name) VALUES (%s)", ("lego",))
    cur.execute("INSERT INTO toys (name) VALUES (%s)", ("knex",))
    conn.commit()
    # make sure data was saved
    cur.execute("SELECT * FROM toys")
    cur.fetchall() # should get [(1, 'duplo'), (2, 'lego'), (3, 'knex')]
    cur.close()
    conn.close()

def connect():
  c = psycopg2.connect("dbname=flask-sql")
  return c

def get_all_toys():
  conn = connect()
  cur = conn.cursor()
  cur.execute("SELECT * FROM toys")
  toys = cur.fetchall()
  cur.close()
  conn.close()
  return toys

def add_toy(name):
  conn = connect()
  cur = conn.cursor()
  cur.execute("INSERT INTO toys (name) VALUES (%s)", (name,))
  conn.commit()
  cur.close()
  conn.close()
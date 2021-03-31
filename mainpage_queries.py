import psycopg2

def connect():
    c = psycopg2.connect("dbname=db_group_22")
    return c

def commit(query):
    c = connect()
    cur = c.cursor()
    cur.execute(query)
    c.commit()
    cur.close()
    c.close()

def fetch(query):
    c = connect()
    cur = c.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    c.close()
    return result

# get all cities with start with characters 'start'
def get_all_cities(start):
    cities = fetch(f"select ac.city
from airport_codes as ac
where ac.city like ''{start}'%'
group by ac.city;")
    return cities


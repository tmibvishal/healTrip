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

def get_user_bookings(userid):
    bookings = fetch(f"select * from bookings where userid='{userid}' order by id")
    return bookings

def get_airport_data(airport_code):
    airport = fetch(f"select * from airport_codes where airport_code='{airport_code}'")
    return airport

def get_num_flights(booking_id):
    return int(fetch(f'select count(*) from booking_entry where booking_id={booking_id} and is_hotel is false')[0][0])

def get_num_hotels(booking_id):
    return int(fetch(f'select count(*) from booking_entry where booking_id={booking_id} and is_hotel is true')[0][0])

def get_booking(booking_id):
    return fetch(f'select * from bookings where id={booking_id}')

def get_booking_entries(booking_id):
    return fetch(f'select * from booking_entry where booking_id={booking_id} order by id')

def get_hotel(hotel_id):
    return fetch(f'select * from hotels where hotel_id={hotel_id}')

def get_flight(flight_id):
    return fetch(f'select * from flights where flight_id={flight_id}')
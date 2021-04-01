import db

def add_booking(source_airport_code, userid, departure_date):
    query = """insert into bookings(userid, source_airport_code, departure_date) values (%s, %s, %s)"""
    db.commit(query, (userid, source_airport_code, departure_date))

def add_hotel_entry(booking_id, entry_id, stay_period):
    query = """insert into booking_entry(booking_id, is_hotel, entry_id, stay_period) values (%s, %s, %s, %s)"""
    db.commit(query, (booking_id, True, entry_id, stay_period))

def add_flight_entry(booking_id, entry_id):
    query = """insert into booking_entry(booking_id, is_hotel, entry_id) values (%s, %s, %s)"""
    db.commit(query, (booking_id, False, entry_id))

def get_last_booking_id(userid):
    query= """select id from bookings where userid=%s order by id desc limit 1"""
    return db.fetch(query, (userid, ))[0]


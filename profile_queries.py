import db

def get_user_bookings(userid):
    bookings = db.fetch("select * from bookings where userid=%s order by id desc", (userid, ))
    return bookings

def get_airport_data(airport_code):
    airport = db.fetch("select * from airport_codes where airport_code=%s", (airport_code, ))
    return airport

def get_num_flights(booking_id):
    return int(db.fetch('select count(*) from booking_entry where booking_id=%s and is_hotel is false', (booking_id, ))[0][0])

def get_num_hotels(booking_id):
    return int(db.fetch('select count(*) from booking_entry where booking_id=%s and is_hotel is true', (booking_id, ))[0][0])

def get_booking(booking_id):
    return db.fetch('select * from bookings where id=%s', (booking_id, ))

def get_booking_entries(booking_id):
    return db.fetch('select * from booking_entry where booking_id=%s order by id', (booking_id, ))

def get_hotel(hotel_id):
    hotels = db.fetch('select * from hotels where hotel_id=%s', (hotel_id, ))
    if len(hotels) != 1:
        print(hotel_id, ' hotel not found')
        return None
    return hotels[0]

def get_flight(flight_id):
    flights = db.fetch('select * from flights where flight_id=%s', (flight_id, ))
    if len(flights) != 1:
        print(flight_id, ' flight not found')
        return None
    return flights[0]

def get_reviews(hotel_id):
    return db.fetch('select * from reviews where hotel_id=%s', (hotel_id, ))

def get_state(state_code):
    states = db.fetch("select state_name from states where state_code=%s", (state_code, ))
    if len(states) != 1:
        print(state_code, 'not found')
        return None
    return states[0][0]

def user_has_booked(hotel_id, user_id):
    query="""
    select * from bookings b, booking_entry be where 
    b.id=be.booking_id and userid=%s and is_hotel='true' and entry_id=%s
    """
    entries = db.fetch(query, (user_id, hotel_id))
    return len(entries)>0

def user_has_reviewed(hotel_id, user_id):
    query="""
    select * from users, reviews where users.uname=reviews.review_username and userid=%s and hotel_id=%s
    """
    entries = db.fetch(query, (user_id, hotel_id))
    return len(entries)>0

def add_review(hotel_id, cur_date, rating, user_id, title, details):
    query="""
    insert into reviews(hotel_id, review_date, review_rating, review_username, review_title, review_text)
    values (%s, %s, %s, %s, %s, %s)
    """
    db.commit(query, (hotel_id, cur_date, rating, user_id, title, details))


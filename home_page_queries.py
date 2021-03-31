import db

# get all cities with start with characters 'start'
def get_all_cities(start_string_of_city):
    query = """select DISTINCT(city) 
    from airport_codes 
    where city like %s 
    LIMIT 10;"""
    search_term = start_string_of_city
    like_pattern = '{}%'.format(start_string_of_city)
    cities = db.fetch(query, (like_pattern, ))
    return cities

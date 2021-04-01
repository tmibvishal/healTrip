import db
import datetime

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

def get_covid_status(city):
    query = """select cs.state_code , cs.deaths , cs.hospitalized , cs.inICU , cs.onVentilator , cs.positive , cs.recovered
    from covid_status as cs , airport_codes as ac
    where ac.city = %s
    and ac.state_code = cs.state_code;"""
    city_pattern = '{}'.format(city)
    status = db.fetch(query, (city_pattern, ))
    return status

def check_direct_connection(city1,city2):
    query = """select * from direct_con where city1 = %s and city2 = %s;"""

    city_pattern1 = '{}'.format(city1)
    city_pattern2 = '{}'.format(city2)

    is_direct = db.fetch(query , (city_pattern1 , city_pattern2, ))

    if len(is_direct) != 1:
        return False

    return True

def get_direct_connection(city1,city2,dep_date):
    query = """select fl.flight_id
    from airport_codes as ac1 , airport_codes as ac2 , flights as fl
    where fl.origin = ac1.airport_code and fl.dest = ac2.airport_code
    and ac1.city = %s and ac2.city = %s
    and fl.fl_date = %s
    limit 3; """

    city_pattern1 = '{}'.format(city1)
    city_pattern2 = '{}'.format(city2)
    date_pattern = '{}'.format(dep_date)

    direct_con = db.fetch(query , (city_pattern1 , city_pattern2, date_pattern, ))

    temp_conn = []
    for c in direct_con:
        temp_conn.append(c[0])

    return temp_conn

def get_connecting_flights(city1,city2,dep_date):
    query = """select rc.flight_ids
    from
        (with recursive reach_carr (f,t,all_ids,flight_ids,last_arr_time,cost) as (
                (select origin,dest,ARRAY[origin] , ARRAY[fl.flight_id] ,fl.crs_arr_time, fl.distance
                from flights as fl , airport_codes as ac1
                where fl.origin = ac1.airport_code and ac1.city = %s 
                and fl.fl_date = %s)
                union
                (select rc.f,fl.dest,all_ids || fl.origin , flight_ids || fl.flight_id , fl.crs_arr_time , rc.cost + fl.distance
                from reach_carr as rc,flights as fl , airport_codes as ac1 , airport_codes as ac2
                where (rc.t = fl.origin)
                and (rc.f = ac1.airport_code and ac1.city = %s)
                and (rc.t <> ac2.airport_code and ac2.city = %s)
                and fl.crs_dep_time > rc.last_arr_time
                and fl.fl_date = %s
                and fl.dest <> ANY(all_ids)
                and array_length(all_ids,1) < 3
                )) select * from reach_carr) as rc , airport_codes as ac1 , airport_codes as ac2
    where (rc.f = ac1.airport_code and ac1.city = %s)
    and (rc.t = ac2.airport_code and ac2.city = %s)
    group by rc.flight_ids , rc.cost
    order by cost asc
    limit 3;"""

    city_pattern1 = '{}'.format(city1)
    city_pattern2 = '{}'.format(city2)
    date_pattern = '{}'.format(dep_date)

    conn = db.fetch(query , (city_pattern1 , date_pattern , city_pattern1 , city_pattern2 , date_pattern , city_pattern1 , city_pattern2 , ))

    temp_conn = []
    for c in conn:
        temp_conn.append(c[0])

    return temp_conn

def get_best_hotel(city):
    query = """ select hotels.hotel_id
    from hotels , hotels_rating
    where hotels.hotel_id = hotels_rating.hotel_id
    and hotels.city = %s
    group by hotels.hotel_id , hotels_rating.rating
    order by rating desc
    limit 3; """

    city_pattern = '{}'.format(city)
    hotels = db.fetch(query, (city_pattern, ))

    temp_hotels = []
    for h in hotels:
        temp_hotels.append(h[0])

    return temp_hotels


def no_round_trip_simple(travelObj):
    src_city = travelObj["sourceCity"]
    dep_date_text = travelObj["departureDate"]
    cities_to_visit = travelObj["citiesToVisit"]

    dep_date = datetime.datetime(int(dep_date_text[:4]),int(dep_date_text[5:7]),int(dep_date_text[8:10]))

    flight_paths = []
    hotels = []

    for city in cities_to_visit:
        city_name = city["cityName"]
        hotels.append(get_best_hotel(city_name))

        """

        if check_direct_connection(src_city , city_name):
            flight_path_temp = get_direct_connection(src_city,city_name,dep_date)

            if len(flight_path_temp) == 0:
                flight_path_temp = get_connecting_flights(src_city,city_name,dep_date)

            flight_paths.append(flight_path_temp)

        else:
        """
        flight_paths.append(get_connecting_flights(src_city,city_name,dep_date))

        src_city = city_name

        time_change = datetime.timedelta(days=city["stayPeriod"])
        dep_date = dep_date + time_change

    travelObj["flight_paths"] = flight_paths
    travelObj["hotels"] = hotels

    return travelObj

def round_trip_simple(travelObj):
    src_city = travelObj["sourceCity"]
    dep_date_text = travelObj["departureDate"]
    cities_to_visit = travelObj["citiesToVisit"]

    dep_date = datetime.datetime(int(dep_date_text[:4]),int(dep_date_text[5:7]),int(dep_date_text[8:10]))

    temp_city_name = src_city

    flight_paths = []
    hotels = []

    for city in cities_to_visit:
        city_name = city["cityName"]
        hotels.append(get_best_hotel(city_name))

        flight_paths.append(get_connecting_flights(src_city,city_name,dep_date))

        src_city = city_name

        time_change = datetime.timedelta(days=city["stayPeriod"])
        dep_date = dep_date + time_change

    # to complete round trip
    flight_paths.append(get_connecting_flights(src_city,temp_city_name,dep_date))

    travelObj["flight_paths"] = flight_paths
    travelObj["hotels"] = hotels

    return travelObj
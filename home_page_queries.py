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
    queryReult = db.fetch(query, (city, ))
    if (len(queryReult) == 0):
        statusDict = {"inDB": False}
        return statusDict
    status = queryReult[0]
    statusDict = {"inDB": True, "stateCode": status[0], "deaths": status[1], "hospitalized": status[2], "inICU": status[3], "onVentilator": status[4], "positive": status[5], "recovered": status[6]}
    return statusDict

def get_direct_connection(city1,city2,dep_date):
    query = """select fl.flight_id
    from airport_codes as ac1 , airport_codes as ac2 , flights as fl
    where fl.origin = ac1.airport_code and fl.dest = ac2.airport_code
    and ac1.city = %s and ac2.city = %s
    and fl.fl_date = %s
    limit 3; """
    direct_con = db.fetch(query , (city1 , city2, dep_date, ))

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
    conn = db.fetch(query , (city1 , dep_date , city1 , city2 , dep_date , city1 , city2 , ))

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

    hotels = db.fetch(query, (city, ))

    temp_hotels = []
    for h in hotels:
        temp_hotels.append(h[0])

    return temp_hotels

# plan a simple trip
def trip_simple(travelObj,round):
    src_city = travelObj["sourceCity"]
    dep_date_text = travelObj["departureDate"]
    cities_to_visit = travelObj["citiesToVisit"]

    temp_city_name = src_city

    dep_date = datetime.datetime(int(dep_date_text[:4]),int(dep_date_text[5:7]),int(dep_date_text[8:10]))

    flight_paths = []
    hotels = []

    for city in cities_to_visit:
        city_name = city["cityName"]
        hotels.append(get_best_hotel(city_name))

        flight_paths.append(get_connecting_flights(src_city,city_name,dep_date))

        src_city = city_name

        time_change = datetime.timedelta(days=city["stayPeriod"])
        dep_date = dep_date + time_change

    if round:
        flight_paths.append(get_connecting_flights(src_city,temp_city_name,dep_date))

    travelObj["flight_paths"] = flight_paths
    travelObj["hotels"] = hotels

    return travelObj

# returns distance between two cities
def get_distance(city1,city2):
    query = """ select distance
    from city_distance
    where (city_distance.city1 = %s and city_distance.city2 = %s)
    or (city_distance.city2 = %s and city_distance.city1 = %s);"""

    dist = db.fetch(query , (city1 , city2 , city2 , city1, ))

    if len(dist) == 0:
        return 100000000

    return dist[0][0]

# count direct connections from city to cities in cities_to_visit
def count_direct_connections(city,cities_to_visit,dep_date):
    t = tuple(cities_to_visit)

    if len(t) == 1:

        query = """ select count(city1)
        from (select ac1.city as city1 , ac2.city as city2
        from airport_codes as ac1 , airport_codes as ac2 , flights as fl
        where fl.origin = ac1.airport_code and fl.dest = ac2.airport_code
        and fl.fl_date = %s
        group by ac1.city , ac2.city) as dc
        where city1 = %s 
        and city2 = %s"""

        cnt = db.fetch(query, (dep_date, city, t[0] ))

        return cnt[0][0]

    else:
        query = """ select count(city1)
        from (select ac1.city as city1 , ac2.city as city2
        from airport_codes as ac1 , airport_codes as ac2 , flights as fl
        where fl.origin = ac1.airport_code and fl.dest = ac2.airport_code
        and fl.fl_date = %s
        group by ac1.city , ac2.city) as dc
        where city1 = %s 
        and city2 in {}""".format(t)

        cnt = db.fetch(query, (dep_date, city, ))

        return cnt[0][0]

# get the best ordering of cities for given list
def get_best_ordering(city1,date,cities,city_stay_dict,round):
    temp_src = city1
    src_city = city1
    dep_date = date
    cities_to_visit = cities.copy()

    i = 0
    n = len(cities_to_visit)

    best_city_path = []
    flight_paths = []
    hotels = []

    while(i < n):
        best_city = cities_to_visit[0]
        max_conn = 0
        best_city_dist = 100000000

        for city in cities_to_visit:
            cnt = count_direct_connections(city,cities_to_visit,dep_date)
            dist = get_distance(src_city,city)

            if cnt > max_conn:
                max_conn = cnt
                best_city = city
                best_city_dist = dist

            elif cnt == max_conn:
                if dist < best_city_dist:
                    best_city = city
                    best_city_dist = dist

        best_city_path.append(best_city)
        i+=1

        hotels.append(get_best_hotel(best_city))

        flight_paths.append(get_connecting_flights(src_city,best_city,dep_date))

        cities_to_visit.remove(best_city)
        src_city = best_city

        time_change = datetime.timedelta(days=city_stay_dict[best_city])
        dep_date = dep_date + time_change

    if round:
        flight_paths.append(get_connecting_flights(best_city_path[-1],temp_src,dep_date))
        best_city_path.append(temp_src)

    return (flight_paths,hotels,best_city_path)


def trip_best_ordering(travelObj,round):
    src_city = travelObj["sourceCity"]
    dep_date_text = travelObj["departureDate"]
    cities_to_visit = travelObj["citiesToVisit"]

    dep_date = datetime.datetime(int(dep_date_text[:4]),int(dep_date_text[5:7]),int(dep_date_text[8:10]))

    city_stay_dict = {}
    visit = []

    for city in cities_to_visit:
        city_stay_dict[city["cityName"]] = city["stayPeriod"]
        visit.append(city["cityName"])

    (flight_paths,hotels,best_city_path) = get_best_ordering(src_city,dep_date,visit,city_stay_dict,round)

    travelObj["flight_paths"] = flight_paths
    travelObj["hotels"] = hotels
    travelObj["best_city_path"] = best_city_path

    return travelObj



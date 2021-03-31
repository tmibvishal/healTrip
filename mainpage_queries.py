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
group by ac.city")
    return cities

def init_autocomplete():
    commit(f"create index city_index on airport_codes(city)")

def destroy_autocomplete():
    commit(f"drop index city_index")

def get_covid_status(city):
    status = fetch(f"select cs.state_code , cs.deaths , cs.hospitalized , cs.inICU , cs.onVentilator , cs.positive , cs.recovered
from covid_status as cs , airport_codes as ac
where ac.city = 'Given city'
and ac.state_code = cs.state_code")
    return status

def init_connections():
    commit(f"CREATE MATERIALIZED VIEW direct_con
    as
    select ac1.city as city1 , ac2.city as city2
    from airport_codes as ac1 , airport_codes as ac2 , flights as fl
    where fl.origin = ac1.airport_code and fl.dest = ac2.airport_code
    group by ac1.city , ac2.city")

    commit(f"create index direct_con_index on direct_con(city1,city2)")

def destroy_connections():
    commit(f"drop index direct_con_index")
    commit(f"drop materialized view direct_con")

def check_direct_connection(city1,city2):
    is_direct = fetch(f"select * from direct_con where city1 = '{city1}' and city2 = '{city2}'")

    if len(is_direct) != 1:
        return False

    return True


def get_connecting_flights(city1,city2):
    flights_py = fetch(f"select rc.flight_ids
    from
        (with recursive reach_carr (f,t,all_ids,flight_ids,last_arr_time,cost) as (
                (select origin,dest,ARRAY[origin] , ARRAY[fl.flight_id] ,fl.crs_arr_time, fl.distance
                from flights as fl , airport_codes as ac1
                where fl.origin = ac1.airport_code and ac1.city = 'Chicago' 
                and fl.fl_date = '2021-04-01')
                union
                (select rc.f,fl.dest,all_ids || fl.origin , flight_ids || fl.flight_id , fl.crs_arr_time , rc.cost + fl.distance
                from reach_carr as rc,flights as fl , airport_codes as ac1 , airport_codes as ac2
                where (rc.t = fl.origin)
                and (rc.f = ac1.airport_code and ac1.city = 'Chicago')
                and (rc.t <> ac2.airport_code and ac2.city = 'Seattle')
                and fl.crs_dep_time > rc.last_arr_time
                and fl.fl_date = '2021-04-01'
                and fl.dest <> ANY(all_ids)
                and array_length(all_ids,1) < 3
                )) select * from reach_carr) as rc , airport_codes as ac1 , airport_codes as ac2
    where (rc.f = ac1.airport_code and ac1.city = 'Chicago')
    and (rc.t = ac2.airport_code and ac2.city = 'Seattle')
    group by rc.flight_ids , rc.cost
    order by cost asc
    limit 3")

    return flights_py




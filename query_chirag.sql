-- select cities starting with something --
/*
select ac.city
from airport_codes as ac
where ac.city like 'A%'
group by ac.city;

create index city_index on airport_codes(city);
*/

-- select the 3 best possible paths between two cities on a certain date --
select rc.flight_ids
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
limit 3;

-- get the covid data of a city --
/*
select cs.state_code , cs.deaths , cs.hospitalized , cs.inICU , cs.onVentilator , cs.positive , cs.recovered
from covid_status as cs , airport_codes as ac
where ac.city = 'Given city'
and ac.state_code = cs.state_code;
*/

-- direct connection --
/*
select fl.flight_id
from airport_codes as ac1 , airport_codes as ac2 , flights as fl
where fl.origin = ac1.airport_code and fl.dest = ac2.airport_code
and ac1.city = 'city1' and ac2.city = 'city2';
*/

-- choose best hotels --
/*
select hotels.hotel_id
from hotels , hotels_rating
where hotels.hotel_id = hotels_rating.hotel_id
and hotels.city = 'Chicago'
group by hotels.hotel_id , hotels_rating.rating
order by rating desc;
*/
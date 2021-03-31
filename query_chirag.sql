-- select cities starting with something --
/*
select ac.city
from airport_codes as ac
where ac.city like 'A%'
group by ac.city;
*/

-- select the 3 best possible paths between two cities on a certain date --
/*
select rc.flight_ids
from
    (with recursive reach_carr (f,t,all_ids,flight_ids,last_arr_time,cost) as (
            (select origin,dest,ARRAY[origin] , ARRAY[fl.flight_id] ,fl.crs_arr_time, fl.distance
            from flights as fl , airport_codes as ac1
            where fl.origin = ac1.airport_code and ac1.city = 'Chicago' 
            and fl.fl_date = '2018-04-01')

            union

            (select rc.f,fl.dest,all_ids || fl.origin , flight_ids || fl.flight_id , fl.crs_arr_time , rc.cost + fl.distance
            from reach_carr as rc,flights as fl , airport_codes as ac1 , airport_codes as ac2
            where (rc.t = fl.origin)
            and (rc.f = ac1.airport_code and ac1.city = 'Chicago')
            and (rc.t <> ac2.airport_code and ac2.city = 'Dallas')
            and fl.crs_dep_time > rc.last_arr_time
            and fl.fl_date = '2018-04-01'
            and fl.dest <> ANY(all_ids)
            and array_length(all_ids,1) < 3
            )) select * from reach_carr) as rc , airport_codes as ac1 , airport_codes as ac2
where (rc.f = ac1.airport_code and ac1.city = 'Chicago')
and (rc.t = ac2.airport_code and ac2.city = 'Dallas')
group by rc.flight_ids , rc.cost
order by cost asc
limit 3;
*/

-- find the best round trip path from a source city and visiting a sequence of cities --
select rc.flight_ids
from
    (with recursive reach_carr (f,t,all_ids,flight_ids,last_arr_time,cost) as (
            (select origin,dest,ARRAY[origin] , ARRAY[fl.flight_id] ,fl.crs_arr_time, fl.distance
            from flights as fl , airport_codes as ac1
            where fl.origin = ac1.airport_code and ac1.city = 'Chicago' 
            and fl.fl_date = '2018-04-01')

            union

            (select rc.f,fl.dest,all_ids || fl.origin , flight_ids || fl.flight_id , fl.crs_arr_time , rc.cost + fl.distance
            from reach_carr as rc,flights as fl , airport_codes as ac1 , airport_codes as ac2
            where (rc.t = fl.origin)
            and (rc.f = ac1.airport_code and ac1.city = 'Chicago')
            and (rc.t <> ac2.airport_code and ac2.city = 'Dallas')
            and fl.crs_dep_time > rc.last_arr_time
            and fl.fl_date = '2018-04-01'
            and fl.dest <> ANY(all_ids)
            and array_length(all_ids,1) < 3
            )) select * from reach_carr) as rc , airport_codes as ac1 , airport_codes as ac2
where (rc.f = ac1.airport_code and ac1.city = 'Chicago')
and (rc.t = ac2.airport_code and ac2.city = 'Dallas')
group by rc.flight_ids , rc.cost
order by cost asc
limit 3;


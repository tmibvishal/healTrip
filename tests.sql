-- All flights have mapped airport codes and hotels in their cities
select count(*) from flights;

select count(*) 
from 
    flights f, airport_codes ac1, airport_codes ac2 
where 
    f.origin = ac1.airport_code 
    and f.dest = ac2.airport_code 
    and ac1.city in (select distinct city from hotels) 
    and ac2.city in (select distinct city from hotels); 

-- Stats
select count(distinct origin) from flights;
select count(distinct dest) from flights;

select count(*) from hotels 
where city in (select distinct ac.city from flights f, airport_codes ac where f.origin = ac.airport_code);
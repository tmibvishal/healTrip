-- select cities, hotels and airports --
select nc.city , nh.name , ac.airport_code
from cities as nc , hotels as nh , airport_codes as ac
where nc.city = nh.city and nc.city = ac.city;
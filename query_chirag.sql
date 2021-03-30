select ac.city
from airport_codes as ac
where ac.city like 'A%'
group by ac.city;
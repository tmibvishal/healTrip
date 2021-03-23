-- select cities, hotels and airports --
-- select nc.city , nh.name , ac.airport_code
-- from cities as nc , hotels as nh , airport_codes as ac
-- where nc.city = nh.city and nc.city = ac.city;

-- \copy (select row_number() over(order by city,name) hotel_id,address,city,name,postalCode,province,avg(rating) as mean_rating from reviews group by address,city,name,postalCode,province) to 'data/unique_hotels.csv' csv header;

-- \copy (select row_number() over(order by hotel_id, review_date) review_id, hotel_id,review_date,review_rating,review_username,review_title,review_text from hotels_all, hotels where hotels.name = hotels_all.name and hotels.city = hotels_all.city and hotels.address = hotels_all.address) to 'data-cleaned/reviews.csv' csv header;


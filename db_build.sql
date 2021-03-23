create table airport_codes(
    city text ,
    state_code text ,
    country text ,
    airport_code text
);

create table flights(
    fl_date date ,
    op_carrier text ,
    origin text ,
    dest text ,
    crs_dep_time integer ,
    crs_arr_time integer ,
    distance integer
);

create table hotels(
    hotel_id integer,
    city text,
    province text,
    name text,
    address text,
    postalcode text,
    constraint hotel_key primary key (hotel_id)
);

create table reviews(
    review_id integer,
    hotel_id integer,
    review_date date,
    review_rating real,
    review_username text,
    review_title text,
    review_text text,
    constraint review_key primary key (review_id),
    constraint hotel_ref foreign key (hotel_id) references hotels(hotel_id)
);

create table cities(
    city text ,
    city_ascii text ,
    state_id text ,
    state_name text
);

\copy flights from 'data/flights.csv' delimiter ',' csv header;
\copy airport_codes from 'data/codes.csv' delimiter ',' csv header;
\copy hotels from 'data/hotels.csv' delimiter ',' csv header;
\copy reviews from 'data/reviews.csv' delimiter ',' csv header;
\copy cities from 'data/us_cities.csv' delimiter ',' csv header;


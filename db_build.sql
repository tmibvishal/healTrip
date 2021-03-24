create table airport_codes(
    city text ,
    state_code text ,
    airport_code text,
    constraint airport_key primary key (airport_code)
);

create table flights(
    flight_id integer,
    fl_date date ,
    op_carrier text ,
    origin text ,
    dest text ,
    crs_dep_time integer ,
    crs_arr_time integer ,
    distance integer,
    constraint flight_key primary key (flight_id),
    constraint origin_ref foreign key (origin) references airport_codes(airport_code),
    constraint dest_ref foreign key (dest) references airport_codes(airport_code)
);

create table hotels(
    hotel_id integer,
    city text,
    state_code text,
    name text,
    address text,
    postalcode text,
    constraint hotel_key primary key (hotel_id)
    -- constraint city_ref foreign key (city, state_code) references airport_codes(city, state_code)
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

create table states(
    state_code text,
    state_name text,
    constraint state_key primary key (state_code)
);

\copy airport_codes from 'data/codes.csv' delimiter ',' csv header;
\copy flights from 'data/flights.csv' delimiter ',' csv header;
\copy hotels from 'data/hotels.csv' delimiter ',' csv header;
\copy reviews from 'data/reviews.csv' delimiter ',' csv header;
\copy states from 'data/states.csv' delimiter ',' csv header;


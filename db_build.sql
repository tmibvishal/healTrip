create table users(
    userid serial,
    uname text NOT NULL,
    email text ,
    pass text,
    is_admin boolean,
    constraint users_key PRIMARY KEY (userid),
    constraint unique_username UNIQUE (uname)
);

create table airport_codes(
    city text ,
    state_code text ,
    airport_code text,
    constraint airport_key primary key (airport_code)
);

create table bookings(
    id serial,
    userid integer,
    source_airport_code text,
    departure_date Date,
    constraint booking_key primary key (id),
    constraint source_ref foreign key (source_airport_code) references airport_codes(airport_code) on delete set null,
    constraint user_ref foreign key (userid) references users(userid) on delete cascade
);

create table booking_entry(
    id serial,
    booking_id integer, -- id of booking
    is_hotel boolean, -- 0 for flight, 1 for hotel
    entry_id integer, -- flight id or hotel id
    stay_period integer, -- null for flight, no of days for hotel
    constraint entry_key primary key (id),
    constraint booking_ref foreign key (booking_id) references bookings(id) on delete cascade
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
    constraint origin_ref foreign key (origin) references airport_codes(airport_code) on delete cascade,
    constraint dest_ref foreign key (dest) references airport_codes(airport_code) on delete cascade
);

create table hotels(
    hotel_id integer,
    city text,
    state_code text,
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
    constraint hotel_ref foreign key (hotel_id) references hotels(hotel_id) on delete cascade
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


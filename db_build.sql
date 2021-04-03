create table users(
    userid serial,
    uname text NOT NULL,
    email text ,
    pass text,
    is_admin boolean,
    constraint users_key PRIMARY KEY (userid),
    constraint unique_username UNIQUE (uname)
);

-- TODO VishalS: add triggers and make starting 5 table er diagram
create table disabled_cities(
    city text NOT NULL,
    constraint unique_city UNIQUE (city)
);

create table airport_codes(
    city text ,
    state_code text ,
    airport_code text,
    enabled boolean default true,
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

-- TODO Chirag: only include airport that are enabled - these 2 tables ka ER diagram bna
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
    enabled boolean default true,
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

create table covid_status(
    state_code text,
    deaths integer,
    hospitalized integer,
    inICU integer,
    onVentilator integer,
    positive integer,
    recovered integer,
    constraint covid_key primary key (state_code),
    constraint state_ref foreign key (state_code) references states(state_code)
);

\copy airport_codes (city, state_code, airport_code) from 'data/codes.csv' delimiter ',' csv header;
\copy flights from 'data/new_flights.csv' delimiter ',' csv header;
\copy hotels (hotel_id, city, state_code, name, address, postalcode) from 'data/hotels.csv' delimiter ',' csv header;
\copy reviews from 'data/reviews.csv' delimiter ',' csv header;
\copy states from 'data/states.csv' delimiter ',' csv header;
\copy covid_status from 'data/covid_status.csv' delimiter ',' csv header;

CREATE OR REPLACE FUNCTION procedure_disable_city() RETURNS TRIGGER AS $p_disable_city$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            UPDATE airport_codes SET enabled = true WHERE city = OLD.city;
            UPDATE hotels SET enabled = true WHERE city = OLD.city;
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            -- can also check if new updated value is not already in table o.w. error
            UPDATE airport_codes SET enabled = true WHERE city = OLD.city;
            UPDATE hotels SET enabled = true WHERE city = OLD.city;
            UPDATE airport_codes SET enabled = false WHERE city = NEW.city;
            UPDATE hotels SET enabled = false WHERE city = NEW.city;
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            UPDATE airport_codes SET enabled = false WHERE city = NEW.city;
            UPDATE hotels SET enabled = false WHERE city = NEW.city;
            RETURN NEW;
        END IF;
        RETURN NULL; -- result is ignored since this is an AFTER trigger
    END;
$p_disable_city$ LANGUAGE PLPGSQL;

CREATE TRIGGER disable_city_trigger
    AFTER INSERT OR UPDATE OR DELETE 
    ON disabled_cities
    FOR EACH ROW 
    EXECUTE PROCEDURE procedure_disable_city();


create index city_index on airport_codes(city); -- So that auto complete feature will work faster on home page --

CREATE MATERIALIZED VIEW city_distance
    as
    select city1 , city2 , min(distance) as distance
    from
        (select ac1.city as city1 , ac2.city as city2 , fl.distance
        from airport_codes as ac1 , airport_codes as ac2 , flights as fl
        where fl.origin = ac1.airport_code and fl.dest = ac2.airport_code
        group by ac1.city , ac2.city , fl.distance) as dist
    group by city1, city2;

create index city_distance_index on city_distance(city1,city2);

create MATERIALIZED view hotels_rating
as
    select hotels.hotel_id , avg(review_rating) as rating
    from hotels , reviews
    where hotels.hotel_id = reviews.hotel_id
    group by hotels.hotel_id;

create index rating_index on hotels_rating(hotel_id);



-- TODO Bindal: make last 3 ER table diagram --
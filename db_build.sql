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
    id text ,
    address text ,
    city text ,
    name text ,
    postalCode text ,
    province text ,
    rating real
);

create table cities(
    city text ,
    city_ascii text ,
    state_id text ,
    state_name text ,
    id text
);

\copy flights from 'data/flights.csv' delimiter ',' csv header;
\copy airport_codes from 'data/codes.csv' delimiter ',' csv header;
\copy hotels from 'data/new_hotels.csv' delimiter ',' csv header;
\copy cities from 'data/new_us_cities.csv' delimiter ',' csv header;


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

\copy covid_status from 'data/covid_status.csv' delimiter ',' csv header;


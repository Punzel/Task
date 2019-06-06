

CREATE TABLE check_results (
    id  integer primary key AUTOINCREMENT,
    url text,
    check_time date,
    response_time time integer,
    error text,
    succesfull integer,
    regex_matches  text)
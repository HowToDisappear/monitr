CREATE TABLE crypto (
    id bigserial PRIMARY KEY,
    exchange VARCHAR ( 20 ) NOT NULL,
    symbol VARCHAR ( 20 ) NOT NULL,
    base VARCHAR ( 20 ) NOT NULL,
    quote VARCHAR ( 20 ) NOT NULL,
    last_price REAL NOT NULL,
    time_received TIMESTAMP NOT NULL
);

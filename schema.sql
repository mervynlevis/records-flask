DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    signup_date
);

-- INSERT INTO users (user_id, password, signup_date)
-- VALUES
-- ('test','test','March 1, 2021');


DROP TABLE IF EXISTS records;

CREATE TABLE records
(
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    length TEXT NOT NULL,
    price TEXT NOT NULL,
    stock INTEGER NOT NULL,
    format TEXT NOT NULL
);

INSERT INTO records (title, artist, length, price, stock, format) 
VALUES 
('I want to wash','soap fighters','40 min','€25',50,'vinyl'),
('lyrics for lizards','flight of the pink lizards','40 min','€25',50,'vinyl'),
('glasgow calling','two seconds to glasgow','40 min','€25',50,'vinyl'),
('loofa legend','soap fighters','40 min','€25',50,'vinyl'),
('album of songs','the band formerly known as artist 5','40 min','€25',50,'vinyl'),
('music band: the album','music band','40 min','€25',50,'vinyl'),
('these neighs','john bon pony','40 min','€25',50,'vinyl'),
('jingle all the neigh','john bon pony','40 min','€25',50,'vinyl'),
('maybe its neighbelline','john bon pony','40 min','€25',50,'vinyl'),
('songs to listen to','music band','40 min','€25',50,'vinyl'),
('another album','music band','40 min','€12',50,'CD'),
('by the neigh','john bon pony','40 min','€12',50,'CD'),
('pinto jazz','bean','40 min','€12',50,'CD'),
('same to you bud','soap fighters','40 min','€12',50,'CD'),
('mayo blues','ham sandwich','40 min','€12',1,'CD');

DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    order_content TEXT NOT NULL,
    price TEXT NOT NULL,
    order_date TEXT
);

DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    record_id TEXT,
    artist TEXT,
    title TEXT,
    user_id TEXT,
    review TEXT,
    stars TEXT
);

INSERT INTO reviews (record_id, artist, title, user_id, review, stars)
VALUES
('1','soap fighters','I want to wash','admin','good album','****'),
('1','soap fighters','I want to wash','merv','good album','****');

DROP TABLE IF EXISTS sales;

CREATE TABLE sales
(   
    total_sales TEXT
);

INSERT INTO sales VALUES
('0');
DROP TABLE IF EXISTS `brands` ;

CREATE TABLE `brands` (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL);

CREATE TABLE `fuel_type` (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
    );

CREATE TABLE `car` (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER NOT NULL,
    name TEXT UNIQUE NOT NULL,
    FOREIGN KEY(brand_id) REFERENCES brands(id)
    );


CREATE TABLE `offer` (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    title TEXT,
    price REAL NOT NULL,
    year INTEGER NOT NULL,
    fuel_id INTEGER NOT NULL,
    url TEXT NOT NULL
    );

CREATE TABLE `car_blotter` (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    title TEXT,
    price REAL NOT NULL,
    year INTEGER NOT NULL,
    fuel_id TEXT NOT NULL,
    url TEXT NOT NULL
    );
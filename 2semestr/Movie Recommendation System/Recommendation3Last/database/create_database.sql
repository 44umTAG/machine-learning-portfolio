
CREATE DATABASE IF NOT EXISTS movie_recommendation;
USE movie_recommendation;

CREATE TABLE users (
    userId INT PRIMARY KEY
);

CREATE TABLE movies (
    movieId INT PRIMARY KEY,
    title VARCHAR(255),
    genres VARCHAR(255),
    year INT
);

CREATE TABLE ratings (
    ratingId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT,
    movieId INT,
    rating FLOAT,
    timestamp DATETIME,
    FOREIGN KEY (userId) REFERENCES users(userId),
    FOREIGN KEY (movieId) REFERENCES movies(movieId)
);

CREATE TABLE genres (
    genreId INT AUTO_INCREMENT PRIMARY KEY,
    movieId INT,
    genre VARCHAR(100),
    FOREIGN KEY (movieId) REFERENCES movies(movieId)
);

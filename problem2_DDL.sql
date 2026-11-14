DROP DATABASE IF EXISTS library;
CREATE DATABASE library;
USE library;

CREATE TABLE AUTHOR (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    image_filename VARCHAR(255) DEFAULT 'default.png'
);

CREATE TABLE PUBLISHER (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50)
);

CREATE TABLE CATEGORY (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE BOOK (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    publish_year INT,
    author_id INT NOT NULL,
    publisher_id INT,
    category_id INT,
    image_filename VARCHAR(255) DEFAULT 'default.png',
    FOREIGN KEY (author_id) REFERENCES AUTHOR(author_id) ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES PUBLISHER(publisher_id),
    FOREIGN KEY (category_id) REFERENCES CATEGORY(category_id)
);

CREATE TABLE MEMBER (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    join_date DATE NOT NULL
);

CREATE TABLE LOAN (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE NULL,
    FOREIGN KEY (book_id) REFERENCES BOOK(book_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES MEMBER(member_id)
);
USE library;

INSERT INTO AUTHOR (name, country) VALUES
('Omar Osama', 'Egypt'),
('Omar Nassret', 'Egypt'),
('Omariko', 'Germany'),
('George Rassel', 'UK'),
('Kareem Adel', 'Lebanon');


INSERT INTO PUBLISHER (name, country) VALUES
('Dar Al Shorouk', 'Egypt'),
('Penguin Books', 'UK'),
('Springer Verlag', 'Germany');


INSERT INTO CATEGORY (name) VALUES
('Fiction'),
('Technology'),
('Action & Gaming');


INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id) VALUES
('1984', 15.99, 1949, 4, 2, 1),
('Animal Farm', 12.50, 1945, 4, 2, 1),
('Database Systems Guide', 22.00, 2024, 1, 1, 2),
('Python & Flask Mastery', 24.50, 2025, 1, 1, 2),
('Network Security Basics', 18.00, 2023, 1, 3, 2),
('The Queen', 19.50, 2021, 2, 1, 1),
('Alexandria Nights', 14.00, 2022, 2, 1, 1),
('Clean SQL Queries', 27.00, 2026, 2, 2, 2),
('Call of Duty Tactics', 29.99, 2023, 3, 3, 3),
('Sim Racing Physics', 35.00, 2026, 3, 3, 3);

INSERT INTO MEMBER (name, email, join_date) VALUES
('Ahmed', 'ahmed@example.com', '2025-01-10'),
('Mariam', 'mariam@example.com', '2025-02-14'),
('Mazen', 'mazen@example.com', '2025-03-20'),
('Shahd', 'shahd@example.com', '2025-04-05'),
('Mona', 'mona@example.com', '2025-05-12');


INSERT INTO LOAN (book_id, member_id, loan_date, return_date) VALUES
(1, 1, '2026-09-01', '2026-09-10'),
(1, 2, '2026-09-15', '2026-09-25'),
(1, 3, '2026-10-01', NULL),
(3, 1, '2026-09-05', '2026-09-18'),
(3, 4, '2026-10-05', '2026-10-15'),
(4, 1, '2026-10-10', NULL),
(2, 2, '2026-09-12', '2026-09-20'),
(5, 3, '2026-10-12', '2026-10-22'),
(6, 1, '2026-10-18', '2026-10-28'),
(7, 2, '2026-10-20', NULL),
(8, 4, '2026-10-25', '2026-11-02'),
(4, 3, '2026-11-01', '2026-11-09');
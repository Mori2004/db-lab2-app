USE library;


SELECT b.book_id, b.title, b.price, b.publish_year,
       a.name AS author_name, p.name AS publisher_name, c.name AS category_name
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
LEFT JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
LEFT JOIN CATEGORY c ON b.category_id = c.category_id
WHERE b.title LIKE '%a%'
  AND b.price BETWEEN 10 AND 30
  AND b.category_id = 1
ORDER BY b.price ASC;


SELECT b.book_id, b.title, b.price, b.publish_year,
       a.name AS author_name, p.name AS publisher_name, c.name AS category_name
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
LEFT JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
LEFT JOIN CATEGORY c ON b.category_id = c.category_id
ORDER BY b.book_id ASC;


SELECT c.name AS category_name, COUNT(b.book_id) AS book_count, AVG(b.price) AS avg_price
FROM CATEGORY c
LEFT JOIN BOOK b ON c.category_id = b.category_id
GROUP BY c.category_id, c.name;


SELECT a.author_id, a.name AS author_name, COUNT(b.book_id) AS book_count
FROM AUTHOR a
JOIN BOOK b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(b.book_id) >= 2;


SELECT SUM(price) AS total_price, MIN(price) AS smallest_price, MAX(price) AS largest_price
FROM BOOK;


SELECT l.loan_id, b.title AS book_title, m.name AS member_name, l.loan_date
FROM LOAN l
JOIN BOOK b ON l.book_id = b.book_id
JOIN MEMBER m ON l.member_id = m.member_id
WHERE l.return_date IS NULL;


SELECT m.member_id, m.name, m.email, m.join_date
FROM MEMBER m
LEFT JOIN LOAN l ON m.member_id = l.member_id
WHERE l.loan_id IS NULL;


SELECT b.book_id, b.title, b.price, b.publish_year
FROM BOOK b
LEFT JOIN LOAN l ON b.book_id = l.book_id
WHERE l.loan_id IS NULL;


SELECT b.book_id, b.title, COUNT(l.loan_id) AS loan_count
FROM BOOK b
JOIN LOAN l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title
ORDER BY loan_count DESC
LIMIT 3;


SELECT m.member_id, m.name, m.email, COUNT(l.loan_id) AS loan_count
FROM MEMBER m
JOIN LOAN l ON m.member_id = l.member_id
GROUP BY m.member_id, m.name, m.email
ORDER BY loan_count DESC
LIMIT 1;


SELECT a.author_id, a.name, a.country, COUNT(b.book_id) AS book_count
FROM AUTHOR a
LEFT JOIN BOOK b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name, a.country;


SELECT b.book_id, b.title, a.name AS author_name, p.name AS publisher_name, a.country
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country;
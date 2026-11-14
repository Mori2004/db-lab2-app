# Database Labs: Flask & MySQL Web App

**Team Members:**
* Omar Nassret (ID: 2304250)
* Omar Osama (ID: 2304240)

This repository contains the complete deliverables for Database Labs 2, 3, and 4. The project is a Python Flask web application integrated with multiple MySQL databases, featuring user authentication, a To-Do list, and a Library Management System with advanced SQL search, join, and aggregate reporting pages. It also includes raw backend SQL scripts for a Company database schema.

## 📂 Project Structure

- **`/website`**: Contains the core Flask application (`app.py`), HTML templates (Bootstrap 5), and dependencies.
- **`/` (Root)**: Contains the SQL DDL, DML, query scripts, and answers for Lab 4 (`company` and `library` databases).

## 🚀 Features

1. **Authentication System (Lab 2)**
   - Secure user registration and login using `bcrypt` password hashing.
   - Connected to the `registration` MySQL database.

2. **To-Do Task Manager (Lab 2)**
   - Logged-in users can Create, Read, Update, and Delete (CRUD) personal tasks.
   - Tasks are isolated per user via session management.

3. **Library Management & Search System (Lab 3 & Lab 4 - Part II)**
   - CRUD interface for `BOOKS` and `AUTHORS` connected to the `library` MySQL database.
   - **F2.1 Search Books**: Filter books by title keyword (`LIKE`), price range (`BETWEEN`), and category using prepared statements (`%s` placeholders), sorted cheapest first.
   - **F2.2 Catalogue**: Full book catalogue joining `BOOK`, `AUTHOR`, `PUBLISHER`, and `CATEGORY`.
   - **F2.3 Reports**: Category book counts & average prices (`GROUP BY`), prolific authors with $\ge 2$ books (`HAVING`), and library total/min/max book price summary.
   - **F2.4 Loans**: Unreturned loans (`return_date IS NULL`), members who never borrowed a book (`LEFT JOIN`), and books never borrowed (`LEFT JOIN`).
   - **F2.5 Most Borrowed**: Top 3 most borrowed books and top borrowing member (`ORDER BY` + `LIMIT`).
   - **F2.6 Authors & Books**: All authors with book counts including 0 (`LEFT JOIN`), and books whose author and publisher come from the same country.

4. **Company Schema (Lab 4 - Part I)**
   - Extended `DDL` and `DML` SQL scripts building the `company` database (`EMPLOYEE`, `DEPARTMENT`, `PROJECT`, `WORKS_ON`, `DEPENDENT`) and answers in `problem1_Answers.txt`.

## 🛠️ Tech Stack
- **Backend:** Python, Flask, PyMySQL, Bcrypt
- **Frontend:** HTML5, Bootstrap 5.3, Jinja2
- **Database:** MySQL (managed via DBeaver)

## ⚙️ How to Run Locally

1. **Install Dependencies:**
   ```bash
   pip install -r website/requirements.txt
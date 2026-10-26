# Database Labs: Flask & MySQL Web App

**Team Members:**
* Omar Nassret (ID: 2304250)
* Omar Osama (ID: 2304240)

This repository contains the complete deliverables for Database Labs 2 and 3. The project is a Python Flask web application integrated with multiple MySQL databases, featuring user authentication, a To-Do list, and a Library Management System. It also includes raw backend SQL scripts for a Company database schema.

## 📂 Project Structure

- **`/website`**: Contains the core Flask application, HTML templates (Bootstrap 5), and dependencies.
- **`/` (Root)**: Contains the SQL DDL/DML scripts and answers for Lab 3 (Company and Library databases).

## 🚀 Features

1. **Authentication System (Lab 2)**
   - Secure user registration and login using `bcrypt` password hashing.
   - Connected to the `registration` MySQL database.

2. **To-Do Task Manager (Lab 2)**
   - Logged-in users can Create, Read, Update, and Delete (CRUD) personal tasks.
   - Tasks are isolated per user via session management.

3. **Library Management System (Lab 3 - Part 2)**
   - Fully dynamic CRUD interface for `BOOKS` and `AUTHORS`.
   - Connected to the `library` MySQL database.
   - Enforces relational constraints (e.g., deleting an author cascades to delete their books).
   - image formate of PNJ is adedd for Author and Books cover

4. **Company Schema (Lab 3 - Part 1)**
   - Raw `DDL` and `DML` SQL scripts building the `company` database.
   - Includes circular dependency resolution and foreign key constraint answers in `problem1_Answers.txt`.

## 🛠️ Tech Stack
- **Backend:** Python, Flask, PyMySQL, Bcrypt
- **Frontend:** HTML5, Bootstrap 5.3, Jinja2
- **Database:** MySQL (managed via DBeaver)

## ⚙️ How to Run Locally

1. **Install Dependencies:**
   ```bash
   pip install -r website/requirements.txt
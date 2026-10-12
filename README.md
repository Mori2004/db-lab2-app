# Database Lab 2: Login & To-Do Application

## 1. Names
* Member 1: [Omar Nassret] - [2304250]
* Member 2: [Omar Osama] - [2304240]

## 2. Stack
* **Back End:**  Python (Flask)
* **Front End:**  HTML, Bootstrap 5, JavaScript
* **Database:**  MySQL

## 3. How to Run
1. Run `database/schema.sql` in DBeaver to set up the database.
2. Install Python dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in my local MySQL password.
4. Run the Flask server: `python app.py`
5. Open browser at `http://127.0.0.1:5000`

## 4. Requirements
* R1: Register page with duplicate email check
* R2: Login page with bcrypt authentication
* R3: Protected route for private user lists
* R4-R7: Add, edit, toggle done, delete to-dos with confirmation
* R8: Form validation in browser and server
* R9: Prepared statements
* R10: Responsive layout

## 5. Answers
(a) The todo_id comes from the user and another user could modify requests to another user task adding AND user_id = ? allow that a user can only alter their own tasks if removed any logged in user could edit or delete anyone else's tasks

(b) MySQL rejects the query with Error 1452 (Foreign key constraint fails) this represents the Referential Integrity Constraint

(c) Plaintext passwords expose credentials if the database leaks  bcrypt hashes prevent rainbow table attacks and are computationally slow

(d) NOT NULL prevents NULL values but empty strings ("") or spaces are non-NULL Server checks are required to catch empty string input
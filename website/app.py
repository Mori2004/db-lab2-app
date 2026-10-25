import os
import pymysql
import re
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "registration"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )



# ==========================================
# 1. TO-DO & AUTHENTICATION ROUTES (LAB 2)
# ==========================================



@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC;"
        cursor.execute(sql, (session["user_id"],))
        todos = cursor.fetchall()
    conn.close()

    return render_template("index.html", todos=todos, user_name=session.get("user_name"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Please enter a valid email address (e.g., user@example.com).', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                conn.close()
                flash('Email address is already registered!', 'error')
                return redirect(url_for('register'))

            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_pw)
            )
            conn.commit()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        errors = []
        if not email:
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("login.html", email=email)

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Fixed column names to match the registration insert statement
            sql = "SELECT id, name, password FROM users WHERE email = %s;"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
        conn.close()

        if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            flash("Invalid email or password", "danger")
            return render_template("login.html", email=email)

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    if not title:
        flash("Title is required", "danger")
    elif len(title) > 200:
        flash("Title is too long", "danger")
    else:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO todos (user_id, title) VALUES (%s, %s);"
            cursor.execute(sql, (session["user_id"], title))
        conn.close()

    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    if not title:
        flash("Title is required", "danger")
    elif len(title) > 200:
        flash("Title is too long", "danger")
    else:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s;"
            cursor.execute(sql, (title, todo_id, session["user_id"]))
        conn.close()

    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
def toggle_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    is_done = 1 if request.form.get("is_done") == "1" else 0
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s;"
        cursor.execute(sql, (is_done, todo_id, session["user_id"]))
    conn.close()

    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "DELETE FROM todos WHERE todo_id = %s AND user_id = %s;"
        cursor.execute(sql, (todo_id, session["user_id"]))
    conn.close()

    return redirect(url_for("index"))




# ==========================================
# 2. LIBRARY ROUTES (LAB 3 ADDITIONS)
# ==========================================




@app.route('/books')
def list_books():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM BOOK")
        books = cursor.fetchall()
        cursor.execute("SELECT * FROM AUTHOR")
        authors = cursor.fetchall()
    conn.close()
    return render_template('books.html', books=books, authors=authors)

@app.route('/authors')
def list_authors():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM AUTHOR")
        authors = cursor.fetchall()
    conn.close()
    return render_template('authors.html', authors=authors)

@app.route('/books/add', methods=['POST'])
def add_book():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    title = request.form['title']
    price = request.form['price']
    author_id = request.form['author_id']
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO BOOK (title, price, author_id) VALUES (%s, %s, %s)", (title, price, author_id))
    conn.close()
    flash('Book added successfully!', 'success')
    return redirect(url_for('list_books'))

@app.route('/authors/add', methods=['POST'])
def add_author():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    name = request.form['name']
    country = request.form['country']
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO AUTHOR (name, country) VALUES (%s, %s)", (name, country))
    conn.close()
    flash('Author added successfully!', 'success')
    return redirect(url_for('list_authors'))

@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        author_id = request.form['author_id']
        with conn.cursor() as cursor:
            cursor.execute("UPDATE BOOK SET title=%s, price=%s, author_id=%s WHERE book_id=%s", (title, price, author_id, book_id))
        conn.close()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('list_books'))
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM BOOK WHERE book_id=%s", (book_id,))
        book = cursor.fetchone()
        cursor.execute("SELECT * FROM AUTHOR")
        authors = cursor.fetchall()
    conn.close()
    return render_template('edit_book.html', book=book, authors=authors)

@app.route('/authors/edit/<int:author_id>', methods=['GET', 'POST'])
def edit_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        country = request.form['country']
        with conn.cursor() as cursor:
            cursor.execute("UPDATE AUTHOR SET name=%s, country=%s WHERE author_id=%s", (name, country, author_id))
        conn.close()
        flash('Author updated successfully!', 'success')
        return redirect(url_for('list_authors'))
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM AUTHOR WHERE author_id=%s", (author_id,))
        author = cursor.fetchone()
    conn.close()
    return render_template('edit_author.html', author=author)

@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM BOOK WHERE book_id=%s", (book_id,))
    conn.close()
    flash('Book deleted!', 'danger')
    return redirect(url_for('list_books'))

@app.route('/authors/delete/<int:author_id>', methods=['POST'])
def delete_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM AUTHOR WHERE author_id=%s", (author_id,))
    conn.close()
    flash('Author deleted! Associated books deleted via ON DELETE CASCADE.', 'danger')
    return redirect(url_for('list_authors'))

if __name__ == "__main__":
    app.run(debug=True)
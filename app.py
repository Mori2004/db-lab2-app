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

        # 1. Check if email contains @ and a valid domain format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Please enter a valid email address (e.g., user@example.com).', 'error')
            return redirect(url_for('register'))

        # 2. Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        # 3. Check if email already exists in database
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                conn.close()
                flash('Email address is already registered!', 'error')
                return redirect(url_for('register'))

            # Hash password and insert user
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
            sql = "SELECT user_id, name, password_hash FROM users WHERE email = %s;"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
        conn.close()

        if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            flash("Invalid email or password", "danger")
            return render_template("login.html", email=email)

        session["user_id"] = user["user_id"]
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

if __name__ == "__main__":
    app.run(debug=True)
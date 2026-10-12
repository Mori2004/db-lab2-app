import os
import pymysql
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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not name:
            errors.append("Name is required")
        if not email:
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")
        if not confirm_password:
            errors.append("Confirm password is required")
        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("register.html", name=name, email=email)

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s);"
                cursor.execute(sql, (email, name, hashed_password))
                
                cursor.execute("SELECT user_id FROM users WHERE email = %s;", (email,))
                user = cursor.fetchone()
                
                session["user_id"] = user["user_id"]
                session["user_name"] = name
                return redirect(url_for("index"))
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:
                flash("Email Already Exists", "danger")
                return render_template("register.html", name=name, email=email)
            raise e
        finally:
            conn.close()

    return render_template("register.html")

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
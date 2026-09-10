from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# کلید مخصوص Session
app.secret_key = "A7x!92Kp#4Lm$8Qz"


# =========================
# DATABASE
# =========================

def create_database():
    conn = sqlite3.connect("messages.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    # اضافه کردن تاریخ به دیتابیس‌های قدیمی
    try:
        conn.execute(
            "ALTER TABLE messages ADD COLUMN created_at TEXT"
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# ABOUT
# =========================

@app.route("/about")
def about():
    return render_template("about.html")


# =========================
# CONTACT
# =========================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        # جلوگیری از ارسال فرم خالی
        if not name or not email or not message:
            return render_template(
                "contact.html",
                error="لطفاً همه قسمت‌ها را کامل کنید ❌"
            )

        conn = sqlite3.connect("messages.db")

        conn.execute(
            """
            INSERT INTO messages
            (name, email, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                message,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("success"))

    return render_template("contact.html")


# =========================
# SUCCESS
# =========================

@app.route("/success")
def success():
    return render_template("success.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "admin" and password == "Amin9876":

            session["logged_in"] = True

            return redirect(url_for("admin"))

        return render_template(
            "login.html",
            error="نام کاربری یا رمز عبور اشتباه است ❌"
        )

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("logged_in", None)

    return redirect(url_for("login"))


# =========================
# ADMIN PANEL
# =========================

@app.route("/admin")
def admin():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("messages.db")

    messages = conn.execute(
        """
        SELECT *
        FROM messages
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        messages=messages
    )


# =========================
# DELETE MESSAGE
# =========================

@app.route(
    "/delete-message/<int:message_id>",
    methods=["POST"]
)
def delete_message(message_id):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("messages.db")

    conn.execute(
        "DELETE FROM messages WHERE id = ?",
        (message_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# =========================
# START
# =========================

create_database()

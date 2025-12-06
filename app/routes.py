from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_connection
from datetime import date, timedelta



main = Blueprint("main", __name__)


@main.route("/login", methods=["GET", "POST"])
def login():
    # If user submitted the form
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Get user from DB
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, name, email, password_hash FROM Users WHERE email = ?;",
            (email,),
        )
        user = cur.fetchone()
        conn.close()

        # If no user or password doesn't match
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        # Successful login -> store in session
        session["user_id"] = user["user_id"]
        session["user_name"] = user["name"]

        return redirect(url_for("main.dashboard"))

    # GET request -> just show the login page
    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        errors = []

        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        if not password:
            errors.append("Password is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                flash(e, "error")
            # Refill name/email in form
            return render_template("register.html", name=name, email=email)

        conn = get_connection()
        cur = conn.cursor()

        # Check if email already exists
        cur.execute("SELECT user_id FROM Users WHERE email = ?;", (email,))
        existing = cur.fetchone()
        if existing:
            conn.close()
            flash("Email already registered. Please log in instead.", "error")
            return render_template("register.html", name=name, email=email)

        # Hash the password
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")


        # Insert user
        cur.execute(
            "INSERT INTO Users (name, email, password_hash) VALUES (?, ?, ?);",
            (name, email, password_hash),
        )
        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main.login"))

    # GET request -> show empty form
    return render_template("register.html")


@main.route("/dashboard")
def dashboard():
    # Protect this route: require login
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]
    user_name = session.get("user_name")

    today = date.today()
    today_str = today.isoformat()

    # Start of this month
    month_start = today.replace(day=1).isoformat()

    # Last 7 days (including today)
    week_start = (today - timedelta(days=6)).isoformat()

    conn = get_connection()
    cur = conn.cursor()

    # Total all-time
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM Expenses WHERE user_id = ?;",
        (user_id,),
    )
    total_all = cur.fetchone()["total"]

    # Total this month
    cur.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM Expenses
        WHERE user_id = ?
          AND expense_date BETWEEN ? AND ?;
        """,
        (user_id, month_start, today_str),
    )
    total_month = cur.fetchone()["total"]

    # Total last 7 days
    cur.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM Expenses
        WHERE user_id = ?
          AND expense_date BETWEEN ? AND ?;
        """,
        (user_id, week_start, today_str),
    )
    total_week = cur.fetchone()["total"]

    conn.close()

    return render_template(
        "dashboard.html",
        user_name=user_name,
        total_all=total_all,
        total_month=total_month,
        total_week=total_week,
    )



@main.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    # Require login
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        amount = request.form.get("amount")
        expense_date = request.form.get("expense_date")
        category_id = request.form.get("category_id")
        description = request.form.get("description")

        errors = []

        # Basic validation
        if not amount:
            errors.append("Amount is required.")
        else:
            try:
                amt = float(amount)
                if amt <= 0:
                    errors.append("Amount must be greater than 0.")
            except ValueError:
                errors.append("Amount must be a valid number.")

        if not expense_date:
            errors.append("Date is required.")
        if not category_id:
            errors.append("Category is required.")

        if errors:
            for e in errors:
                flash(e, "error")
            # Reload categories and re-render the form
            cur.execute("SELECT category_id, category_name FROM Categories ORDER BY category_name;")
            categories = cur.fetchall()
            conn.close()
            return render_template("add_expense.html", categories=categories)

        # If everything is valid, insert the expense
        cur.execute(
            """
            INSERT INTO Expenses (user_id, category_id, amount, expense_date, description)
            VALUES (?, ?, ?, ?, ?);
            """,
            (user_id, category_id, amt, expense_date, description),
        )

        conn.commit()
        conn.close()

        flash("Expense added successfully.", "success")
        return redirect(url_for("main.dashboard"))

    # GET request: show the form with categories
    cur.execute("SELECT category_id, category_name FROM Categories ORDER BY category_name;")
    categories = cur.fetchall()
    conn.close()
    return render_template("add_expense.html", categories=categories)

@main.route("/expenses/history")
def view_history():
    # Require login
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    # Get all expenses for this user, with category name
    cur.execute(
        """
        SELECT e.expense_id,
               e.expense_date,
               e.amount,
               e.description,
               c.category_name
        FROM Expenses e
        JOIN Categories c ON e.category_id = c.category_id
        WHERE e.user_id = ?
        ORDER BY e.expense_date DESC, e.created_at DESC;
        """,
        (user_id,),
    )

    expenses = cur.fetchall()
    conn.close()

    return render_template("history.html", expenses=expenses)


@main.route("/logout")
def logout():
    # Clear all session data
    session.clear()

    # Notify the user
    flash("You have been logged out.", "success")

    # Redirect to login page
    return redirect(url_for("main.login"))



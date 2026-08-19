from flask import Flask, render_template, request, redirect, url_for, flash
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal

app = Flask(__name__)
app.secret_key = "hotel-project-secret-key"

def get_db():
    return psycopg2.connect(
        os.environ.get("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )

@app.route("/")
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM customers")
    customers = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM rooms")
    rooms = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM bookings")
    bookings = cur.fetchone()["total"]
    cur.execute("SELECT COALESCE(SUM(amount),0) AS total FROM payments")
    revenue = cur.fetchone()["total"]
    cur.close()
    conn.close()
    return render_template("dashboard.html", customers=customers, rooms=rooms,
                           bookings=bookings, revenue=revenue)

@app.route("/customers")
def customers():
    conn = get_db()
   cur = conn.cursor()
    cur.execute("SELECT * FROM customers ORDER BY customer_id DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("customers.html", customers=rows)

@app.route("/customers/add", methods=["POST"])
def add_customer():
    data = request.form
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO customers (customer_name, phone, email, address) VALUES (%s,%s,%s,%s)",
        (data["customer_name"], data["phone"], data["email"], data["address"])
    )
    conn.commit()
    cur.close(); conn.close()
    flash("Customer added successfully.")
    return redirect(url_for("customers"))

@app.route("/customers/delete/<int:id>", methods=["POST"])
def delete_customer(id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM customers WHERE customer_id=%s", (id,))
        conn.commit()
        flash("Customer deleted successfully.")
    except Error as e:
        conn.rollback()
        flash(f"Cannot delete customer: {e}")
    cur.close(); conn.close()
    return redirect(url_for("customers"))

@app.route("/rooms")
def rooms():
    conn = get_db()
     cur = conn.cursor()
    cur.execute("SELECT * FROM rooms ORDER BY room_number")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("rooms.html", rooms=rows)

@app.route("/rooms/add", methods=["POST"])
def add_room():
    data = request.form
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES (%s,%s,%s,%s)",
        (data["room_number"], data["room_type"], data["price_per_night"], "Available")
    )
    conn.commit()
    cur.close(); conn.close()
    flash("Room added successfully.")
    return redirect(url_for("rooms"))

@app.route("/bookings")
def bookings():
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT b.booking_id, c.customer_name, r.room_number, r.room_type,
               b.check_in, b.check_out, b.status
        FROM bookings b
        JOIN customers c ON b.customer_id = c.customer_id
        JOIN rooms r ON b.room_id = r.room_id
        ORDER BY b.booking_id DESC
    """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("bookings.html", bookings=rows)

@app.route("/bookings/add", methods=["POST"])
def add_booking():
    data = request.form
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO bookings (customer_id, room_id, check_in, check_out, status)
            VALUES (%s,%s,%s,%s,'Confirmed')
        """, (data["customer_id"], data["room_id"], data["check_in"], data["check_out"]))
        conn.commit()
        flash("Booking added. Trigger automatically changed the room status to Booked.")
    except Error as e:
        conn.rollback()
        flash(f"Booking failed: {e}")
    cur.close(); conn.close()
    return redirect(url_for("bookings"))

@app.route("/new-booking")
def new_booking():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT customer_id, customer_name FROM customers ORDER BY customer_name")
    customers = cur.fetchall()
    cur.execute("SELECT room_id, room_number, room_type, price_per_night FROM rooms WHERE status='Available' ORDER BY room_number")
    rooms = cur.fetchall()
    cur.close(); conn.close()
    return render_template("new_booking.html", customers=customers, rooms=rooms)

@app.route("/payments")
def payments():
    conn = get_db()
     cur = conn.cursor()
    cur.execute("""
        SELECT p.payment_id, c.customer_name, p.booking_id, p.amount,
               p.payment_date, p.payment_method
        FROM payments p
        JOIN bookings b ON p.booking_id=b.booking_id
        JOIN customers c ON b.customer_id=c.customer_id
        ORDER BY p.payment_id DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("payments.html", payments=rows)

@app.route("/payments/add", methods=["POST"])
def add_payment():
    data = request.form
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO payments (booking_id, amount, payment_method)
        VALUES (%s,%s,%s)
    """, (data["booking_id"], data["amount"], data["payment_method"]))
    conn.commit()
    cur.close(); conn.close()
    flash("Payment added successfully.")
    return redirect(url_for("payments"))

@app.route("/reports")
def reports():
    conn = get_db()
     cur = conn.cursor()
    cur.execute("""
        SELECT c.customer_name, r.room_number, r.room_type,
               b.check_in, b.check_out, b.status
        FROM bookings b
        JOIN customers c ON b.customer_id=c.customer_id
        JOIN rooms r ON b.room_id=r.room_id
        ORDER BY b.check_in DESC
    """)
    booking_report = cur.fetchall()

    cur.execute("""
        SELECT r.room_type, COUNT(*) AS bookings_count,
               COALESCE(SUM(p.amount),0) AS revenue
        FROM rooms r
        LEFT JOIN bookings b ON r.room_id=b.room_id
        LEFT JOIN payments p ON b.booking_id=p.booking_id
        GROUP BY r.room_type
    """)
    room_report = cur.fetchall()
    cur.close(); conn.close()
    return render_template("reports.html", booking_report=booking_report, room_report=room_report)

if __name__ == "__main__":
    app.run(debug=True)

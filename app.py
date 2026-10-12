import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

from datetime import datetime

from functools import wraps

from dbfunc import fetch_all, execute_query

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ["FLASK_SECRET_KEY"]

# =========================

# HELPERS

# =========================

def current_year():

    return datetime.now().year

def get_user():

    return session.get("user_id")

def get_role():

    return session.get("role")

# =========================

# ADMIN DECORATOR

# =========================

def admin_required(f):

    @wraps(f)

    def wrapper(*args, **kwargs):

        if not session.get("user_id"):

            flash("Please login first", "error")

            return redirect(url_for("login"))

        if session.get("role") != "admin":

            flash("Admin access denied", "error")

            return redirect(url_for("index"))

        return f(*args, **kwargs)

    return wrapper

# =========================

# HOME (INDEX PAGE FIXED)

# =========================

@app.route('/')

def index():

    events_data = fetch_all("""

        SELECT events.*,

               venues.name AS venue_name,

               event_categories.name AS category_name

        FROM events

        JOIN venues ON events.venue_id = venues.venue_id

        JOIN event_categories ON events.category_id = event_categories.category_id

        ORDER BY events.event_date ASC

        LIMIT 6

    """) or []

    return render_template(

        "index.html",

        events=events_data,

        current_year=current_year()

    )

# =========================

# EVENTS

# =========================

@app.route('/events')

def events():

    search = (request.args.get('search') or '').strip()

    category = (request.args.get('category') or '').strip()

    price = (request.args.get('price') or '').strip()

    query = """

        SELECT events.*,

               venues.name AS venue_name,

               event_categories.name AS category_name

        FROM events

        JOIN venues ON events.venue_id = venues.venue_id

        JOIN event_categories ON events.category_id = event_categories.category_id

        WHERE 1=1

    """

    params = []

    if search:

        query += " AND events.title LIKE %s"

        params.append(f"%{search}%")

    if category:

        query += " AND event_categories.name = %s"

        params.append(category)

    if price == "free":

        query += " AND events.price = 0"

    elif price == "low":

        query += " AND events.price > 0 AND events.price <= 20"

    elif price == "high":

        query += " AND events.price > 20"

    query += " ORDER BY events.event_date ASC"

    events_data = fetch_all(query, tuple(params)) or []

    return render_template(

        'events.html',

        events=events_data,

        current_year=current_year()

    )

# =========================

# EVENT DETAIL (SAFE FIX)

# =========================

@app.route('/event/<int:event_id>')

def event_detail(event_id):

    event = fetch_all("""

        SELECT events.*,

               venues.name AS venue_name,

               event_categories.name AS category_name

        FROM events

        JOIN venues ON events.venue_id = venues.venue_id

        JOIN event_categories ON events.category_id = event_categories.category_id

        WHERE events.event_id = %s

    """, (event_id,)) or []

    if len(event) == 0:

        return "Event not found", 404

    return render_template(

        "event_detail.html",

        event=event[0],

        current_year=current_year()

    )

# =========================

# BOOK EVENT

# =========================

@app.route('/book_event/<int:event_id>', methods=['POST'])

def book_event(event_id):

    if not get_user():

        return redirect(url_for('login'))

    try:

        tickets = int(request.form.get('tickets', 1))

    except:

        flash("Invalid ticket number", "error")

        return redirect(url_for('event_detail', event_id=event_id))

    event = fetch_all("SELECT * FROM events WHERE event_id=%s", (event_id,)) or []

    if len(event) == 0:

        return "Event not found", 404

    event = event[0]

    if tickets <= 0:

        flash("Invalid tickets", "error")

        return redirect(url_for('event_detail', event_id=event_id))

    if event['available_tickets'] < tickets:

        flash("Not enough tickets", "error")

        return redirect(url_for('event_detail', event_id=event_id))

    total_price = float(event['price']) * tickets

    execute_query("""

        INSERT INTO bookings

        (user_id, event_id, tickets_booked, price_at_booking, total_price, status)

        VALUES (%s,%s,%s,%s,%s,%s)

    """, (

        get_user(),

        event_id,

        tickets,

        event['price'],

        total_price,

        "confirmed"

    ))

    execute_query("""

        UPDATE events

        SET available_tickets = available_tickets - %s

        WHERE event_id = %s

    """, (tickets, event_id))

    flash("Booking successful!", "success")

    return redirect(url_for('event_detail', event_id=event_id))

# =========================

# VENUES

# =========================

@app.route('/venues')

def venues():

    venues_data = fetch_all("SELECT * FROM venues ORDER BY name ASC") or []

    return render_template("venues.html",

                           venues=venues_data,

                           current_year=current_year())

# =========================

# VENUE DETAIL

# =========================

@app.route('/venue/<int:venue_id>')

def venue_detail(venue_id):

    venue = fetch_all("SELECT * FROM venues WHERE venue_id=%s", (venue_id,)) or []

    if len(venue) == 0:

        return "Venue not found", 404

    events_data = fetch_all("""

        SELECT events.*,

               event_categories.name AS category_name

        FROM events

        JOIN event_categories ON events.category_id = event_categories.category_id

        WHERE events.venue_id=%s

        ORDER BY events.event_date ASC

    """, (venue_id,)) or []

    return render_template(

        "venue_detail.html",

        venue=venue[0],

        events=events_data,

        current_year=current_year()

    )

# =========================

# EVENTS BY VENUE

# =========================

@app.route('/events/venue/<int:venue_id>')

def events_by_venue(venue_id):

    events_data = fetch_all("""

        SELECT events.*,

               venues.name AS venue_name,

               event_categories.name AS category_name

        FROM events

        JOIN venues ON events.venue_id = venues.venue_id

        JOIN event_categories ON events.category_id = event_categories.category_id

        WHERE events.venue_id=%s

        ORDER BY events.event_date ASC

    """, (venue_id,)) or []

    return render_template(

        "events.html",

        events=events_data,

        current_year=current_year()

    )

# =========================

# STATIC PAGES

# =========================

@app.route('/about')

def about():

    return render_template("about.html", current_year=current_year())

@app.route('/contact')

def contact():

    return render_template("contact.html", current_year=current_year())

@app.route('/legal')

def legal():

    return render_template("legal.html", current_year=current_year())

@app.route('/forgot')

def forgot():

    return render_template("forgot.html", current_year=current_year())

# =========================

# MY BOOKINGS (SAFE FIX)

# =========================

@app.route('/my_bookings')

def my_bookings():

    if not get_user():

        return redirect(url_for('login'))

    bookings = fetch_all("""

        SELECT 

            bookings.*,

            events.title,

            events.event_date,

            venues.name AS venue_name

        FROM bookings

        JOIN events ON bookings.event_id = events.event_id

        JOIN venues ON events.venue_id = venues.venue_id

        WHERE bookings.user_id = %s

        ORDER BY bookings.booking_date DESC

    """, (get_user(),)) or []

    return render_template(

        "my_bookings.html",

        bookings=bookings,

        current_year=current_year()

    )

# =========================

# BOOKING DETAIL

# =========================

@app.route('/booking/<int:booking_id>')

def booking_detail(booking_id):

    if not get_user():

        return redirect(url_for('login'))

    booking = fetch_all("""

        SELECT 

            bookings.*,

            events.title,

            events.description,

            events.event_date,

            venues.name AS venue_name

        FROM bookings

        JOIN events ON bookings.event_id = events.event_id

        JOIN venues ON events.venue_id = venues.venue_id

        WHERE bookings.booking_id = %s

    """, (booking_id,)) or []

    if len(booking) == 0:

        return "Booking not found", 404

    return render_template(

        "booking_detail.html",

        booking=booking[0],

        current_year=current_year()

    )

# =========================

# LOGIN (FIXED CRASH)

# =========================

@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        email = (request.form.get('email') or '').strip()

        password = request.form.get('password')

        user = fetch_all("SELECT * FROM users WHERE email=%s", (email,)) or []

        if len(user) == 0:

            flash("Invalid login", "error")

            return redirect(url_for('login'))

        user = user[0]

        if not check_password_hash(user['password_hash'], password):

            flash("Invalid login", "error")

            return redirect(url_for('login'))

        session['user_id'] = user['user_id']

        session['role'] = user.get('role', 'customer')

        session['user_name'] = user['first_name']

        flash("Logged in!", "success")

        return redirect(url_for('index'))

    return render_template("login.html", current_year=current_year())

# =========================

# LOGOUT

# =========================

@app.route('/logout')

def logout():

    session.clear()

    flash("Logged out", "success")

    return redirect(url_for('index'))

# =========================

# REGISTER

# =========================

@app.route('/register', methods=['GET', 'POST'])

def register():

    if request.method == 'POST':

        email = request.form.get('email')

        exists = fetch_all("SELECT * FROM users WHERE email=%s", (email,)) or []

        if len(exists) > 0:

            flash("Email already exists", "error")

            return redirect(url_for('register'))

        password = generate_password_hash(request.form.get('password'))

        execute_query("""

            INSERT INTO users(first_name,last_name,email,password_hash,role)

            VALUES (%s,%s,%s,%s,%s)

        """, (

            request.form.get('first_name'),

            request.form.get('last_name'),

            email,

            password,

            "customer"

        ))

        flash("Account created!", "success")

        return redirect(url_for('login'))

    return render_template("register.html", current_year=current_year())

# =========================

# ADMIN (SAFE FIX)

# =========================

@app.route('/admin')

@admin_required

def admin():

    users = fetch_all("SELECT * FROM users") or []

    events_data = fetch_all("SELECT * FROM events") or []

    venues_data = fetch_all("SELECT * FROM venues") or []

    total_users = fetch_all("SELECT COUNT(*) AS total FROM users")[0]['total'] or 0

    total_events = fetch_all("SELECT COUNT(*) AS total FROM events")[0]['total'] or 0

    total_bookings = fetch_all("SELECT COUNT(*) AS total FROM bookings")[0]['total'] or 0

    revenue = fetch_all("SELECT IFNULL(SUM(total_price),0) AS total FROM bookings")[0]['total'] or 0

    return render_template(

        "admin.html",

        users=users,

        events=events_data,

        venues=venues_data,

        total_users=total_users,

        total_events=total_events,

        total_bookings=total_bookings,

        revenue=revenue,

        current_year=current_year()

    )

# =========================

# RUN

# =========================

if __name__ == "__main__":

    app.run(debug=False)

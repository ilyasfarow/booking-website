# Event Booking Website

A full-stack event booking web application developed using **Python, Flask and MySQL** as part of a university project.

The application allows users to browse events, explore venues, register accounts, log in and book event tickets. It also includes an administration dashboard for viewing users, events, venues and booking statistics.

## Features

### User Features
- **User Registration and Login:** Account creation and authentication using password hashing.
- **Event Browsing:** View upcoming events and filter by category, price or search term.
- **Event Booking:** Book tickets for available events, with ticket quantity validation.
- **Booking History:** View previous bookings and booking details.
- **Venue Information:** Browse venues and view their associated events.

### Administration
- Role-based access to an administrator dashboard.
- View registered users, events and venues.
- Display booking totals and revenue statistics.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework and routing |
| MySQL | Relational database |
| HTML | Webpage structure |
| CSS | Website styling |
| Jinja2 | Dynamic HTML templates |
| Git & GitHub | Version control |

## Project Structure

```text
booking-website/
├── app.py                 # Flask routes and application logic
├── dbfunc.py              # Database connection and query functions
├── static/
│   ├── images/            # Website images and assets
│   └── style/             # CSS styling
├── templates/             # HTML/Jinja2 templates
├── .gitignore
└── README.md
```

## How It Works

1. Users register or log in to their accounts.
2. Users browse events and select an event to view its details.
3. The application checks ticket availability before processing a booking.
4. Booking information is stored in a MySQL database.
5. Users can access their booking history through their account.
6. Administrators can view application statistics through the admin dashboard.

## Running the Project Locally

### Prerequisites
- Python 3
- MySQL Server
- A configured MySQL database

### Installation

Clone the repository:

```bash
git clone https://github.com/ilyasfarow/booking-website.git
cd booking-website
```

Install the required Python packages:

```bash
python -m pip install flask mysql-connector-python
```

Configure the database connection in `dbfunc.py` for your local MySQL setup.

Set the following environment variables before running the application:

- `DB_PASSWORD` — your local MySQL password
- `FLASK_SECRET_KEY` — a randomly generated secret for Flask sessions

Run the application:

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

**Note:** The database export is not included in this repository. The application requires the original database schema to run correctly.

## Security and Development Notes

- Passwords are hashed using Werkzeug.
- SQL queries use parameterised inputs.
- Database credentials and Flask session secrets are read from environment variables.
- The application is a university project and is not production-ready.
- Future improvements include transactional booking operations and stricter booking ownership checks.

## Future Improvements

- Add database setup scripts using anonymised sample data.
- Implement automated unit and integration tests.
- Improve booking transaction handling to prevent overselling.
- Strengthen booking authorisation and error handling.
- Deploy a demonstration version of the website.

## Author

**Ilyas Farow**

Computer Science student at the University of the West of England (UWE Bristol).

GitHub: https://github.com/ilyasfarow

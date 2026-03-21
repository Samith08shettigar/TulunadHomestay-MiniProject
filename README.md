# 🏡 Tulunad Homestay

A full-stack web application for managing a homestay in the Tulunad region, built with **Flask** and **SQLite**. Users can browse rooms, book stays, and leave feedback. Admins can manage rooms, bookings, and view feedback from a dedicated dashboard.

---

## ✨ Features

- **User Authentication** — Register, login, and session management
- **Room Browsing** — View available rooms with images, pricing, and capacity
- **Booking System** — Book rooms with date selection, meal type, and campfire options (with double-booking prevention)
- **Feedback System** — Rate and review completed stays
- **Admin Dashboard** — Manage rooms (add/edit), handle bookings (confirm/cancel), and view user feedback
- **Error Handling** — Custom 403 and 404 error pages

---

## 🛠️ Tech Stack

| Layer     | Technology       |
|-----------|------------------|
| Backend   | Python, Flask    |
| Database  | SQLite           |
| Frontend  | HTML, CSS, JavaScript |
| Auth      | Werkzeug (password hashing) |

---

## 📁 Project Structure

```
Tulunad/
├── app.py                  # Application factory & entry point
├── database.py             # SQLite database connection helpers
├── models.py               # Database table definitions
├── helpers.py              # Auth decorators (login_required, admin_required)
├── seed.py                 # Database seeder (admin user + sample rooms)
├── requirements.txt        # Python dependencies
│
├── blueprints/
│   ├── __init__.py
│   ├── auth.py             # Login, register, logout routes
│   ├── admin.py            # Admin dashboard, room & booking management
│   └── user.py             # User dashboard, bookings, feedback
│
├── static/
│   ├── css/style.css       # Global styles
│   └── js/main.js          # Client-side JavaScript
│
├── templates/
│   ├── base.html           # Base layout template
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── 403.html            # Forbidden error page
│   ├── 404.html            # Not found error page
│   ├── admin/              # Admin templates (dashboard, rooms, bookings, feedback)
│   └── user/               # User templates (dashboard, rooms, bookings, feedback)
│
└── instance/
    └── homestay.db         # SQLite database (auto-created)
```

---

## 🚀 Setup Instructions (Windows)

### Prerequisites

- **Python 3.10+** — Download from [python.org](https://www.python.org/downloads/)
  > ⚠️ During installation, make sure to check **"Add Python to PATH"**

### Step 1 — Clone the Repository

Open **Command Prompt** or **PowerShell** and run:

```bash
git clone https://github.com/SevanthRao/Tulunad_Homestay.git
cd Tulunad_Homestay
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3 — Activate the Virtual Environment

**Command Prompt:**
```bash
.venv\Scripts\activate
```

**PowerShell:**
```bash
.venv\Scripts\Activate.ps1
```

> If you get a PowerShell execution policy error, run this first:
> ```bash
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

You should see `(.venv)` at the beginning of your terminal prompt.

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Seed the Database

This creates an admin user and sample rooms:

```bash
python seed.py
```

### Step 6 — Run the Application

```bash
python app.py
```

The app will start at **http://127.0.0.1:5000** — open this URL in your browser.

---

## 🔑 Default Login Credentials

| Role  | Email              | Password   |
|-------|--------------------|------------|
| Admin | admin@tulunad.com  | admin123   |

> You can register a new account as a regular user from the registration page.

---

## 🧹 Deactivate Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

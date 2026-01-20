Project Structure


leave-management/
|
|-- backend/
|   |
|   |-- requirements.txt
|   |
|   `-- app/
|       |
|       |-- main.py
|       |-- database.py
|       |-- models.py
|       |-- schemas.py
|       |-- auth.py
|
|-- frontend/
|   |
|   |-- index.html
|   |-- register.html
|   |-- dashboard.html
|   |-- style.css
|   `-- script.js
|
|-- Tests/
|   |
|   |-- __init__.py
|   |-- conftest.py
|   |-- test_auth.py
|   |-- test_hr.py
|   |-- test_leave.py
|   `-- test_manager_team.py
|
`-- README.md



🚀 Features

User registration and login
Secure password hashing using bcrypt
Role-based access (Employee, Manager, HR)
Apply and view leave requests
Manager team leave viewing
HR dashboard for users and statistics
REST API built with FastAPI
SQLite database
Automated testing using Pytest

🛠 Technologies Used

Backend: FastAPI, SQLAlchemy
Database: SQLite
Authentication: Passlib (bcrypt)
Frontend: HTML, CSS, JavaScript
Testing: Pytest
Server: Uvicorn

**Setup Instructions**
1. Clone the repository

git clone <repository-url>

cd leave-management

2. Create virtual environment

python -m venv venv

Activate it:
Windows:

venv\Scripts\activate

Linux / macOS:

source venv/bin/activate

3. Install backend dependencies

cd backend

pip install -r requirements.txt

4. Run the backend server

uvicorn app.main:app

Server will start at:

http://127.0.0.1:8000

5. Run the frontend

Open in live server:

frontend/index.html 


🗄 Database

SQLite database is created automatically when the backend starts.

Database file should not be committed to version control.

If login problems occur after dependency changes:

Stop backend

Delete the database file

Restart backend

Register users again

🧪 Running Tests

From the project root directory:

pytest -v


or

python -m pytest

🔐 Authentication

Passwords are hashed using bcrypt

Plain-text passwords are never stored

Secure verification during login

👥 User Roles
Role	Permissions
Employee	Apply leave, view own leaves
Manager	Apply leave,View team leave requests
HR	View all users and leave statistics



👨‍💻 Author

Developed as a backend learning project using FastAPI.




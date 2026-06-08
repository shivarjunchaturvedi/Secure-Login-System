# Secure Login System

## Overview

Secure Login System is a web-based authentication application developed using Flask, SQLite, and bcrypt. The system provides secure user registration and login functionality with password hashing, session management, and protection against common security threats.

## Features

* User Registration
* Secure User Login
* Password Hashing using bcrypt
* SQL Injection Protection
* Session Management
* Logout Functionality
* Password Strength Validation
* Responsive User Interface
* Secure Authentication Workflow

## Technologies Used

* Python
* Flask
* SQLite
* bcrypt
* HTML
* CSS
* Bootstrap
* JavaScript

## Project Structure

```text
Secure-Login-System/
│
├── app.py
├── users.db
├── README.md
│
├── templates/
│   ├── register.html
│   ├── login.html
│   └── dashboard.html
│
└── screenshots/
```

## Installation

Install required libraries:

```bash
pip install flask bcrypt
```

## Running the Project

```bash
python app.py
```

Open the browser and visit:

```text
http://127.0.0.1:5000
```

## Security Features

* Passwords are stored using bcrypt hashing.
* Parameterized SQL queries help prevent SQL Injection.
* User sessions are managed securely.
* Logout functionality destroys active sessions.

## Learning Outcomes

* Web Application Security
* Authentication Systems
* Password Hashing
* Session Management
* Flask Development
* Database Integration

## Screenshots

* Register Page
* Login Page
* Dashboard Page
* Logout Page

## Author

Shivarjun Chaturvedi

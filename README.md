# COVID Vaccination Booking System

## Overview

This Flask-based web application manages COVID vaccination centers and user bookings. It provides functionalities for both users and admins to interact with vaccination centers, book slots, and manage center details.

## Features

- **User Authentication:**
  - Login, signup, and logout functionalities.
  - User-specific booking details display.
- **Admin Dashboard:**
  - Add, edit, and delete vaccination centers.
  - Manage center working hours and availability.
- **Booking Management:**
  - Book vaccination slots within center operational hours.
  - Validate and restrict bookings based on availability.
- **Database Management:**
  - SQLite database integration using SQLAlchemy.
  - Tables for users, vaccination centers, and booking details.

## Technologies Used

- Flask
- Flask-Login
- SQLAlchemy
- Bootstrap (for frontend UI)

## Setup

1. **Clone Repository:**

2. **Install Dependencies:**

3. **Database Configuration:**
- Set the SQLite database URI in `app.py`.
- Ensure database migrations and updates are managed using SQLAlchemy.

4. **Run Application:**

5. **Access Application:**
- Open `http://localhost:5000` in your web browser.
- Use provided admin credentials to access admin functionalities.

## Usage

- **User Perspective:**
- Log in to view available vaccination centers.
- Book slots within operational hours.
- View booked slots and manage account details.

- **Admin Perspective:**
- Access the admin dashboard to manage vaccination centers.
- Add new centers, edit existing details, or remove centers.
- Monitor and manage overall slot availability.

## Author
- **Abhimanyu Dave**
  - GitHub: [Abhimanyu Dave](https://github.com/AbhiD98)
  - LinkedIn: [Abhimanyu Dave](https://www.linkedin.com/in/abhimanyu-dave-9b1038175/)

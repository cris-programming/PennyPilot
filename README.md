[Leggi questo README in Italiano](README.it.md)

---

# PennyPilot - Personal Finance Manager

A comprehensive web application built with Python and Flask for personal finance management. This tool allows users to track income and expenses, manage monthly budgets, analyze spending habits over time, and much more.

## ✨ Key Features

- **Intuitive Dashboard:** Summary cards and charts for an immediate overview of your financial status.
- **Transaction Management:** Full CRUD (Create, Read, Update, Delete) for income and expenses.
- **Recurring Transactions:** Set up automatic transactions (salaries, subscriptions) with customizable frequencies.
- **Categorization & Budgeting:** Assign categories to expenses and set monthly budgets with visual progress bars and comparative insights (e.g., vs. last month).
- **Historical Analysis:** A dedicated analysis page with interactive charts to track net worth, cash flow, and spending by category over time.
- **Advanced Reporting:** Export annual and monthly data to both CSV and PDF formats.
- **Modern UI:** A clean, responsive interface featuring a collapsible icon-based sidebar.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Charts:** Chart.js
- **PDF Generation:** WeasyPrint
- **Icons:** Font Awesome

## 🚀 Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/cris-programming/PennyPilot.git](https://github.com/cris-programming/PennyPilot.git)
    cd PennyPilot
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database:**
    *Ensure you have a `.flaskenv` file in the root directory with the content `FLASK_APP=app`.*
    ```bash
    flask db upgrade
    ```

5.  **Run the application:**
    ```bash
    python run.py
    ```
The application will be available at `http://127.0.0.1:5000`.
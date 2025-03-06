# Expense Tracker

This is a simple expense tracker application built using Python, Streamlit, and SQLite. The application allows users to upload CSV files containing expense data, categorize expenses, and visualize the data using various charts and tables.

<video controls src="static/expense2.mp4" title="Title"></video>

## Features

- Upload multiple CSV files containing expense data
- Automatically categorize expenses based on predefined categories
- Save and load expense data from an SQLite database
- Edit expense categories
- Visualize expenses by category using pie charts
- Display total income, total expenses, and net balance

## Requirements

- pandas
- python-dateutil
- sqlite3
- streamlit
- plotly

## Installation

1. Clone the repository:

```bash
git clone https://github.com/username/expense_tracker.git
cd expense_tracker
```
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:

```bash
streamlit run expense_tracker.py
```
2. Upload your CSV files containing expense data. The CSV files should have the following columns: `Date`, `Description`, `Category`, and `Amount`.

3. The app will automatically categorize the expenses and save the data to an SQLite database.

4. Use the dashboard to visualize expenses by category, display total income, total expenses, and net balance.

## License
This project is licensed under the MIT License. See the LICENSE file for details.


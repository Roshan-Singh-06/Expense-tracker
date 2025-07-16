# Quick Installation Guide

## Getting Started

1. **Install Python** (if not already installed)
   - Download Python 3.7+ from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```
   python expense_tracker.py
   ```
   
   OR double-click `run_expense_tracker.bat`

4. **Optional: Add Demo Data**
   ```
   python demo_data.py
   ```

## First Time Setup

The application will automatically create an `expenses.json` file when you add your first expense. This file stores all your expense data.

## Troubleshooting

- **"tkinter not found"**: Install tkinter with `pip install tk`
- **"matplotlib not found"**: Run `pip install matplotlib`
- **Charts not showing**: Make sure matplotlib is properly installed

## Features to Try

1. **Add Expense Tab**: Add your daily expenses
2. **View Expenses Tab**: Browse and sort your expenses
3. **Analytics Tab**: View monthly spending charts

Enjoy tracking your expenses!

"""
Demo data generator for Expense Tracker
This script adds sample expense data to test the application
"""

import json
import os
from datetime import datetime, timedelta
import random

def generate_demo_data():
    """Generate sample expense data for the last 30 days"""
    
    # Categories and their typical expense ranges
    categories = {
        "Food": (50, 500),
        "Transportation": (20, 200),
        "Entertainment": (100, 800),
        "Shopping": (200, 2000),
        "Bills": (500, 3000),
        "Healthcare": (100, 1500),
        "Education": (200, 1000),
        "Other": (50, 300)
    }
    
    # Sample descriptions for each category
    descriptions = {
        "Food": ["Lunch at restaurant", "Grocery shopping", "Coffee", "Dinner with friends", "Street food", "Pizza delivery"],
        "Transportation": ["Bus fare", "Taxi ride", "Metro card recharge", "Fuel", "Parking fee", "Auto rickshaw"],
        "Entertainment": ["Movie tickets", "Concert", "Gaming", "Streaming subscription", "Sports event", "Museum visit"],
        "Shopping": ["Clothes", "Electronics", "Books", "Home decor", "Gadgets", "Shoes"],
        "Bills": ["Electricity bill", "Internet bill", "Phone bill", "Rent", "Water bill", "Gas bill"],
        "Healthcare": ["Medicine", "Doctor visit", "Health checkup", "Dental care", "Eye test", "Physiotherapy"],
        "Education": ["Course fee", "Books", "Online subscription", "Tuition", "Workshop", "Certification"],
        "Other": ["Gift", "Donation", "Miscellaneous", "Travel", "Emergency", "Repair"]
    }
    
    expenses = []
    
    # Generate expenses for the last 30 days
    for days_ago in range(30):
        date = datetime.now() - timedelta(days=days_ago)
        date_str = date.strftime("%Y-%m-%d")
        
        # Random number of expenses per day (0-4)
        num_expenses = random.randint(0, 4)
        
        for _ in range(num_expenses):
            category = random.choice(list(categories.keys()))
            min_amount, max_amount = categories[category]
            amount = round(random.uniform(min_amount, max_amount), 2)
            description = random.choice(descriptions[category])
            
            expense = {
                "date": date_str,
                "amount": amount,
                "category": category,
                "description": description,
                "timestamp": (date + timedelta(seconds=random.randint(0, 86400))).isoformat()
            }
            
            expenses.append(expense)
    
    return expenses

def save_demo_data():
    """Save demo data to expenses.json"""
    data_file = "expenses.json"
    
    # Load existing data if any
    existing_expenses = []
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                existing_expenses = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_expenses = []
    
    # Generate new demo data
    demo_expenses = generate_demo_data()
    
    # Combine with existing data
    all_expenses = existing_expenses + demo_expenses
    
    # Save to file
    with open(data_file, 'w') as f:
        json.dump(all_expenses, f, indent=2)
    
    print(f"Generated {len(demo_expenses)} demo expenses!")
    print(f"Total expenses in database: {len(all_expenses)}")
    print("Demo data saved to expenses.json")
    print("\nSample expenses:")
    for expense in demo_expenses[:5]:
        print(f"  {expense['date']}: ₹{expense['amount']} - {expense['category']} - {expense['description']}")

if __name__ == "__main__":
    save_demo_data()

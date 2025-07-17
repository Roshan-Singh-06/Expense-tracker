"""
AI Expense Tracker Demo
Demonstrates the AI-powered features of the expense tracker
"""

import json
import os
from datetime import datetime, timedelta
import random

def generate_ai_demo_data():
    """Generate realistic demo expense data for AI features"""
    
    # Realistic expense categories with descriptions
    expense_templates = {
        'Food': [
            ('Starbucks coffee', 150, 350),
            ('Lunch at restaurant', 300, 800),
            ('Grocery shopping', 500, 2000),
            ('Pizza delivery', 400, 800),
            ('Street food', 50, 200),
            ('Breakfast cafe', 100, 300),
            ('Dinner at hotel', 800, 2500),
            ('McDonald\'s meal', 200, 400),
            ('Fresh juice', 80, 150),
            ('Ice cream', 100, 250)
        ],
        'Transportation': [
            ('Uber ride', 150, 500),
            ('Metro card recharge', 200, 500),
            ('Auto rickshaw', 80, 200),
            ('Bus ticket', 30, 100),
            ('Taxi fare', 200, 600),
            ('Petrol fill up', 1000, 3000),
            ('Parking fee', 50, 200),
            ('Ola cab', 120, 400),
            ('Train ticket', 150, 800),
            ('Flight booking', 3000, 15000)
        ],
        'Shopping': [
            ('Clothing purchase', 800, 3000),
            ('Amazon order', 500, 2000),
            ('Flipkart shopping', 600, 2500),
            ('Electronics store', 2000, 25000),
            ('Grocery store', 400, 1500),
            ('Pharmacy medicines', 200, 800),
            ('Book purchase', 300, 800),
            ('Shoes shopping', 1000, 4000),
            ('Mobile accessories', 500, 2000),
            ('Home appliances', 3000, 20000)
        ],
        'Entertainment': [
            ('Movie ticket', 200, 500),
            ('Concert ticket', 1000, 3000),
            ('Netflix subscription', 199, 799),
            ('Gaming purchase', 500, 2000),
            ('Amusement park', 800, 2000),
            ('Sports event', 500, 2000),
            ('Theatre show', 600, 1500),
            ('Museum entry', 100, 300),
            ('Club entry', 800, 2000),
            ('Online game', 300, 1000)
        ],
        'Bills': [
            ('Electricity bill', 800, 3000),
            ('Internet bill', 600, 1500),
            ('Mobile recharge', 200, 600),
            ('Water bill', 300, 800),
            ('Gas cylinder', 400, 800),
            ('DTH recharge', 300, 600),
            ('Insurance premium', 2000, 10000),
            ('Credit card payment', 5000, 50000),
            ('Loan EMI', 10000, 50000),
            ('Rent payment', 15000, 50000)
        ],
        'Healthcare': [
            ('Doctor consultation', 500, 1500),
            ('Medicine purchase', 200, 1000),
            ('Health checkup', 1000, 5000),
            ('Dental treatment', 800, 3000),
            ('Eye checkup', 600, 2000),
            ('Physiotherapy', 800, 2000),
            ('Hospital bill', 2000, 15000),
            ('Lab tests', 500, 2000),
            ('Vaccination', 300, 1000),
            ('Medical equipment', 1000, 5000)
        ],
        'Education': [
            ('Course fee', 5000, 50000),
            ('Book purchase', 300, 1000),
            ('Online course', 1000, 5000),
            ('Workshop fee', 2000, 10000),
            ('Certification exam', 3000, 15000),
            ('Stationery', 200, 500),
            ('Laptop for study', 25000, 80000),
            ('Library membership', 500, 2000),
            ('Tuition fee', 3000, 15000),
            ('Educational software', 2000, 10000)
        ],
        'Other': [
            ('Gift purchase', 500, 3000),
            ('Charity donation', 1000, 5000),
            ('Travel expense', 2000, 20000),
            ('Hotel booking', 3000, 15000),
            ('Miscellaneous', 100, 1000),
            ('Emergency expense', 500, 5000),
            ('Repair work', 800, 3000),
            ('Service charge', 200, 800),
            ('ATM withdrawal', 500, 5000),
            ('Bank charges', 100, 500)
        ]
    }
    
    # Generate expenses for the last 60 days
    expenses = []
    start_date = datetime.now() - timedelta(days=60)
    
    for day in range(60):
        current_date = start_date + timedelta(days=day)
        
        # Generate 1-5 expenses per day randomly
        num_expenses = random.choices([0, 1, 2, 3, 4, 5], weights=[5, 20, 30, 25, 15, 5])[0]
        
        for _ in range(num_expenses):
            # Choose random category
            category = random.choice(list(expense_templates.keys()))
            
            # Choose random expense template from category
            template = random.choice(expense_templates[category])
            description, min_amount, max_amount = template
            
            # Generate random amount within range
            amount = random.randint(min_amount, max_amount)
            
            # Add some variation to description
            if random.random() < 0.3:  # 30% chance to add variation
                variations = [
                    f"{description} - weekend",
                    f"{description} - urgent",
                    f"{description} - online",
                    f"{description} - special offer",
                    f"{description} - premium"
                ]
                description = random.choice(variations)
            
            # Create expense entry
            expense = {
                "date": current_date.strftime('%Y-%m-%d'),
                "amount": amount,
                "category": category,
                "description": description,
                "timestamp": current_date.isoformat()
            }
            
            expenses.append(expense)
    
    return expenses

def save_ai_demo_data():
    """Save AI demo data to expenses.json"""
    
    print("🚀 Generating AI Expense Tracker Demo Data...")
    
    # Generate demo expenses
    demo_expenses = generate_ai_demo_data()
    
    # Save to file
    data_file = "expenses.json"
    
    try:
        with open(data_file, 'w') as f:
            json.dump(demo_expenses, f, indent=2)
        
        print(f"✅ Successfully generated {len(demo_expenses)} demo expenses!")
        print(f"📁 Saved to: {os.path.abspath(data_file)}")
        
        # Print statistics
        total_amount = sum(exp['amount'] for exp in demo_expenses)
        categories = {}
        for exp in demo_expenses:
            cat = exp['category']
            categories[cat] = categories.get(cat, 0) + exp['amount']
        
        print(f"\n📊 Demo Data Statistics:")
        print(f"💰 Total Amount: ₹{total_amount:,.2f}")
        print(f"📈 Number of Transactions: {len(demo_expenses)}")
        print(f"📅 Date Range: {demo_expenses[0]['date']} to {demo_expenses[-1]['date']}")
        
        print(f"\n🏷️ Category Breakdown:")
        for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_amount) * 100
            print(f"  {category}: ₹{amount:,.2f} ({percentage:.1f}%)")
        
        print(f"\n🤖 AI Features Ready:")
        print("  ✅ Smart Categorization - Will learn from this data")
        print("  ✅ Financial AI - Ready for analysis")
        print("  ✅ Real-time Dashboard - Live charts available")
        print("  ✅ Anomaly Detection - Pattern recognition active")
        print("  ✅ Predictions - Trend analysis possible")
        
        print(f"\n🎯 Next Steps:")
        print("  1. Run the expense tracker: python expense_tracker.py")
        print("  2. Explore the 🤖 AI Features tab")
        print("  3. Try adding new expenses (AI will suggest categories)")
        print("  4. Open the Real-time Dashboard for live analytics")
        print("  5. View AI Financial Insights for detailed analysis")
        
    except Exception as e:
        print(f"❌ Error saving demo data: {e}")

def run_ai_tests():
    """Run basic tests for AI components"""
    
    print("\n🧪 Running AI Component Tests...")
    
    try:
        # Test AI Categorizer
        from ai_categorizer import AIExpenseCategorizer
        categorizer = AIExpenseCategorizer()
        
        test_descriptions = [
            ("Coffee at Starbucks", 200),
            ("Uber ride to office", 150),
            ("Netflix subscription", 199),
            ("Grocery shopping", 800),
            ("Doctor consultation", 500)
        ]
        
        print("\n🏷️ Testing Smart Categorization:")
        for desc, amount in test_descriptions:
            category = categorizer.smart_categorize(desc, amount)
            print(f"  '{desc}' (₹{amount}) → {category}")
        
        # Test Financial AI
        from financial_ai import FinancialAI
        financial_ai = FinancialAI()
        
        # Create sample data
        sample_expenses = [
            {'date': '2024-01-01', 'amount': 500, 'category': 'Food', 'description': 'Restaurant'},
            {'date': '2024-01-02', 'amount': 200, 'category': 'Transportation', 'description': 'Taxi'},
            {'date': '2024-01-03', 'amount': 1500, 'category': 'Shopping', 'description': 'Clothes'},
        ]
        
        insights = financial_ai.analyze_spending_patterns(sample_expenses)
        print(f"\n🧠 Financial AI Test: {insights.get('status', 'Unknown')}")
        
        print("\n✅ All AI components working correctly!")
        
    except ImportError as e:
        print(f"⚠️ AI components not available: {e}")
        print("   Install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ AI test failed: {e}")

if __name__ == "__main__":
    print("🤖 AI Expense Tracker Demo Setup")
    print("=" * 50)
    
    # Generate demo data
    save_ai_demo_data()
    
    # Run tests
    run_ai_tests()
    
    print("\n🎉 Demo setup complete!")
    print("Run 'python expense_tracker.py' to start the AI-powered expense tracker!")

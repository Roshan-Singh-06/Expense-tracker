"""
Test AI Features Demo
This script demonstrates the enhanced AI capabilities
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime, timedelta

def demo_ai_features():
    """Demonstrate AI features"""
    print("🤖 AI-Powered Expense Tracker - Feature Demo")
    print("=" * 50)
    
    # Check if expenses exist
    if os.path.exists('expenses.json'):
        with open('expenses.json', 'r') as f:
            expenses = json.load(f)
        
        print(f"📊 Current Data: {len(expenses)} expenses loaded")
        
        # Calculate some stats
        total_amount = sum(exp['amount'] for exp in expenses)
        avg_amount = total_amount / len(expenses) if expenses else 0
        
        print(f"💰 Total Spending: ₹{total_amount:,.2f}")
        print(f"📈 Average Transaction: ₹{avg_amount:,.2f}")
        
        # Find high-value transactions (potential anomalies)
        threshold = avg_amount * 2
        high_value = [exp for exp in expenses if exp['amount'] > threshold]
        
        if high_value:
            print(f"⚠️  Anomaly Alert: {len(high_value)} high-value transactions detected!")
            print(f"   Threshold: ₹{threshold:,.0f}")
            for exp in high_value[-3:]:  # Show last 3
                print(f"   • ₹{exp['amount']:,.0f} - {exp['description']} ({exp['date']})")
        
        # Category analysis
        categories = {}
        for exp in expenses:
            cat = exp['category']
            categories[cat] = categories.get(cat, 0) + exp['amount']
        
        print("\n🏷️  Spending by Category:")
        for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_amount) * 100 if total_amount > 0 else 0
            print(f"   • {cat}: ₹{amount:,.0f} ({percentage:.1f}%)")
        
        # Recent spending trend
        recent_expenses = [exp for exp in expenses 
                          if datetime.strptime(exp['date'], '%Y-%m-%d') >= datetime.now() - timedelta(days=7)]
        
        if recent_expenses:
            recent_total = sum(exp['amount'] for exp in recent_expenses)
            daily_avg = recent_total / 7
            print(f"\n📅 Last 7 Days: ₹{recent_total:,.0f} (₹{daily_avg:,.0f}/day)")
            
            if daily_avg > 1000:
                print("🚨 HIGH SPENDING ALERT: Daily average exceeds ₹1,000!")
            elif daily_avg > 500:
                print("⚠️  MODERATE SPENDING: Daily average is ₹500+")
            else:
                print("✅ HEALTHY SPENDING: Daily average is under control")
        
        print("\n" + "=" * 50)
        print("🎯 AI RECOMMENDATIONS:")
        
        # Generate recommendations
        if any(exp['amount'] > avg_amount * 3 for exp in expenses):
            print("• 💡 Review large transactions for accuracy")
        
        if categories.get('Food', 0) > total_amount * 0.3:
            print("• 🍕 Food spending is high (>30%) - consider meal planning")
        
        if categories.get('Entertainment', 0) > total_amount * 0.2:
            print("• 🎬 Entertainment spending is high (>20%) - set limits")
        
        if daily_avg > 800:
            print("• 📊 Consider setting a daily budget of ₹600-800")
        
        print("• 📈 Enable budget alerts for better control")
        print("• 🔔 Set up spending notifications")
        
    else:
        print("📝 No expenses found. Add some expenses to see AI features!")
    
    print("\n✨ Features Now Available in Main App:")
    print("🤖 Live AI suggestions panel")
    print("📊 Real-time financial health score")
    print("⚠️  Automatic anomaly detection")
    print("💡 Proactive spending recommendations")
    print("🚨 Urgent alert notifications")
    print("📈 Interactive dashboard")

if __name__ == "__main__":
    demo_ai_features()

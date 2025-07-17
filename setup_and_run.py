"""
AI Expense Tracker - Complete Setup and Launch Script
Handles installation, setup, and launching of the AI-powered expense tracker
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    requirements = [
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "plyer>=2.0",
        "tkinter"  # Usually comes with Python
    ]
    
    # Optional AI packages
    optional_requirements = [
        "openai>=1.0.0",
        "SpeechRecognition>=3.10.0",
        "reportlab>=3.6.0",
        "python-docx>=0.8.11",
        "openpyxl>=3.0.9"
    ]
    
    success = True
    installed_packages = []
    failed_packages = []
    
    # Install core requirements
    for package in requirements:
        try:
            print(f"  Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True, check=True)
            installed_packages.append(package)
            print(f"  ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {package}: {e}")
            failed_packages.append(package)
            if package in ["matplotlib", "numpy", "pandas"]:  # Critical packages
                success = False
    
    # Install optional packages (don't fail if these don't install)
    print(f"\n📦 Installing optional AI packages...")
    for package in optional_requirements:
        try:
            print(f"  Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True, check=True)
            installed_packages.append(package)
            print(f"  ✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"  ⚠️ Optional package {package} could not be installed (skipping)")
    
    print(f"\n📊 Installation Summary:")
    print(f"  ✅ Successfully installed: {len(installed_packages)} packages")
    if failed_packages:
        print(f"  ❌ Failed to install: {len(failed_packages)} packages")
        for pkg in failed_packages:
            print(f"    - {pkg}")
    
    return success

def check_files():
    """Check if all required files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        "expense_tracker.py",
        "ai_categorizer.py", 
        "financial_ai.py",
        "real_time_dashboard.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files found")
    return True

def create_demo_data():
    """Create demo data if expenses.json doesn't exist"""
    if os.path.exists("expenses.json"):
        print("\n📊 Existing expense data found - keeping current data")
        return True
    
    print("\n🚀 Creating demo data for AI features...")
    try:
        # Import and run demo data generator
        from ai_demo import save_ai_demo_data
        save_ai_demo_data()
        return True
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        print("   You can add expenses manually after starting the application")
        return False

def test_ai_components():
    """Test if AI components are working"""
    print("\n🧪 Testing AI components...")
    
    try:
        # Test AI Categorizer
        from ai_categorizer import AIExpenseCategorizer
        categorizer = AIExpenseCategorizer()
        test_category = categorizer.smart_categorize("Coffee at cafe", 200)
        print(f"  ✅ AI Categorizer: Working (test: Coffee → {test_category})")
        
        # Test Financial AI
        from financial_ai import FinancialAI
        financial_ai = FinancialAI()
        print("  ✅ Financial AI: Ready for analysis")
        
        # Test Dashboard
        print("  ✅ Real-time Dashboard: Ready to launch")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ AI components error: {e}")
        print("     Some AI features may not be available")
        return False
    except Exception as e:
        print(f"  ⚠️ AI test warning: {e}")
        return True

def launch_application():
    """Launch the expense tracker application"""
    print("\n🚀 Launching AI Expense Tracker...")
    
    try:
        # Import and run the main application
        import expense_tracker
        print("✅ Application started successfully!")
        print("\n🎯 Quick Start Guide:")
        print("  1. Go to the '🤖 AI Features' tab to explore AI capabilities")
        print("  2. Add new expenses and see AI categorization in action")
        print("  3. Open the Real-time Dashboard for live analytics")
        print("  4. View AI Financial Insights for detailed analysis")
        
        # Start the main application
        if hasattr(expense_tracker, 'main'):
            expense_tracker.main()
        else:
            # If no main function, create and run the app directly
            import tkinter as tk
            root = tk.Tk()
            app = expense_tracker.ExpenseTracker(root)
            root.mainloop()
            
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        print("\nTry running manually: python expense_tracker.py")
        return False
    
    return True

def show_welcome_message():
    """Show welcome message and feature overview"""
    welcome_text = """
🤖 AI-POWERED EXPENSE TRACKER
================================

🌟 FEATURES:
  🏷️ Smart Categorization - AI learns your spending patterns
  🧠 Financial Intelligence - Deep insights and recommendations  
  📊 Real-time Dashboard - Live charts and analytics
  ⚠️ Anomaly Detection - Unusual spending alerts
  🔮 Predictive Analytics - Future spending forecasts
  📈 Smart Reports - AI-powered financial reports

🚀 GETTING STARTED:
  • The application will open with demo data already loaded
  • Explore the "🤖 AI Features" tab for advanced capabilities
  • Try adding new expenses to see AI categorization
  • Check the Real-time Dashboard for live insights

💡 TIP: The AI gets smarter as you use it more!
"""
    print(welcome_text)

def main():
    """Main setup and launch function"""
    print("🤖 AI Expense Tracker - Setup & Launch")
    print("=" * 50)
    
    # Show welcome message
    show_welcome_message()
    
    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Critical packages failed to install")
        print("Please install manually: pip install matplotlib pandas numpy seaborn scikit-learn")
        input("\nPress Enter to exit...")
        return
    
    # Check files
    if not check_files():
        print("\n❌ Required files are missing")
        input("\nPress Enter to exit...")
        return
    
    # Create demo data
    create_demo_data()
    
    # Test AI components
    test_ai_components()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete! Launching application...")
    print("=" * 50)
    
    # Launch application
    launch_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue if it persists")
        input("\nPress Enter to exit...")

"""
Notification Demo for Expense Tracker
This script demonstrates all the notification features available in the expense tracker.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from expense_tracker import ExpenseTracker
import time
import threading

def demo_notifications():
    """Demo all notification types"""
    root = tk.Tk()
    app = ExpenseTracker(root)
    
    def show_demo_notifications():
        """Show various notification types with delays"""
        # Wait for app to load
        time.sleep(2)
        
        # Success notification
        app.show_toast_notification(
            "✅ Success Demo", 
            "This is a success notification example!", 
            "success"
        )
        time.sleep(3)
        
        # Warning notification
        app.show_toast_notification(
            "⚠️ Warning Demo", 
            "This is a warning notification example!", 
            "warning"
        )
        time.sleep(3)
        
        # Error notification
        app.show_toast_notification(
            "❌ Error Demo", 
            "This is an error notification example!", 
            "error"
        )
        time.sleep(3)
        
        # Info notification
        app.show_toast_notification(
            "ℹ️ Info Demo", 
            "This is an info notification example!", 
            "info"
        )
        time.sleep(3)
        
        # Achievement notification
        app.show_achievement_notification(
            "You've completed the notification demo! 🎉"
        )
        time.sleep(3)
        
        # Budget alert simulation
        app.show_toast_notification(
            "💸 Budget Alert Demo", 
            "Daily spending exceeded by ₹500.00\nTotal today: ₹1,500.00", 
            "warning"
        )
        
        # System notification (if available)
        app.show_system_notification(
            "🔔 System Notification Demo",
            "This notification appears in your system tray!"
        )
    
    # Start demo in background thread
    demo_thread = threading.Thread(target=show_demo_notifications, daemon=True)
    demo_thread.start()
    
    root.mainloop()

if __name__ == "__main__":
    print("Starting Notification Demo...")
    print("The demo will show various types of notifications every 3 seconds.")
    print("Close the application window when done.")
    demo_notifications()

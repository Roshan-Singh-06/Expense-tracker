"""
Real-time Dashboard Module
Provides live analytics and interactive visualizations
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import json

# Set the style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class RealTimeDashboard:
    def __init__(self, parent, expense_data_callback):
        """
        Initialize the real-time dashboard
        
        Args:
            parent: Parent tkinter widget
            expense_data_callback: Function that returns current expense data
        """
        self.parent = parent
        self.get_expense_data = expense_data_callback
        self.dashboard_window = None
        self.is_running = False
        self.update_thread = None
        self.auto_refresh = True
        self.refresh_interval = 30  # seconds
        
        # Chart containers
        self.charts = {}
        self.figure = None
        self.canvas = None
        
        # Style configuration
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#F18F01',
            'warning': '#C73E1D',
            'info': '#7209B7',
            'background': '#F8F9FA',
            'card_bg': '#FFFFFF'
        }
        
    def open_dashboard(self):
        """Open the real-time dashboard window"""
        if self.dashboard_window and self.dashboard_window.winfo_exists():
            self.dashboard_window.lift()
            self.dashboard_window.focus()
            return
        
        self.dashboard_window = tk.Toplevel(self.parent)
        self.dashboard_window.title("📊 Real-time Financial Dashboard")
        self.dashboard_window.geometry("1400x900")
        self.dashboard_window.configure(bg=self.colors['background'])
        
        # Configure window closing behavior
        self.dashboard_window.protocol("WM_DELETE_WINDOW", self.close_dashboard)
        
        self.setup_dashboard_ui()
        self.start_real_time_updates()
        
    def setup_dashboard_ui(self):
        """Setup the dashboard user interface"""
        # Create main container
        main_frame = tk.Frame(self.dashboard_window, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header section
        self.create_header(main_frame)
        
        # Create notebook for different dashboard views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create different dashboard tabs
        self.create_overview_tab()
        self.create_analytics_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create the dashboard header with controls"""
        header_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief='raised', bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="📊 Real-time Financial Dashboard",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Controls frame
        controls_frame = tk.Frame(header_frame, bg=self.colors['card_bg'])
        controls_frame.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=self.auto_refresh)
        auto_refresh_check = tk.Checkbutton(
            controls_frame,
            text="Auto Refresh",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh,
            bg=self.colors['card_bg'],
            font=('Segoe UI', 10)
        )
        auto_refresh_check.pack(side=tk.LEFT, padx=5)
        
        # Refresh interval
        tk.Label(controls_frame, text="Interval:", bg=self.colors['card_bg'], font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.StringVar(value=str(self.refresh_interval))
        interval_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.interval_var,
            values=["10", "30", "60", "120"],
            width=8,
            state="readonly"
        )
        interval_combo.pack(side=tk.LEFT, padx=5)
        interval_combo.bind('<<ComboboxSelected>>', self.update_refresh_interval)
        
        # Manual refresh button
        refresh_btn = tk.Button(
            controls_frame,
            text="🔄 Refresh",
            command=self.manual_refresh,
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            padx=15
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Last update time
        self.last_update_label = tk.Label(
            controls_frame,
            text="Last update: Never",
            bg=self.colors['card_bg'],
            fg='gray',
            font=('Segoe UI', 9)
        )
        self.last_update_label.pack(side=tk.LEFT, padx=10)
        
    def create_overview_tab(self):
        """Create the overview dashboard tab"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="📈 Overview")
        
        # Create matplotlib figure for overview
        self.overview_figure = plt.Figure(figsize=(14, 8), facecolor=self.colors['background'])
        self.overview_canvas = FigureCanvasTkAgg(self.overview_figure, overview_frame)
        self.overview_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_analytics_tab(self):
        """Create the analytics dashboard tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Create matplotlib figure for analytics
        self.analytics_figure = plt.Figure(figsize=(14, 8), facecolor=self.colors['background'])
        self.analytics_canvas = FigureCanvasTkAgg(self.analytics_figure, analytics_frame)
        self.analytics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = tk.Frame(parent, bg=self.colors['primary'], height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Connection indicator
        self.connection_indicator = tk.Label(
            status_frame,
            text="🟢 Live",
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 9)
        )
        self.connection_indicator.pack(side=tk.RIGHT, padx=10)
        
    def update_overview_charts(self, data):
        """Update the overview charts"""
        if not data or not self.overview_figure:
            return
            
        try:
            self.overview_figure.clear()
            
            df = pd.DataFrame(data)
            if df.empty:
                return
                
            # Convert and clean data
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df[df['amount'] > 0]
            
            if df.empty:
                return
                
            # Create subplots
            gs = self.overview_figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # 1. Daily spending trend
            ax1 = self.overview_figure.add_subplot(gs[0, :])
            daily_spending = df.groupby(df['date'].dt.date)['amount'].sum()
            ax1.plot(daily_spending.index, daily_spending.values, marker='o', linewidth=2, markersize=4)
            ax1.set_title('Daily Spending Trend', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Amount (₹)')
            ax1.grid(True, alpha=0.3)
            
            # Format x-axis
            if len(daily_spending) > 10:
                ax1.tick_params(axis='x', rotation=45)
            
            # 2. Category distribution
            ax2 = self.overview_figure.add_subplot(gs[1, 0])
            category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
            
            if len(category_totals) > 0:
                # Limit to top 6 categories
                top_categories = category_totals.head(6)
                colors = sns.color_palette("husl", len(top_categories))
                
                wedges, texts, autotexts = ax2.pie(
                    top_categories.values,
                    labels=top_categories.index,
                    autopct='%1.1f%%',
                    colors=colors,
                    startangle=90
                )
                
                # Improve text readability
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    
            ax2.set_title('Category Distribution', fontsize=12, fontweight='bold')
            
            # 3. Weekly pattern
            ax3 = self.overview_figure.add_subplot(gs[1, 1])
            df['day_name'] = df['date'].dt.day_name()
            
            # Order days properly
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekly_avg = df.groupby('day_name')['amount'].mean().reindex(day_order, fill_value=0)
            
            bars = ax3.bar(range(len(weekly_avg)), weekly_avg.values, color=sns.color_palette("viridis", len(weekly_avg)))
            ax3.set_title('Average Spending by Day', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Average Amount (₹)')
            ax3.set_xticks(range(len(weekly_avg)))
            ax3.set_xticklabels([day[:3] for day in weekly_avg.index], rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                           f'₹{height:.0f}',
                           ha='center', va='bottom', fontsize=9)
            
            self.overview_canvas.draw()
            
        except Exception as e:
            print(f"Error updating overview charts: {e}")
            
    def update_analytics_charts(self, data):
        """Update the analytics charts"""
        if not data or not self.analytics_figure:
            return
            
        try:
            self.analytics_figure.clear()
            
            df = pd.DataFrame(data)
            if df.empty:
                return
                
            # Convert and clean data
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df[df['amount'] > 0]
            
            if df.empty:
                return
                
            # Create advanced analytics charts
            gs = self.analytics_figure.add_gridspec(2, 2, hspace=0.35, wspace=0.25)
            
            # 1. Monthly trend with moving average
            ax1 = self.analytics_figure.add_subplot(gs[0, :])
            daily_spending = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
            daily_spending['moving_avg'] = daily_spending['amount'].rolling(window=7, min_periods=1).mean()
            
            ax1.plot(daily_spending['date'], daily_spending['amount'], alpha=0.7, label='Daily Spending', linewidth=1)
            ax1.plot(daily_spending['date'], daily_spending['moving_avg'], color='red', linewidth=2, label='7-day Moving Average')
            ax1.set_title('Spending Trend with Moving Average', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Amount (₹)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. Category spending over time
            ax2 = self.analytics_figure.add_subplot(gs[1, 0])
            
            # Get top 5 categories
            top_categories = df.groupby('category')['amount'].sum().nlargest(5).index
            
            for category in top_categories:
                cat_data = df[df['category'] == category]
                daily_cat = cat_data.groupby(cat_data['date'].dt.date)['amount'].sum()
                
                if len(daily_cat) > 1:
                    ax2.plot(daily_cat.index, daily_cat.values, marker='o', label=category, linewidth=2, markersize=3)
            
            ax2.set_title('Top Category Trends', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Daily Amount (₹)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 3. Transaction amount distribution
            ax3 = self.analytics_figure.add_subplot(gs[1, 1])
            
            # Create histogram of transaction amounts
            amounts = df['amount'].values
            ax3.hist(amounts, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax3.axvline(amounts.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ₹{amounts.mean():.0f}')
            ax3.axvline(np.median(amounts), color='green', linestyle='--', linewidth=2, label=f'Median: ₹{np.median(amounts):.0f}')
            
            ax3.set_title('Transaction Amount Distribution', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Amount (₹)')
            ax3.set_ylabel('Frequency')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            self.analytics_canvas.draw()
            
        except Exception as e:
            print(f"Error updating analytics charts: {e}")
    
    def start_real_time_updates(self):
        """Start the real-time update thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Initial update
        self.manual_refresh()
    
    def _update_loop(self):
        """Background update loop"""
        while self.is_running:
            try:
                if self.auto_refresh:
                    self.dashboard_window.after(0, self.refresh_dashboard)
                
                time.sleep(self.refresh_interval)
                
            except Exception as e:
                print(f"Update loop error: {e}")
                break
    
    def refresh_dashboard(self):
        """Refresh all dashboard components"""
        if not self.dashboard_window or not self.dashboard_window.winfo_exists():
            self.stop_real_time_updates()
            return
            
        try:
            # Update status
            self.status_label.config(text="Refreshing...")
            self.connection_indicator.config(text="🔄 Updating")
            
            # Get latest data
            data = self.get_expense_data()
            
            # Update all components
            self.update_overview_charts(data)
            self.update_analytics_charts(data)
            
            # Update status
            current_time = datetime.now().strftime('%H:%M:%S')
            self.last_update_label.config(text=f"Last update: {current_time}")
            self.status_label.config(text="Ready")
            self.connection_indicator.config(text="🟢 Live")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.connection_indicator.config(text="🔴 Error")
    
    def manual_refresh(self):
        """Manual refresh triggered by user"""
        self.refresh_dashboard()
    
    def toggle_auto_refresh(self):
        """Toggle auto refresh on/off"""
        self.auto_refresh = self.auto_refresh_var.get()
        
        if self.auto_refresh:
            self.connection_indicator.config(text="🟢 Live")
        else:
            self.connection_indicator.config(text="⏸️ Paused")
    
    def update_refresh_interval(self, event=None):
        """Update the refresh interval"""
        try:
            self.refresh_interval = int(self.interval_var.get())
        except ValueError:
            self.refresh_interval = 30
    
    def stop_real_time_updates(self):
        """Stop the real-time updates"""
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
    
    def close_dashboard(self):
        """Close the dashboard window"""
        self.stop_real_time_updates()
        if self.dashboard_window:
            self.dashboard_window.destroy()
            self.dashboard_window = None

# Test function
def test_dashboard():
    """Test the real-time dashboard"""
    import random
    from datetime import datetime, timedelta
    
    # Sample data generator
    def generate_sample_data():
        categories = ['Food', 'Transportation', 'Shopping', 'Entertainment', 'Healthcare']
        data = []
        
        start_date = datetime.now() - timedelta(days=30)
        for i in range(50):
            date = start_date + timedelta(days=random.randint(0, 30))
            amount = random.randint(100, 2000)
            category = random.choice(categories)
            description = f"Sample expense {i+1}"
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': amount,
                'category': category,
                'description': description
            })
        
        return data
    
    # Create test window
    root = tk.Tk()
    root.title("Dashboard Test")
    root.geometry("300x200")
    
    # Create dashboard
    dashboard = RealTimeDashboard(root, generate_sample_data)
    
    # Add test button
    test_btn = tk.Button(
        root,
        text="Open Dashboard",
        command=dashboard.open_dashboard,
        font=('Segoe UI', 12),
        bg='#2E86AB',
        fg='white',
        padx=20,
        pady=10
    )
    test_btn.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    test_dashboard()

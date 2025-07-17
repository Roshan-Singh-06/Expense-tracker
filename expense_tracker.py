import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
import json
import os
import csv
import threading
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import seaborn as sns

# Try to import system notification libraries
try:
    import plyer
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

# Import AI modules
try:
    from ai_categorizer import AIExpenseCategorizer
    from financial_ai import FinancialAI
    from real_time_dashboard import RealTimeDashboard
    AI_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"AI features not available: {e}")
    AI_FEATURES_AVAILABLE = False

# Set modern styling for matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Professional Expense Tracker")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8f9fa')
        self.root.minsize(1000, 600)
        
        # Modern color scheme
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'white': '#ffffff',
            'accent': '#9b59b6',
            'gradient_start': '#667eea',
            'gradient_end': '#764ba2'
        }
        
        # Configure modern ttk style
        self.configure_styles()
        
        # Data file path
        self.data_file = os.path.join(os.path.dirname(__file__), "expenses.json")
        
        # Initialize data
        self.expenses = self.load_data()
        
        # Initialize AI components
        self.ai_categorizer = None
        self.financial_ai = None
        self.dashboard = None
        
        if AI_FEATURES_AVAILABLE:
            self.ai_categorizer = AIExpenseCategorizer()
            self.financial_ai = FinancialAI()
            self.dashboard = RealTimeDashboard(self.root, self.get_expense_data)
        
        # Notification settings
        self.notifications_enabled = True
        self.daily_budget = 1000  # Default daily budget
        self.notification_history = []
        
        # Load notification settings
        self.load_notification_settings()
        
        # Start notification service
        self.start_notification_service()
        
        # Create main interface
        self.create_widgets()
        self.refresh_transactions()
        self.update_graph()
        
        # Show welcome notification
        self.show_toast_notification("Welcome! 🎉", "Expense Tracker is ready to help you manage your finances!", "success")
        
    def configure_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure('Modern.TNotebook', background=self.colors['light'])
        style.configure('Modern.TNotebook.Tab', 
                       padding=[20, 10], 
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       font=('Segoe UI', 11, 'bold'))
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['secondary']),
                            ('active', self.colors['info'])],
                 foreground=[('selected', self.colors['white']),
                            ('active', self.colors['white'])])
        
        # Configure frame styles
        style.configure('Card.TFrame', 
                       background=self.colors['white'],
                       relief='solid',
                       borderwidth=1)
        
        # Configure combobox styles
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['white'],
                       background=self.colors['secondary'],
                       foreground=self.colors['dark'],
                       borderwidth=1,
                       relief='solid')
        
        # Configure treeview styles
        style.configure('Modern.Treeview',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       fieldbackground=self.colors['white'],
                       borderwidth=0,
                       font=('Segoe UI', 10))
        style.configure('Modern.Treeview.Heading',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=('Segoe UI', 11, 'bold'),
                       relief='flat')
        style.map('Modern.Treeview',
                 background=[('selected', self.colors['secondary'])],
                 foreground=[('selected', self.colors['white'])])
        
    def load_data(self):
        """Load expenses from JSON file, create if doesn't exist"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        else:
            # Create empty JSON file
            with open(self.data_file, 'w') as f:
                json.dump([], f)
            return []
    
    def save_data(self):
        """Save expenses to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.expenses, f, indent=2)
    
    def create_widgets(self):
        """Create the main GUI widgets with modern design"""
        # Create main container
        self.main_frame = tk.Frame(self.root, bg=self.colors['light'])
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(self.main_frame)
        
        # Create notebook for tabs with modern styling
        self.notebook = ttk.Notebook(self.main_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, pady=(20, 0))
        
        # Create tabs
        self.create_add_expense_tab()
        self.create_view_expenses_tab()
        self.create_analytics_tab()
        
        # Add AI features tab if available
        if AI_FEATURES_AVAILABLE:
            self.create_ai_features_tab()
        
        # AI Suggestions Panel (add after notebook)
        if AI_FEATURES_AVAILABLE:
            self.create_ai_suggestions_panel()
        
    def create_header(self, parent):
        """Create modern header section"""
        header_frame = tk.Frame(parent, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title and subtitle
        title_label = tk.Label(header_frame, 
                              text="💰 Expense Tracker Pro", 
                              font=('Segoe UI', 24, 'bold'),
                              fg=self.colors['white'],
                              bg=self.colors['primary'])
        title_label.pack(side='left', padx=20, pady=10)
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Professional Financial Management",
                                 font=('Segoe UI', 12),
                                 fg=self.colors['light'],
                                 bg=self.colors['primary'])
        subtitle_label.pack(side='left', padx=(0, 20), pady=(35, 10))
        
        # Quick stats and controls
        stats_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        stats_frame.pack(side='right', padx=20, pady=10)
        
        # Notification settings button
        notif_button = tk.Button(stats_frame, text="🔔", 
                               command=self.create_notification_settings_dialog,
                               bg=self.colors['secondary'], fg=self.colors['white'],
                               font=('Segoe UI', 12, 'bold'),
                               relief='flat', cursor='hand2', width=3)
        notif_button.pack(side='right', padx=(10, 0))
        
        total_expenses = sum(expense['amount'] for expense in self.expenses)
        total_transactions = len(self.expenses)
        
        self.quick_total_label = tk.Label(stats_frame,
                                         text=f"₹{total_expenses:,.2f}",
                                         font=('Segoe UI', 16, 'bold'),
                                         fg=self.colors['warning'],
                                         bg=self.colors['primary'])
        self.quick_total_label.pack()
        
        tk.Label(stats_frame,
                text=f"Total Expenses ({total_transactions} transactions)",
                font=('Segoe UI', 10),
                fg=self.colors['light'],
                bg=self.colors['primary']).pack()
    
    def create_add_expense_tab(self):
        """Create the add expense tab with modern card-based design"""
        add_frame = ttk.Frame(self.notebook)
        self.notebook.add(add_frame, text="➕ Add Expense")
        
        # Main container with padding
        main_container = tk.Frame(add_frame, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Left side - Add expense form
        left_frame = ttk.Frame(main_container, style='Card.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Form header
        form_header = tk.Frame(left_frame, bg=self.colors['white'], height=60)
        form_header.pack(fill='x', padx=20, pady=20)
        form_header.pack_propagate(False)
        
        tk.Label(form_header, 
                text="💳 Add New Expense",
                font=('Segoe UI', 18, 'bold'),
                fg=self.colors['primary'],
                bg=self.colors['white']).pack(side='left', pady=15)
        
        # Form content
        form_content = tk.Frame(left_frame, bg=self.colors['white'])
        form_content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Date field
        self.create_form_field(form_content, "📅 Date:", 0)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_frame = tk.Frame(form_content, bg=self.colors['white'])
        date_frame.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=10)
        self.date_entry = tk.Entry(date_frame, textvariable=self.date_var, 
                                  font=('Segoe UI', 11), relief='solid', 
                                  borderwidth=1, bg=self.colors['white'])
        self.date_entry.pack(fill='x', ipady=8)
        
        # Amount field
        self.create_form_field(form_content, "💰 Amount (₹):", 1)
        self.amount_var = tk.StringVar()
        amount_frame = tk.Frame(form_content, bg=self.colors['white'])
        amount_frame.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=10)
        self.amount_entry = tk.Entry(amount_frame, textvariable=self.amount_var,
                                    font=('Segoe UI', 11), relief='solid',
                                    borderwidth=1, bg=self.colors['white'])
        self.amount_entry.pack(fill='x', ipady=8)
        
        # Category field
        self.create_form_field(form_content, "🏷️ Category:", 2)
        self.category_var = tk.StringVar()
        categories = ["🍕 Food", "🚗 Transportation", "🎬 Entertainment",
                      "📱 Bills", "🏥 Healthcare", 
                      "📚 Education", "🛍️ Shopping", "📦 Other"]
        category_frame = tk.Frame(form_content, bg=self.colors['white'])
        category_frame.grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=10)
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                          values=categories, style='Modern.TCombobox',
                                          font=('Segoe UI', 11))
        self.category_combo.pack(fill='x', ipady=8)
        
        # Description field
        self.create_form_field(form_content, "📝 Description:", 3)
        self.description_var = tk.StringVar()
        desc_frame = tk.Frame(form_content, bg=self.colors['white'])
        desc_frame.grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=10)
        self.description_entry = tk.Entry(desc_frame, textvariable=self.description_var,
                                         font=('Segoe UI', 11), relief='solid',
                                         borderwidth=1, bg=self.colors['white'])
        self.description_entry.pack(fill='x', ipady=8)
        
        # Configure grid weights
        form_content.columnconfigure(1, weight=1)
        
        # Add button with gradient effect
        button_frame = tk.Frame(left_frame, bg=self.colors['white'])
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        add_button = tk.Button(button_frame, text="✨ Add Expense", 
                              command=self.add_expense,
                              bg=self.colors['success'], fg=self.colors['white'], 
                              font=('Segoe UI', 12, 'bold'),
                              relief='flat', cursor='hand2',
                              activebackground=self.colors['secondary'])
        add_button.pack(fill='x', ipady=12)
        
        # Right side - Recent expenses
        right_frame = ttk.Frame(main_container, style='Card.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # Recent expenses header
        recent_header = tk.Frame(right_frame, bg=self.colors['white'], height=60)
        recent_header.pack(fill='x', padx=20, pady=20)
        recent_header.pack_propagate(False)
        
        tk.Label(recent_header, 
                text="📊 Recent Expenses",
                font=('Segoe UI', 18, 'bold'),
                fg=self.colors['primary'],
                bg=self.colors['white']).pack(side='left', pady=15)
        
        # Recent expenses list
        recent_content = tk.Frame(right_frame, bg=self.colors['white'])
        recent_content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create modern treeview for recent expenses
        self.recent_tree = ttk.Treeview(recent_content, 
                                       columns=('Date', 'Amount', 'Category', 'Description'), 
                                       show='headings', height=12, style='Modern.Treeview')
        self.recent_tree.pack(fill='both', expand=True)
        
        # Configure columns
        self.recent_tree.heading('Date', text='Date')
        self.recent_tree.heading('Amount', text='Amount (₹)')
        self.recent_tree.heading('Category', text='Category')
        self.recent_tree.heading('Description', text='Description')
        
        self.recent_tree.column('Date', width=80, anchor='center')
        self.recent_tree.column('Amount', width=90, anchor='center')
        self.recent_tree.column('Category', width=100, anchor='center')
        self.recent_tree.column('Description', width=150)
        
        # Modern scrollbar
        recent_scrollbar = ttk.Scrollbar(recent_content, orient='vertical', 
                                        command=self.recent_tree.yview)
        recent_scrollbar.pack(side='right', fill='y')
        self.recent_tree.configure(yscrollcommand=recent_scrollbar.set)
        
    def create_form_field(self, parent, label_text, row):
        """Create a form field with modern styling"""
        label = tk.Label(parent, text=label_text, 
                        font=('Segoe UI', 12, 'bold'),
                        fg=self.colors['dark'], bg=self.colors['white'])
        label.grid(row=row, column=0, sticky='w', padx=(0, 10), pady=10)
    
    def create_view_expenses_tab(self):
        """Create the view expenses tab with modern design"""
        view_frame = ttk.Frame(self.notebook)
        self.notebook.add(view_frame, text="📋 View Expenses")
        
        # Main container
        main_container = tk.Frame(view_frame, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Controls card
        controls_card = ttk.Frame(main_container, style='Card.TFrame')
        controls_card.pack(fill='x', pady=(0, 20))
        
        controls_frame = tk.Frame(controls_card, bg=self.colors['white'])
        controls_frame.pack(fill='x', padx=20, pady=15)
        
        # Controls header
        tk.Label(controls_frame, text="🎛️ Filter & Sort Options", 
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['white']).pack(anchor='w', pady=(0, 10))
        
        # Controls row
        controls_row = tk.Frame(controls_frame, bg=self.colors['white'])
        controls_row.pack(fill='x')
        
        # Sorting options
        sort_frame = tk.Frame(controls_row, bg=self.colors['white'])
        sort_frame.pack(side='left', padx=(0, 30))
        
        tk.Label(sort_frame, text="Sort by:", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['white'], fg=self.colors['dark']).pack(anchor='w')
        self.sort_var = tk.StringVar(value="Date (Recent)")
        sort_options = ["Date (Recent)", "Date (Oldest)", "Amount (High to Low)", 
                       "Amount (Low to High)", "Category"]
        self.sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, 
                                      values=sort_options, style='Modern.TCombobox',
                                      width=18, font=('Segoe UI', 10))
        self.sort_combo.pack(pady=(5, 0), ipady=5)
        self.sort_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_transactions())
        
        # Category filter
        filter_frame = tk.Frame(controls_row, bg=self.colors['white'])
        filter_frame.pack(side='left', padx=(0, 30))
        
        tk.Label(filter_frame, text="Filter by Category:", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['white'], fg=self.colors['dark']).pack(anchor='w')
        self.filter_var = tk.StringVar(value="All")
        filter_options = ["All", "🍕 Food", "🚗 Transportation", "🎬 Entertainment", 
                         "🛍️ Shopping", "📱 Bills", "🏥 Healthcare", "📚 Education", "📦 Other"]
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                        values=filter_options, style='Modern.TCombobox',
                                        width=18, font=('Segoe UI', 10))
        self.filter_combo.pack(pady=(5, 0), ipady=5)
        self.filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_transactions())
        
        # Action buttons
        button_frame = tk.Frame(controls_row, bg=self.colors['white'])
        button_frame.pack(side='right')
        
        delete_button = tk.Button(button_frame, text="🗑️ Delete Selected", 
                                 command=self.delete_expense,
                                 bg=self.colors['danger'], fg=self.colors['white'], 
                                 font=('Segoe UI', 10, 'bold'),
                                 relief='flat', cursor='hand2',
                                 activebackground='#c0392b')
        delete_button.pack(side='right', padx=5, ipady=8, ipadx=15)
        
        refresh_button = tk.Button(button_frame, text="🔄 Refresh", 
                                  command=self.refresh_transactions,
                                  bg=self.colors['info'], fg=self.colors['white'], 
                                  font=('Segoe UI', 10, 'bold'),
                                  relief='flat', cursor='hand2',
                                  activebackground='#138496')
        refresh_button.pack(side='right', padx=5, ipady=8, ipadx=15)
        
        # Transactions card
        transactions_card = ttk.Frame(main_container, style='Card.TFrame')
        transactions_card.pack(fill='both', expand=True, pady=(0, 20))
        
        # Transactions header
        trans_header = tk.Frame(transactions_card, bg=self.colors['white'])
        trans_header.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(trans_header, text="💳 Transaction History", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['primary'], bg=self.colors['white']).pack(side='left')
        
        # Transactions content
        trans_content = tk.Frame(transactions_card, bg=self.colors['white'])
        trans_content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Modern treeview
        self.transactions_tree = ttk.Treeview(trans_content, 
                                             columns=('Date', 'Amount', 'Category', 'Description'), 
                                             show='headings', style='Modern.Treeview')
        self.transactions_tree.pack(side='left', fill='both', expand=True)
        
        # Configure columns with better styling
        self.transactions_tree.heading('Date', text='📅 Date')
        self.transactions_tree.heading('Amount', text='💰 Amount (₹)')
        self.transactions_tree.heading('Category', text='🏷️ Category')
        self.transactions_tree.heading('Description', text='📝 Description')
        
        self.transactions_tree.column('Date', width=100, anchor='center')
        self.transactions_tree.column('Amount', width=120, anchor='center')
        self.transactions_tree.column('Category', width=140, anchor='center')
        self.transactions_tree.column('Description', width=300)
        
        # Modern scrollbar
        trans_scrollbar = ttk.Scrollbar(trans_content, orient='vertical', 
                                       command=self.transactions_tree.yview)
        trans_scrollbar.pack(side='right', fill='y')
        self.transactions_tree.configure(yscrollcommand=trans_scrollbar.set)
        
        # Summary card
        summary_card = ttk.Frame(main_container, style='Card.TFrame')
        summary_card.pack(fill='x')
        
        summary_frame = tk.Frame(summary_card, bg=self.colors['white'])
        summary_frame.pack(fill='x', padx=20, pady=15)
        
        # Summary content
        summary_left = tk.Frame(summary_frame, bg=self.colors['white'])
        summary_left.pack(side='left')
        
        self.total_label = tk.Label(summary_left, text="Total Expenses: ₹0", 
                                   font=('Segoe UI', 14, 'bold'), 
                                   fg=self.colors['danger'], bg=self.colors['white'])
        self.total_label.pack(anchor='w')
        
        summary_right = tk.Frame(summary_frame, bg=self.colors['white'])
        summary_right.pack(side='right')
        
        self.count_label = tk.Label(summary_right, text="Number of Transactions: 0", 
                                   font=('Segoe UI', 12), 
                                   fg=self.colors['dark'], bg=self.colors['white'])
        self.count_label.pack(anchor='e')
    
    def create_analytics_tab(self):
        """Create the analytics tab with enhanced visualizations"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Main container
        main_container = tk.Frame(analytics_frame, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Controls card
        controls_card = ttk.Frame(main_container, style='Card.TFrame')
        controls_card.pack(fill='x', pady=(0, 20))
        
        controls_frame = tk.Frame(controls_card, bg=self.colors['white'])
        controls_frame.pack(fill='x', padx=20, pady=15)
        
        # Controls header
        tk.Label(controls_frame, text="📈 Analytics Dashboard", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['primary'], bg=self.colors['white']).pack(anchor='w', pady=(0, 10))
        
        # Controls row
        controls_row = tk.Frame(controls_frame, bg=self.colors['white'])
        controls_row.pack(fill='x')
        
        # Month selection
        month_frame = tk.Frame(controls_row, bg=self.colors['white'])
        month_frame.pack(side='left', padx=(0, 20))
        
        tk.Label(month_frame, text="📅 Select Month:", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['white'], fg=self.colors['dark']).pack(anchor='w')
        current_month = datetime.now().strftime("%Y-%m")
        self.month_var = tk.StringVar(value=current_month)
        month_entry = tk.Entry(month_frame, textvariable=self.month_var, 
                              font=('Segoe UI', 11), width=12,
                              relief='solid', borderwidth=1, bg=self.colors['white'])
        month_entry.pack(pady=(5, 0), ipady=5)
        month_entry.bind('<Return>', lambda e: self.update_graph())
        
        # Control buttons
        button_frame = tk.Frame(controls_row, bg=self.colors['white'])
        button_frame.pack(side='right')
        
        refresh_button = tk.Button(button_frame, text="🔄 Refresh Charts", 
                                  command=self.update_graph,
                                  bg=self.colors['secondary'], fg=self.colors['white'], 
                                  font=('Segoe UI', 11, 'bold'),
                                  relief='flat', cursor='hand2',
                                  activebackground=self.colors['primary'])
        refresh_button.pack(side='right', padx=5, ipady=10, ipadx=20)
        
        export_button = tk.Button(button_frame, text="📊 Export Data", 
                                 command=self.export_data,
                                 bg=self.colors['accent'], fg=self.colors['white'], 
                                 font=('Segoe UI', 11, 'bold'),
                                 relief='flat', cursor='hand2',
                                 activebackground='#8e44ad')
        export_button.pack(side='right', padx=5, ipady=10, ipadx=20)
        
        # Charts card
        charts_card = ttk.Frame(main_container, style='Card.TFrame')
        charts_card.pack(fill='both', expand=True)
        
        charts_content = tk.Frame(charts_card, bg=self.colors['white'])
        charts_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create optimized matplotlib figure
        self.fig = Figure(figsize=(12, 8), dpi=100, facecolor='white')
        self.fig.patch.set_facecolor('white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, charts_content)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Add navigation toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar_frame = tk.Frame(charts_content, bg=self.colors['white'])
        toolbar_frame.pack(fill='x', pady=(10, 0))
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.config(bg=self.colors['white'])
        toolbar.update()
        
    def export_data(self):
        """Export expense data to CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            if not self.expenses:
                messagebox.showinfo("No Data", "No expenses to export!")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Expenses"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['date', 'amount', 'category', 'description', 'timestamp']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for expense in self.expenses:
                        writer.writerow(expense)
                
                # Show success notifications
                self.show_toast_notification("📊 Export Complete", f"Data exported to {os.path.basename(file_path)}", "success")
                self.show_system_notification("📊 Export Complete", f"Expense data has been exported to {file_path}")
                messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def add_expense(self):
        """Add a new expense with enhanced validation and AI categorization"""
        try:
            # Validate inputs
            if not self.amount_var.get():
                messagebox.showerror("❌ Error", "Please fill in amount")
                return
            
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("❌ Error", "Amount must be positive")
                return
            
            description = self.description_var.get() or "No description"
            
            # Use AI categorization if available and category not manually selected
            category = self.category_var.get()
            if (not category or category == "Select category") and AI_FEATURES_AVAILABLE and self.ai_categorizer:
                # Try AI categorization
                suggested_category = self.ai_categorizer.smart_categorize(description, amount)
                
                # Ask user if they want to use the suggestion
                if suggested_category and suggested_category != "Other":
                    result = messagebox.askyesno(
                        "🤖 AI Suggestion", 
                        f"AI suggests category: '{suggested_category}'\n\nUse this suggestion?",
                        icon='question'
                    )
                    if result:
                        category = suggested_category
                        # Train the AI with user's acceptance
                        self.ai_categorizer.learn_from_feedback(description, amount, suggested_category, True)
                    else:
                        # Let user choose manually
                        category = self.category_var.get()
                        if not category or category == "Select category":
                            messagebox.showerror("❌ Error", "Please select a category")
                            return
                        # Train the AI with user's rejection and correct choice
                        self.ai_categorizer.learn_from_feedback(description, amount, category, False)
                else:
                    if not category or category == "Select category":
                        messagebox.showerror("❌ Error", "Please select a category")
                        return
            elif not category or category == "Select category":
                messagebox.showerror("❌ Error", "Please select a category")
                return
            
            # Clean category (remove emoji if present)
            if category.startswith('🍕'):
                category = "Food"
            elif category.startswith('🚗'):
                category = "Transportation"
            elif category.startswith('🎬'):
                category = "Entertainment"
            elif category.startswith('🛍️'):
                category = "Shopping"
            elif category.startswith('📱'):
                category = "Bills"
            elif category.startswith('🏥'):
                category = "Healthcare"
            elif category.startswith('📚'):
                category = "Education"
            elif category.startswith('📦'):
                category = "Other"
            
            # Create expense entry
            expense = {
                "date": self.date_var.get(),
                "amount": amount,
                "category": category,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to expenses list
            self.expenses.append(expense)
            self.save_data()
            
            # Clear form
            self.amount_var.set("")
            self.description_var.set("")
            
            # Update header stats
            self.update_header_stats()
            
            # Refresh displays
            self.refresh_transactions()
            self.refresh_recent_expenses()
            self.update_graph()
            
            # Check for achievements
            self.check_achievements()
            
            # Check daily budget
            self.check_daily_budget()
            
            # Show success notification
            self.show_toast_notification("✅ Success", "Expense added successfully!", "success")
            messagebox.showinfo("✅ Success", "Expense added successfully!")
            
            # Update AI suggestions after adding expense
            if AI_FEATURES_AVAILABLE and hasattr(self, 'suggestions_container'):
                self.root.after(500, self.update_ai_suggestions)
                # Check for urgent alerts
                self.root.after(1000, self.check_for_urgent_alerts)
            
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter a valid amount")
    
    def update_header_stats(self):
        """Update the header statistics"""
        total_expenses = sum(expense['amount'] for expense in self.expenses)
        total_transactions = len(self.expenses)
        
        self.quick_total_label.config(text=f"₹{total_expenses:,.2f}")
        # Update the transactions count label if it exists
        for widget in self.quick_total_label.master.winfo_children():
            if isinstance(widget, tk.Label) and "transactions" in widget.cget("text"):
                widget.config(text=f"Total Expenses ({total_transactions} transactions)")
    
    def delete_expense(self):
        """Delete selected expense with enhanced feedback"""
        selected = self.transactions_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Warning", "Please select an expense to delete")
            return
        
        if messagebox.askyesno("🗑️ Confirm Deletion", "Are you sure you want to delete this expense?\n\nThis action cannot be undone."):
            # Get the index of the selected item
            item = self.transactions_tree.item(selected[0])
            date = item['values'][0]
            amount_str = item['values'][1].replace('₹', '').replace(',', '')
            amount = float(amount_str)
            category_full = item['values'][2]
            # Extract category name (remove emoji)
            category = category_full.split(' ', 1)[-1] if ' ' in category_full else category_full
            description = item['values'][3]
            
            # Find and remove the expense
            for i, expense in enumerate(self.expenses):
                if (expense['date'] == date and 
                    expense['amount'] == amount and 
                    expense['category'] == category and 
                    expense['description'] == description):
                    del self.expenses[i]
                    break
            
            self.save_data()
            self.update_header_stats()
            self.refresh_transactions()
            self.refresh_recent_expenses()
            self.update_graph()
            
            # Show deletion notification
            self.show_toast_notification("🗑️ Deleted", "Expense deleted successfully!", "info")
            messagebox.showinfo("✅ Success", "Expense deleted successfully!")
    
    def refresh_transactions(self):
        """Refresh the transactions view with sorting and filtering"""
        # Clear existing items
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Get filtered expenses
        filtered_expenses = self.expenses.copy()
        
        # Apply category filter (handle emoji categories)
        filter_value = self.filter_var.get()
        if filter_value != "All":
            # Convert emoji category to plain category
            category_map = {
                "🍕 Food": "Food",
                "🚗 Transportation": "Transportation", 
                "🎬 Entertainment": "Entertainment",
                "🛍️ Shopping": "Shopping",
                "📱 Bills": "Bills",
                "🏥 Healthcare": "Healthcare",
                "📚 Education": "Education",
                "📦 Other": "Other"
            }
            target_category = category_map.get(filter_value, filter_value)
            filtered_expenses = [e for e in filtered_expenses if e['category'] == target_category]
        
        # Apply sorting
        sort_option = self.sort_var.get()
        if sort_option == "Date (Recent)":
            filtered_expenses.sort(key=lambda x: x['date'], reverse=True)
        elif sort_option == "Date (Oldest)":
            filtered_expenses.sort(key=lambda x: x['date'])
        elif sort_option == "Amount (High to Low)":
            filtered_expenses.sort(key=lambda x: x['amount'], reverse=True)
        elif sort_option == "Amount (Low to High)":
            filtered_expenses.sort(key=lambda x: x['amount'])
        elif sort_option == "Category":
            filtered_expenses.sort(key=lambda x: x['category'])
        
        # Populate treeview with alternating row colors
        total_amount = 0
        for i, expense in enumerate(filtered_expenses):
            # Add emoji to category for display
            display_category = expense['category']
            category_emojis = {
                "Food": "🍕",
                "Transportation": "🚗",
                "Entertainment": "🎬",
                "Shopping": "🛍️",
                "Bills": "📱",
                "Healthcare": "🏥",
                "Education": "📚",
                "Other": "📦"
            }
            if display_category in category_emojis:
                display_category = f"{category_emojis[display_category]} {display_category}"
            
            item_id = self.transactions_tree.insert('', 'end', values=(
                expense['date'],
                f"₹{expense['amount']:.2f}",
                display_category,
                expense['description']
            ))
            
            # Alternate row colors
            if i % 2 == 0:
                self.transactions_tree.item(item_id, tags=('evenrow',))
            else:
                self.transactions_tree.item(item_id, tags=('oddrow',))
                
            total_amount += expense['amount']
        
        # Configure row colors
        self.transactions_tree.tag_configure('evenrow', background='#f8f9fa')
        self.transactions_tree.tag_configure('oddrow', background='#ffffff')
        
        # Update summary
        self.total_label.config(text=f"💰 Total Expenses: ₹{total_amount:,.2f}")
        self.count_label.config(text=f"📊 Transactions: {len(filtered_expenses)}")
        
        # Update AI suggestions when data changes
        if AI_FEATURES_AVAILABLE and hasattr(self, 'suggestions_container'):
            self.root.after(1000, self.update_ai_suggestions)  # Delay to avoid too frequent updates
    
    def refresh_recent_expenses(self):
        """Refresh the recent expenses view in add tab with enhanced display"""
        # Clear existing ite
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        # Get recent expenses (last 8)
        recent_expenses = sorted(self.expenses, key=lambda x: x['timestamp'], reverse=True)[:8]
        
        # Populate treeview with enhanced formatting
        for i, expense in enumerate(recent_expenses):
            # Add emoji to category for display
            display_category = expense['category']
            category_emojis = {
                "Food": "🍕",
                "Transportation": "🚗",
                "Entertainment": "🎬",
                "Shopping": "🛍️",
                "Bills": "📱",
                "Healthcare": "🏥",
                "Education": "📚",
                "Other": "📦"
            }
            if display_category in category_emojis:
                display_category = f"{category_emojis[display_category]} {display_category}"
            
            item_id = self.recent_tree.insert('', 'end', values=(
                expense['date'],
                f"₹{expense['amount']:.2f}",
                display_category,
                expense['description']
            ))
            
            # Alternate row colors
            if i % 2 == 0:
                self.recent_tree.item(item_id, tags=('evenrow',))
            else:
                self.recent_tree.item(item_id, tags=('oddrow',))
        
        # Configure row colors
        self.recent_tree.tag_configure('evenrow', background='#f8f9fa')
        self.recent_tree.tag_configure('oddrow', background='#ffffff')
    
    def update_graph(self):
        """Update the monthly expense graph with optimized visualizations"""
        self.fig.clear()

        # Set modern style
        plt.style.use('seaborn-v0_8-whitegrid')

        # Get current month data
        try:
            target_month = self.month_var.get()
            year, month = map(int, target_month.split('-'))
        except:
            year, month = datetime.now().year, datetime.now().month
            target_month = f"{year:04d}-{month:02d}"

        # Filter expenses for the target month
        month_expenses = [e for e in self.expenses if e['date'].startswith(target_month)]

        if month_expenses:
            # Create a clean 1x2 grid layout with equal column widths
            gs = self.fig.add_gridspec(1, 2, width_ratios=[1, 1], 
                                       hspace=0.3, wspace=0.4,
                                       left=0.08, right=0.95, top=0.85, bottom=0.15)

            # Monthly summary stats (left side)
            ax1 = self.fig.add_subplot(gs[0, 0])
            self.create_summary_stats(ax1, month_expenses, target_month)

            # Weekly spending trend (right side)
            ax2 = self.fig.add_subplot(gs[0, 1])
            self.create_enhanced_weekly_trend(ax2, month_expenses)

        else:
            # Enhanced no data display
            ax = self.fig.add_subplot(1, 1, 1)
            ax.text(0.5, 0.5, f'📊 No expenses found for {target_month}\n\n💡 Add some expenses to see beautiful charts!',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=18,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
            ax.set_title('Monthly Expense Dashboard', fontsize=20, fontweight='bold', pad=20)
            ax.axis('off')

        # Set modern title
        self.fig.suptitle(f'📊 Expense Analytics Dashboard - {target_month}',
                          fontsize=14, fontweight='bold', y=0.93, color='#2c3e50')

        self.fig.patch.set_facecolor('white')
        self.canvas.draw()
    
    def create_enhanced_daily_chart(self, ax, month_expenses, year, month):
        """Create compact daily expense bar chart"""
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        days_in_month = (next_month - datetime(year, month, 1)).days

        daily_amounts = {i: 0 for i in range(1, days_in_month + 1)}
        for expense in month_expenses:
            day = int(expense['date'].split('-')[2])
            daily_amounts[day] += expense['amount']

        days = list(daily_amounts.keys())
        amounts = list(daily_amounts.values())
        max_amount = max(amounts) if amounts else 1

        # Soft blue gradient
        custom_cmap = LinearSegmentedColormap.from_list("soft_grad", ["#74b9ff", "#0984e3", "#2d3436"])
        colors = [custom_cmap(amount / max_amount) if amount > 0 else '#f0f0f0' for amount in amounts]

        bars = ax.bar(days, amounts, color=colors, alpha=0.85, edgecolor='white', linewidth=0.4)
        sorted_amounts = sorted(enumerate(amounts), key=lambda x: x[1], reverse=True)
        top_3_indices = [i for i, _ in sorted_amounts[:3] if amounts[i] > 0]

        for i in top_3_indices:
            ax.text(days[i], amounts[i] + max_amount * 0.02,
                    f'₹{amounts[i]:.0f}', ha='center', va='bottom',
                    fontsize=7, fontweight='bold', color="#2c3e50")

        ax.set_title('Daily Spending', fontsize=11, fontweight='bold', pad=10, color='#2c3e50')
        ax.set_xlabel('Day', fontweight='bold', fontsize=9)
        ax.set_ylabel('Amount (₹)', fontweight='bold', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(0.5, days_in_month + 0.5)
        ax.set_xticks([1, 5, 10, 15, 20, 25, days_in_month])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'₹{x/1000:.0f}k' if x >= 1000 else f'₹{x:.0f}'))
        ax.tick_params(axis='both', labelsize=8)
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def create_enhanced_category_chart(self, ax, month_expenses):
        """Create compact category-wise pie chart"""
        category_totals = {}
        for expense in month_expenses:
            category = expense['category']
            category_totals[category] = category_totals.get(category, 0) + expense['amount']

        if category_totals:
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))

            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.0f%%',
                                              colors=colors, startangle=90,
                                              explode=[0.02] * len(categories),
                                              textprops={'fontsize': 8, 'fontweight': 'bold'},
                                              wedgeprops=dict(edgecolor='white', linewidth=0.7))

            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)

            for text in texts:
                text.set_fontsize(8)

            ax.set_title('Category Breakdown', fontsize=11, fontweight='bold', pad=10, color='#2c3e50')
        else:
            ax.text(0.5, 0.5, '📊 No category data', horizontalalignment='center',
                    verticalalignment='center', transform=ax.transAxes, fontsize=10)
            ax.set_title('Category Breakdown', fontsize=11, fontweight='bold', pad=10, color='#2c3e50')
            ax.axis('off')
    
    def create_enhanced_weekly_trend(self, ax, month_expenses):
        """Create enhanced weekly spending trend chart"""
        weekly_totals = {}
        for expense in month_expenses:
            date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
            week_start = date_obj - timedelta(days=date_obj.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            weekly_totals[week_key] = weekly_totals.get(week_key, 0) + expense['amount']

        if weekly_totals:
            weeks = sorted(weekly_totals.keys())
            amounts = [weekly_totals[week] for week in weeks]
            week_labels = [f"Week {i+1}" for i in range(len(weeks))]

            # Enhanced gradient colors for bars
            max_amount = max(amounts)
            colors = ['#3498db' if amount == max_amount else '#74b9ff' for amount in amounts]

            bars = ax.bar(week_labels, amounts, color=colors, alpha=0.85, 
                         edgecolor='white', linewidth=1.5, width=0.7)
            
            # Add value labels on top of bars
            for bar, amount in zip(bars, amounts):
                if amount > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2., 
                           bar.get_height() + max(amounts) * 0.03,
                           f'₹{amount:,.0f}', ha='center', va='bottom', 
                           fontsize=10, fontweight='bold', color='#2c3e50')

            # Enhanced styling
            ax.set_title('📈 Weekly Expense Trend', fontsize=14, fontweight='bold', 
                        pad=20, color='#2c3e50')
            ax.set_xlabel('Week', fontweight='bold', fontsize=11, color='#2c3e50')
            ax.set_ylabel('Amount (₹)', fontweight='bold', fontsize=11, color='#2c3e50')
            ax.grid(True, alpha=0.3, linestyle='--', axis='y')
            
            # Format y-axis
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'₹{x:,.0f}'))
            ax.tick_params(axis='both', labelsize=10, colors='#2c3e50')
            
            # Remove spines for cleaner look
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Set y-axis limit with some padding
            ax.set_ylim(0, max(amounts) * 1.15)
            
        else:
            ax.text(0.5, 0.5, '📈 No Weekly Data Available', 
                    horizontalalignment='center',
                    verticalalignment='center', 
                    transform=ax.transAxes, 
                    fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", alpha=0.8))
            ax.set_title('📈 Weekly Expense Trend', fontsize=14, fontweight='bold', 
                        pad=20, color='#2c3e50')
            ax.axis('off')
    
    def create_summary_stats(self, ax, month_expenses, target_month):
        """Create enhanced summary statistics display"""
        ax.axis('off')

        if month_expenses:
            total_amount = sum(expense['amount'] for expense in month_expenses)
            avg_daily = total_amount / 30  # Approximate daily average
            max_expense = max(expense['amount'] for expense in month_expenses)
            min_expense = min(expense['amount'] for expense in month_expenses)
            
            # Calculate category breakdown for summary
            category_totals = {}
            for expense in month_expenses:
                category = expense['category']
                category_totals[category] = category_totals.get(category, 0) + expense['amount']
            
            top_category = max(category_totals, key=category_totals.get) if category_totals else "N/A"

            # Enhanced stats layout
            stats_text = (
                f"📊 MONTHLY SUMMARY\n"
                f"────────────────────\n\n"
                f"💰 Total Spent: ₹{total_amount:,.0f}\n"
                f"📈 Transactions: {len(month_expenses)}\n"
                f"📅 Daily Average: ₹{avg_daily:,.0f}\n"
                f"🔝 Highest: ₹{max_expense:,.0f}\n"
                f"🔻 Lowest: ₹{min_expense:,.0f}\n"
                f"🏆 Top Category: {top_category}"
            )

            # Create a more professional summary box
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=11,
                    verticalalignment='top', fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.6", 
                             facecolor="#e8f4fd", 
                             edgecolor="#3498db",
                             linewidth=2,
                             alpha=0.9),
                    color='#2c3e50')
        else:
            ax.text(0.5, 0.5, '📊 No Summary Data Available', 
                    horizontalalignment='center',
                    verticalalignment='center', 
                    transform=ax.transAxes, 
                    fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#f9f9f9", alpha=0.8))

  
    def start_notification_service(self):
        """Start the background notification service"""
        def notification_worker():
            while True:
                try:
                    # Check daily budget every hour
                    self.check_daily_budget()
                    
                    # Check for weekly spending reminders
                    self.check_weekly_reminder()
                    
                    # Sleep for 1 hour
                    time.sleep(3600)
                except Exception as e:
                    print(f"Notification service error: {e}")
                    time.sleep(3600)
        
        # Start notification service in background thread
        notification_thread = threading.Thread(target=notification_worker, daemon=True)
        notification_thread.start()
    
    def show_toast_notification(self, title, message, type="info", duration=3000):
        """Show toast notification within the app"""
        # Create toast window
        toast = tk.Toplevel(self.root)
        toast.withdraw()  # Hide initially
        
        # Configure toast window
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        
        # Color scheme based on type
        colors = {
            "success": {"bg": "#27ae60", "fg": "#ffffff"},
            "error": {"bg": "#e74c3c", "fg": "#ffffff"},
            "warning": {"bg": "#f39c12", "fg": "#ffffff"},
            "info": {"bg": "#3498db", "fg": "#ffffff"}
        }
        
        color_scheme = colors.get(type, colors["info"])
        
        # Create toast frame
        toast_frame = tk.Frame(toast, bg=color_scheme["bg"], relief='raised', bd=1)
        toast_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Icon mapping
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        icon = icons.get(type, "ℹ️")
        
        # Title with icon
        title_label = tk.Label(toast_frame, text=f"{icon} {title}", 
                              font=('Segoe UI', 11, 'bold'),
                              bg=color_scheme["bg"], fg=color_scheme["fg"])
        title_label.pack(anchor='w', padx=10, pady=(8, 2))
        
        # Message
        message_label = tk.Label(toast_frame, text=message, 
                                font=('Segoe UI', 9),
                                bg=color_scheme["bg"], fg=color_scheme["fg"],
                                wraplength=300, justify='left')
        message_label.pack(anchor='w', padx=10, pady=(0, 8))
        
        # Position toast at top-right of main window
        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        
        toast.update_idletasks()
        toast_width = toast.winfo_reqwidth()
        toast_height = toast.winfo_reqheight()
        
        x = main_x + main_width - toast_width - 20
        y = main_y + 20
        
        toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        toast.deiconify()
        
        # Auto-close toast after duration
        def close_toast():
            try:
                # Fade out animation
                for alpha in range(100, 0, -5):
                    toast.attributes('-alpha', alpha/100)
                    toast.update()
                    time.sleep(0.02)
                toast.destroy()
            except:
                pass
        
        # Set initial alpha and schedule closing
        toast.attributes('-alpha', 0.95)
        self.root.after(duration, close_toast)
        
        # Click to close
        def close_on_click(event=None):
            toast.destroy()
        
        toast.bind('<Button-1>', close_on_click)
        toast_frame.bind('<Button-1>', close_on_click)
        title_label.bind('<Button-1>', close_on_click)
        message_label.bind('<Button-1>', close_on_click)
    
    def show_system_notification(self, title, message, timeout=10):
        """Show system tray notification"""
        if NOTIFICATIONS_AVAILABLE and self.notifications_enabled:
            try:
                plyer.notification.notify(
                    title=title,
                    message=message,
                    app_name="Expense Tracker Pro",
                    timeout=timeout,
                    toast=True
                )
            except Exception as e:
                print(f"System notification error: {e}")
    
    def check_daily_budget(self):
        """Check if daily spending exceeds budget"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_expenses = [e for e in self.expenses if e['date'] == today]
        daily_total = sum(expense['amount'] for expense in today_expenses)
        
        if daily_total > self.daily_budget:
            excess = daily_total - self.daily_budget
            
            # Check if we already notified about this today
            notification_key = f"daily_budget_{today}"
            if notification_key not in self.notification_history:
                self.notification_history.append(notification_key)
                
                # Show both toast and system notification
                self.show_toast_notification(
                    "💸 Budget Alert!", 
                    f"Daily spending exceeded by ₹{excess:.2f}\nTotal today: ₹{daily_total:.2f}",
                    "warning"
                )
                
                self.show_system_notification(
                    "💸 Daily Budget Exceeded!",
                    f"You've spent ₹{daily_total:.2f} today, exceeding your budget by ₹{excess:.2f}"
                )
    
    def check_weekly_reminder(self):
        """Check for weekly spending reminders"""
        now = datetime.now()
        
        # Send weekly summary every Sunday at 9 PM
        if now.weekday() == 6 and now.hour == 21:  # Sunday, 9 PM
            week_start = now - timedelta(days=7)
            week_expenses = [e for e in self.expenses 
                           if datetime.strptime(e['date'], '%Y-%m-%d') >= week_start]
            
            if week_expenses:
                weekly_total = sum(expense['amount'] for expense in week_expenses)
                
                # Check if we already sent weekly summary today
                notification_key = f"weekly_summary_{now.strftime('%Y-%m-%d')}"
                if notification_key not in self.notification_history:
                    self.notification_history.append(notification_key)
                    
                    self.show_toast_notification(
                        "📊 Weekly Summary",
                        f"This week's spending: ₹{weekly_total:.2f}\nTransactions: {len(week_expenses)}",
                        "info"
                    )
                    
                    self.show_system_notification(
                        "📊 Weekly Expense Summary",
                        f"You spent ₹{weekly_total:.2f} this week across {len(week_expenses)} transactions"
                    )
    
    def show_achievement_notification(self, achievement_text):
        """Show achievement/milestone notifications"""
        self.show_toast_notification(
            "🏆 Achievement Unlocked!",
            achievement_text,
            "success",
            duration=5000
        )
        
        self.show_system_notification(
            "🏆 Achievement Unlocked!",
            achievement_text
        )
    
    def check_achievements(self):
        """Check for spending milestones and achievements"""
        total_expenses = len(self.expenses)
        total_amount = sum(expense['amount'] for expense in self.expenses)
        
        # Achievement milestones
        achievements = [
            (10, "First 10 transactions recorded!"),
            (50, "50 transactions milestone reached!"),
            (100, "Century of transactions achieved!"),
            (500, "500 transactions - You're a tracking pro!"),
            (1000, "1000 transactions - Financial master!")
        ]
        
        amount_achievements = [
            (10000, "₹10,000 total expenses tracked!"),
            (50000, "₹50,000 spending milestone!"),
            (100000, "₹1,00,000 - Major spending milestone!"),
            (500000, "₹5,00,000 tracked - Big spender!")
        ]
        
        # Check transaction count achievements
        for milestone, message in achievements:
            if total_expenses == milestone:
                self.show_achievement_notification(message)
                break
        
        # Check amount achievements
        for milestone, message in amount_achievements:
            if abs(total_amount - milestone) < 100:  # Within 100 of milestone
                achievement_key = f"amount_{milestone}"
                if achievement_key not in self.notification_history:
                    self.notification_history.append(achievement_key)
                    self.show_achievement_notification(message)
                break
    
    def create_notification_settings_dialog(self):
        """Create notification settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("🔔 Notification Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['light'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (300 // 2)
        settings_window.geometry(f"400x300+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(settings_window, bg=self.colors['primary'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔔 Notification Settings", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['white'], bg=self.colors['primary']).pack(pady=15)
        
        # Content frame
        content_frame = tk.Frame(settings_window, bg=self.colors['light'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Enable/Disable notifications
        notif_frame = tk.Frame(content_frame, bg=self.colors['white'], relief='solid', bd=1)
        notif_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(notif_frame, text="General Settings", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor='w', padx=15, pady=(10, 5))
        
        self.notifications_var = tk.BooleanVar(value=self.notifications_enabled)
        notif_check = tk.Checkbutton(notif_frame, 
                                    text="🔔 Enable Notifications",
                                    variable=self.notifications_var,
                                    font=('Segoe UI', 11),
                                    bg=self.colors['white'], fg=self.colors['dark'])
        notif_check.pack(anchor='w', padx=15, pady=5)
        
        # Daily budget setting
        budget_frame = tk.Frame(content_frame, bg=self.colors['white'], relief='solid', bd=1)
        budget_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(budget_frame, text="Budget Alerts", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor='w', padx=15, pady=(10, 5))
        
        budget_row = tk.Frame(budget_frame, bg=self.colors['white'])
        budget_row.pack(fill='x', padx=15, pady=5)
        
        tk.Label(budget_row, text="💰 Daily Budget (₹):", 
                font=('Segoe UI', 11),
                bg=self.colors['white'], fg=self.colors['dark']).pack(side='left')
        
        self.budget_var = tk.StringVar(value=str(self.daily_budget))
        budget_entry = tk.Entry(budget_row, textvariable=self.budget_var, 
                               font=('Segoe UI', 11), width=10,
                               relief='solid', borderwidth=1)
        budget_entry.pack(side='right')
        
        # Test notification button
        test_frame = tk.Frame(content_frame, bg=self.colors['white'], relief='solid', bd=1)
        test_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(test_frame, text="Test Notifications", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor='w', padx=15, pady=(10, 5))
        
        test_button = tk.Button(test_frame, text="🧪 Test Notification", 
                               command=self.test_notification,
                               bg=self.colors['info'], fg=self.colors['white'],
                               font=('Segoe UI', 10, 'bold'),
                               relief='flat', cursor='hand2')
        test_button.pack(anchor='w', padx=15, pady=(5, 15))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg=self.colors['light'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        save_button = tk.Button(button_frame, text="💾 Save Settings", 
                               command=lambda: self.save_notification_settings(settings_window),
                               bg=self.colors['success'], fg=self.colors['white'],
                               font=('Segoe UI', 11, 'bold'),
                               relief='flat', cursor='hand2')
        save_button.pack(side='right', padx=(5, 0), ipady=8, ipadx=15)
        
        cancel_button = tk.Button(button_frame, text="❌ Cancel", 
                                 command=settings_window.destroy,
                                 bg=self.colors['danger'], fg=self.colors['white'],
                                 font=('Segoe UI', 11, 'bold'),
                                 relief='flat', cursor='hand2')
        cancel_button.pack(side='right', padx=(0, 5), ipady=8, ipadx=15)
    
    def test_notification(self):
        """Test notification system"""
        self.show_toast_notification(
            "🧪 Test Notification", 
            "This is a test notification from Expense Tracker Pro!", 
            "info"
        )
        
        self.show_system_notification(
            "🧪 Test Notification",
            "Your notification system is working perfectly!"
        )
    
    def save_notification_settings(self, window):
        """Save notification settings"""
        try:
            self.notifications_enabled = self.notifications_var.get()
            self.daily_budget = float(self.budget_var.get())
            
            # Save settings to file
            settings = {
                "notifications_enabled": self.notifications_enabled,
                "daily_budget": self.daily_budget
            }
            
            settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.show_toast_notification(
                "✅ Settings Saved", 
                "Notification settings have been updated successfully!", 
                "success"
            )
            
            window.destroy()
            
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter a valid budget amount")
    
    def load_notification_settings(self):
        """Load notification settings from file"""
        settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                self.notifications_enabled = settings.get("notifications_enabled", True)
                self.daily_budget = settings.get("daily_budget", 1000)
            except:
                pass  # Use defaults if loading fails

    def create_ai_features_tab(self):
        """Create the AI features tab"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="🤖 AI Features")
        
        # Main container
        main_container = tk.Frame(ai_frame, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text="🤖 AI-Powered Financial Intelligence",
                               font=('Segoe UI', 20, 'bold'),
                               fg=self.colors['white'],
                               bg=self.colors['primary'])
        header_label.pack(expand=True)
        
        # Create grid of AI feature cards
        features_frame = tk.Frame(main_container, bg=self.colors['light'])
        features_frame.pack(fill='both', expand=True)
        
        # Row 1: Dashboard and AI Insights
        row1_frame = tk.Frame(features_frame, bg=self.colors['light'])
        row1_frame.pack(fill='x', pady=(0, 20))
        
        # Real-time Dashboard Card
        dashboard_card = self.create_ai_feature_card(
            row1_frame,
            "📊 Real-time Dashboard",
            "Live analytics and interactive visualizations",
            "Open live dashboard with real-time charts, spending trends, and financial health metrics",
            self.open_dashboard,
            self.colors['secondary']
        )
        dashboard_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # AI Insights Card
        insights_card = self.create_ai_feature_card(
            row1_frame,
            "🧠 AI Financial Insights",
            "Smart analysis and recommendations",
            "Get AI-powered spending analysis, pattern detection, and personalized recommendations",
            self.show_ai_insights,
            self.colors['accent']
        )
        insights_card.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        # Row 2: Categorization and Predictions
        row2_frame = tk.Frame(features_frame, bg=self.colors['light'])
        row2_frame.pack(fill='x', pady=(0, 20))
        
        # Smart Categorization Card
        categorization_card = self.create_ai_feature_card(
            row2_frame,
            "🏷️ Smart Categorization",
            "Automatic expense categorization",
            "AI learns from your spending habits to automatically categorize new expenses",
            self.show_categorization_settings,
            self.colors['success']
        )
        categorization_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Prediction Card
        prediction_card = self.create_ai_feature_card(
            row2_frame,
            "🔮 Spending Predictions",
            "Future spending forecasts",
            "Predict future spending patterns and budget requirements using machine learning",
            self.show_predictions,
            self.colors['warning']
        )
        prediction_card.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        # Row 3: Anomaly Detection and Reports
        row3_frame = tk.Frame(features_frame, bg=self.colors['light'])
        row3_frame.pack(fill='x')
        
        # Anomaly Detection Card
        anomaly_card = self.create_ai_feature_card(
            row3_frame,
            "⚠️ Anomaly Detection",
            "Unusual spending alerts",
            "Detect unusual spending patterns and get alerts for potential budget overruns",
            self.show_anomalies,
            self.colors['danger']
        )
        anomaly_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Smart Reports Card
        reports_card = self.create_ai_feature_card(
            row3_frame,
            "📈 Smart Reports",
            "Intelligent financial reports",
            "Generate comprehensive financial reports with AI insights and recommendations",
            self.generate_smart_report,
            self.colors['info']
        )
        reports_card.pack(side='left', fill='both', expand=True, padx=(10, 0))
    
    def create_ai_feature_card(self, parent, title, subtitle, description, command, color):
        """Create a modern AI feature card"""
        # Main card frame
        card_frame = tk.Frame(parent, bg=self.colors['white'], relief='raised', bd=2)
        
        # Header with color
        header_frame = tk.Frame(card_frame, bg=color, height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title and subtitle
        title_label = tk.Label(header_frame,
                              text=title,
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['white'],
                              bg=color)
        title_label.pack(pady=(10, 0))
        
        subtitle_label = tk.Label(header_frame,
                                 text=subtitle,
                                 font=('Segoe UI', 10),
                                 fg=self.colors['light'],
                                 bg=color)
        subtitle_label.pack()
        
        # Content area
        content_frame = tk.Frame(card_frame, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Description
        desc_label = tk.Label(content_frame,
                             text=description,
                             font=('Segoe UI', 11),
                             fg=self.colors['dark'],
                             bg=self.colors['white'],
                             wraplength=250,
                             justify='left')
        desc_label.pack(pady=(0, 15))
        
        # Action button
        action_btn = tk.Button(content_frame,
                              text="Launch Feature",
                              command=command,
                              bg=color,
                              fg=self.colors['white'],
                              font=('Segoe UI', 11, 'bold'),
                              relief='flat',
                              cursor='hand2',
                              padx=20,
                              pady=8)
        action_btn.pack()
        
        return card_frame
    
    def get_expense_data(self):
        """Get expense data for AI analysis and dashboard"""
        return self.expenses.copy()
    
    def open_dashboard(self):
        """Open the real-time dashboard"""
        if self.dashboard:
            self.dashboard.open_dashboard()
        else:
            messagebox.showinfo("Info", "Real-time dashboard not available. Please install required dependencies.")
    
    def show_ai_insights(self):
        """Show AI financial insights"""
        if not self.financial_ai:
            messagebox.showinfo("Info", "AI insights not available. Please install required dependencies.")
            return
        
        if not self.expenses:
            messagebox.showinfo("Info", "No expense data available for analysis.")
            return
        
        # Create insights window
        insights_window = tk.Toplevel(self.root)
        insights_window.title("🧠 AI Financial Insights")
        insights_window.geometry("800x600")
        insights_window.configure(bg=self.colors['light'])
        
        # Header
        header_frame = tk.Frame(insights_window, bg=self.colors['accent'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text="🧠 AI Financial Insights",
                               font=('Segoe UI', 18, 'bold'),
                               fg=self.colors['white'],
                               bg=self.colors['accent'])
        header_label.pack(expand=True)
        
        # Loading label
        loading_label = tk.Label(insights_window,
                                text="🔄 Analyzing your financial data...",
                                font=('Segoe UI', 14),
                                fg=self.colors['dark'],
                                bg=self.colors['light'])
        loading_label.pack(expand=True)
        
        # Generate insights in background
        def generate_insights():
            try:
                insights = self.financial_ai.analyze_spending_patterns(self.expenses)
                
                # Update UI with insights
                insights_window.after(0, lambda: self.display_insights(insights_window, insights, loading_label))
            except Exception as e:
                insights_window.after(0, lambda: loading_label.config(text=f"Error generating insights: {str(e)}"))
        
        # Start analysis in background thread
        threading.Thread(target=generate_insights, daemon=True).start()
    
    def display_insights(self, window, insights, loading_label):
        """Display the AI insights in the window"""
        # Remove loading label
        loading_label.destroy()
        
        # Create scrollable text area
        text_frame = tk.Frame(window, bg=self.colors['light'])
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Text widget with scrollbar
        text_widget = tk.Text(text_frame,
                             wrap=tk.WORD,
                             font=('Segoe UI', 11),
                             bg=self.colors['white'],
                             fg=self.colors['dark'],
                             padx=20,
                             pady=20)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Format and display insights
        formatted_text = self.format_insights_text(insights)
        text_widget.insert(tk.END, formatted_text)
        text_widget.config(state=tk.DISABLED)
    
    def format_insights_text(self, insights):
        """Format insights for display"""
        if insights.get('status') != 'success':
            return f"Unable to generate insights: {insights.get('message', 'Unknown error')}"
        
        text = "🧠 AI FINANCIAL INSIGHTS REPORT\n"
        text += "=" * 50 + "\n\n"
        
        # Analysis period
        if 'data_period' in insights:
            period = insights['data_period']
            text += f"📊 Analysis Period: {period.get('start_date')} to {period.get('end_date')}\n"
            text += f"📈 Total Transactions: {period.get('total_transactions', 0)}\n\n"
        
        # Spending summary
        if 'spending_summary' in insights:
            summary = insights['spending_summary']
            text += "💰 SPENDING SUMMARY\n"
            text += f"• Total Spending: ₹{summary.get('total_spending', 0):,.2f}\n"
            text += f"• Daily Average: ₹{summary.get('average_daily', 0):,.2f}\n"
            text += f"• Average Transaction: ₹{summary.get('average_transaction', 0):,.2f}\n"
            text += f"• Largest Transaction: ₹{summary.get('largest_transaction', 0):,.2f}\n\n"
        
        # Financial health
        if 'financial_health' in insights:
            health = insights['financial_health']
            score = health.get('overall_score', 0)
            status = health.get('status', 'unknown')
            text += f"🏥 FINANCIAL HEALTH SCORE: {score:.0f}/100 ({status.upper()})\n\n"
        
        # Recommendations
        if 'recommendations' in insights and insights['recommendations']:
            text += "💡 AI RECOMMENDATIONS\n"
            for i, rec in enumerate(insights['recommendations'], 1):
                priority = rec.get('priority', 'medium').upper()
                text += f"{i}. [{priority}] {rec.get('title', 'Recommendation')}\n"
                text += f"   {rec.get('message', 'No details available')}\n"
                if 'action' in rec:
                    text += f"   Action: {rec['action']}\n"
                text += "\n"
        
        # Anomalies
        if 'anomalies' in insights and insights['anomalies'].get('status') != 'insufficient_data':
            anomalies = insights['anomalies']
            text += "⚠️ SPENDING ANOMALIES\n"
            if 'transaction_outliers' in anomalies:
                outliers = anomalies['transaction_outliers']
                text += f"• High-value transactions: {outliers.get('high_value_transactions', 0)}\n"
                if 'largest_transaction' in outliers:
                    largest = outliers['largest_transaction']
                    text += f"• Largest: ₹{largest.get('amount', 0):,.2f} on {largest.get('date', 'unknown')}\n"
            text += "\n"
        
        text += "Generated by AI Financial Intelligence Engine\n"
        text += f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return text
    
    def show_categorization_settings(self):
        """Show AI categorization settings and statistics"""
        if not self.ai_categorizer:
            messagebox.showinfo("Info", "AI categorization not available.")
            return
        
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("🏷️ Smart Categorization Settings")
        settings_window.geometry("600x500")
        settings_window.configure(bg=self.colors['light'])
        
        # Header
        header_frame = tk.Frame(settings_window, bg=self.colors['success'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text="🏷️ Smart Categorization Settings",
                               font=('Segoe UI', 16, 'bold'),
                               fg=self.colors['white'],
                               bg=self.colors['success'])
        header_label.pack(expand=True)
        
        # Content frame
        content_frame = tk.Frame(settings_window, bg=self.colors['light'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Statistics
        stats_text = tk.Text(content_frame,
                            height=15,
                            wrap=tk.WORD,
                            font=('Segoe UI', 11),
                            bg=self.colors['white'],
                            padx=15,
                            pady=15)
        stats_text.pack(fill='both', expand=True)
        
        # Generate statistics
        stats_info = "🏷️ SMART CATEGORIZATION STATUS\n"
        stats_info += "=" * 40 + "\n\n"
        stats_info += "✅ AI Categorization: ACTIVE\n"
        stats_info += "📊 Learning Mode: Enabled\n"
        stats_info += "🎯 Accuracy: Improving with each transaction\n\n"
        stats_info += "FEATURES:\n"
        stats_info += "• Machine Learning categorization\n"
        stats_info += "• Keyword-based fallback system\n"
        stats_info += "• User feedback learning\n"
        stats_info += "• Continuous improvement\n\n"
        stats_info += "HOW IT WORKS:\n"
        stats_info += "1. AI analyzes expense description and amount\n"
        stats_info += "2. Suggests most likely category\n"
        stats_info += "3. Learns from your feedback\n"
        stats_info += "4. Improves accuracy over time\n\n"
        stats_info += "CATEGORIES AVAILABLE:\n"
        categories = ["Food", "Transportation", "Entertainment", "Shopping", 
                     "Bills", "Healthcare", "Education", "Other"]
        for cat in categories:
            stats_info += f"• {cat}\n"
        
        stats_text.insert(tk.END, stats_info)
        stats_text.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = tk.Frame(content_frame, bg=self.colors['light'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        retrain_btn = tk.Button(button_frame,
                               text="🔄 Retrain AI Model",
                               command=self.retrain_ai_model,
                               bg=self.colors['success'],
                               fg=self.colors['white'],
                               font=('Segoe UI', 11, 'bold'),
                               relief='flat',
                               padx=20,
                               pady=8)
        retrain_btn.pack(side='left', padx=(0, 10))
        
        test_btn = tk.Button(button_frame,
                            text="🧪 Test Categorization",
                            command=self.test_categorization,
                            bg=self.colors['info'],
                            fg=self.colors['white'],
                            font=('Segoe UI', 11, 'bold'),
                            relief='flat',
                            padx=20,
                            pady=8)
        test_btn.pack(side='left')
    
    def show_predictions(self):
        """Show spending predictions"""
        messagebox.showinfo("🔮 Predictions", "Spending predictions feature coming soon!\n\nThis will include:\n• Next week spending forecast\n• Monthly budget recommendations\n• Category-wise predictions\n• Budget alerts")
    
    def show_anomalies(self):
        """Show anomaly detection results"""
        messagebox.showinfo("⚠️ Anomalies", "Anomaly detection feature coming soon!\n\nThis will include:\n• Unusual spending alerts\n• Budget overrun warnings\n• Irregular pattern detection\n• Smart notifications")
    
    def generate_smart_report(self):
        """Generate AI-powered smart report"""
        messagebox.showinfo("📈 Smart Reports", "Smart reports feature coming soon!\n\nThis will include:\n• PDF financial reports\n• Excel export with insights\n• Trend analysis\n• Personalized recommendations")
    
    def retrain_ai_model(self):
        """Retrain the AI categorization model"""
        if not self.ai_categorizer:
            return
        
        try:
            # Train on existing data
            training_data = [(exp['description'], exp['amount'], exp['category']) for exp in self.expenses]
            
            if training_data:
                self.ai_categorizer.train_model(training_data)
                messagebox.showinfo("✅ Success", f"AI model retrained with {len(training_data)} transactions!")
            else:
                messagebox.showinfo("ℹ️ Info", "No training data available. Add some expenses first.")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to retrain model: {str(e)}")
    
    def test_categorization(self):
        """Test the AI categorization with user input"""
        if not self.ai_categorizer:
            return
        
        # Create test dialog
        test_window = tk.Toplevel(self.root)
        test_window.title("🧪 Test AI Categorization")
        test_window.geometry("500x300")
        test_window.configure(bg=self.colors['light'])
        
        # Input fields
        tk.Label(test_window, text="Test Description:", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['light']).pack(pady=10)
        
        desc_entry = tk.Entry(test_window, font=('Segoe UI', 12), width=40)
        desc_entry.pack(pady=5)
        desc_entry.insert(0, "Coffee at Starbucks")
        
        tk.Label(test_window, text="Test Amount:", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['light']).pack(pady=(20, 10))
        
        amount_entry = tk.Entry(test_window, font=('Segoe UI', 12), width=20)
        amount_entry.pack(pady=5)
        amount_entry.insert(0, "250")
        
        # Result area
        result_label = tk.Label(test_window, text="", 
                               font=('Segoe UI', 12),
                               bg=self.colors['light'],
                               wraplength=450)
        result_label.pack(pady=20)
        
        def run_test():
            try:
                description = desc_entry.get()
                amount = float(amount_entry.get())
                
                predicted_category = self.ai_categorizer.smart_categorize(description, amount)
                
                result_text = f"🤖 AI Prediction: {predicted_category}\n\n"
                result_text += f"Input: '{description}' - ₹{amount}"
                
                result_label.config(text=result_text, fg=self.colors['success'])
            except Exception as e:
                result_label.config(text=f"Error: {str(e)}", fg=self.colors['danger'])
        
        test_btn = tk.Button(test_window,
                            text="🧪 Test Categorization",
                            command=run_test,
                            bg=self.colors['info'],
                            fg=self.colors['white'],
                            font=('Segoe UI', 12, 'bold'),
                            relief='flat',
                            padx=20,
                            pady=8)
        test_btn.pack(pady=10)
    
    def create_ai_suggestions_panel(self):
        """Create a prominent AI suggestions panel in the main interface"""
        # Create collapsible AI suggestions frame
        self.ai_panel = tk.Frame(self.main_frame, bg=self.colors['primary'], relief='raised', bd=2)
        self.ai_panel.pack(fill='x', padx=10, pady=(10, 5))
        
        # Header with toggle button
        header_frame = tk.Frame(self.ai_panel, bg=self.colors['primary'])
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # AI icon and title
        title_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        title_frame.pack(side='left', fill='x', expand=True)
        
        self.ai_title = tk.Label(title_frame, 
                                text="🤖 AI Financial Assistant",
                                font=('Segoe UI', 12, 'bold'),
                                fg=self.colors['white'],
                                bg=self.colors['primary'])
        self.ai_title.pack(side='left')
        
        # Live indicator
        self.ai_status = tk.Label(title_frame,
                                 text="🟢 LIVE",
                                 font=('Segoe UI', 9, 'bold'),
                                 fg='#00ff00',
                                 bg=self.colors['primary'])
        self.ai_status.pack(side='left', padx=(10, 0))
        
        # Toggle button
        self.ai_expanded = tk.BooleanVar(value=True)
        self.toggle_btn = tk.Button(header_frame,
                                   text="▼",
                                   command=self.toggle_ai_panel,
                                   bg=self.colors['secondary'],
                                   fg=self.colors['white'],
                                   font=('Segoe UI', 10, 'bold'),
                                   width=3,
                                   relief='flat')
        self.toggle_btn.pack(side='right')
        
        # Content frame (collapsible)
        self.ai_content = tk.Frame(self.ai_panel, bg=self.colors['white'])
        self.ai_content.pack(fill='x', padx=10, pady=(0, 10))
        
        # Create suggestion cards container
        self.suggestions_container = tk.Frame(self.ai_content, bg=self.colors['white'])
        self.suggestions_container.pack(fill='x', pady=10)
        
        # Quick stats row
        self.quick_stats_frame = tk.Frame(self.ai_content, bg=self.colors['white'])
        self.quick_stats_frame.pack(fill='x', pady=(0, 10))
        
        # Initialize with loading state
        self.update_ai_suggestions()
        
        # Auto-refresh suggestions every 30 seconds
        self.schedule_ai_updates()
    
    def toggle_ai_panel(self):
        """Toggle the AI panel visibility"""
        if self.ai_expanded.get():
            self.ai_content.pack_forget()
            self.toggle_btn.config(text="▶")
            self.ai_expanded.set(False)
        else:
            self.ai_content.pack(fill='x', padx=10, pady=(0, 10))
            self.toggle_btn.config(text="▼")
            self.ai_expanded.set(True)
    
    def update_ai_suggestions(self):
        """Update the AI suggestions panel with live recommendations"""
        if not AI_FEATURES_AVAILABLE or not hasattr(self, 'suggestions_container'):
            return
        
        # Clear existing suggestions
        for widget in self.suggestions_container.winfo_children():
            widget.destroy()
        
        for widget in self.quick_stats_frame.winfo_children():
            widget.destroy()
        
        try:
            # Show loading state
            loading_label = tk.Label(self.suggestions_container,
                                   text="🔄 Analyzing your spending...",
                                   font=('Segoe UI', 10),
                                   fg=self.colors['info'],
                                   bg=self.colors['white'])
            loading_label.pack(pady=10)
            
            # Generate suggestions in background
            def generate_live_suggestions():
                try:
                    if not self.expenses:
                        suggestions = self.get_welcome_suggestions()
                    else:
                        # Get AI insights
                        insights = self.financial_ai.analyze_spending_patterns(self.expenses)
                        suggestions = self.extract_actionable_suggestions(insights)
                    
                    # Update UI on main thread
                    self.root.after(0, lambda: self.display_live_suggestions(suggestions))
                except Exception as e:
                    self.root.after(0, lambda: self.display_suggestion_error(str(e)))
            
            # Start analysis in background
            threading.Thread(target=generate_live_suggestions, daemon=True).start()
            
        except Exception as e:
            self.display_suggestion_error(str(e))
    
    def get_welcome_suggestions(self):
        """Get welcome suggestions for new users"""
        return [
            {
                'type': 'welcome',
                'title': '👋 Welcome to AI-Powered Expense Tracking!',
                'message': 'Start by adding a few expenses to unlock personalized insights.',
                'action': 'Add your first expense',
                'priority': 'info',
                'icon': '🚀'
            },
            {
                'type': 'tip',
                'title': '💡 Smart Categorization Ready',
                'message': 'AI will automatically suggest categories for your expenses.',
                'action': 'Learn more',
                'priority': 'info',
                'icon': '🏷️'
            }
        ]
    
    def extract_actionable_suggestions(self, insights):
        """Extract actionable suggestions from AI insights"""
        suggestions = []
        
        if insights.get('status') != 'success':
            return [{
                'type': 'error',
                'title': '⚠️ Analysis Unavailable',
                'message': 'Unable to generate insights. Please check your data.',
                'priority': 'warning',
                'icon': '⚠️'
            }]
        
        # Add financial health score as first suggestion
        if 'financial_health' in insights:
            health = insights['financial_health']
            score = health.get('overall_score', 0)
            status = health.get('status', 'unknown')
            
            if score >= 80:
                icon = '🟢'
                priority = 'success'
                title = f'Excellent Financial Health! ({score:.0f}/100)'
            elif score >= 60:
                icon = '🟡'
                priority = 'warning'
                title = f'Good Financial Health ({score:.0f}/100)'
            else:
                icon = '🔴'
                priority = 'danger'
                title = f'Financial Health Needs Attention ({score:.0f}/100)'
            
            suggestions.append({
                'type': 'health',
                'title': title,
                'message': f'Your spending pattern is {status}. Click to see improvement tips.',
                'action': 'View Details',
                'priority': priority,
                'icon': icon
            })
        
        # Add top recommendations
        if 'recommendations' in insights and insights['recommendations']:
            for rec in insights['recommendations'][:2]:  # Show top 2 recommendations
                priority_map = {'high': 'danger', 'medium': 'warning', 'low': 'info'}
                icon_map = {'high': '🚨', 'medium': '💡', 'low': 'ℹ️'}
                
                rec_priority = rec.get('priority', 'medium').lower()
                suggestions.append({
                    'type': 'recommendation',
                    'title': rec.get('title', 'AI Recommendation'),
                    'message': rec.get('message', 'No details available'),
                    'action': rec.get('action', 'Learn More'),
                    'priority': priority_map.get(rec_priority, 'info'),
                    'icon': icon_map.get(rec_priority, '💡')
                })
        
        # Add spending anomaly alert
        if 'anomalies' in insights and insights['anomalies'].get('status') != 'insufficient_data':
            anomalies = insights['anomalies']
            if 'transaction_outliers' in anomalies:
                outliers = anomalies['transaction_outliers']
                high_value = outliers.get('high_value_transactions', 0)
                if high_value > 0:
                    suggestions.append({
                        'type': 'anomaly',
                        'title': f'🔍 {high_value} Unusual Transaction(s) Detected',
                        'message': 'Some expenses seem higher than usual. Review them for accuracy.',
                        'action': 'Review Transactions',
                        'priority': 'warning',
                        'icon': '⚠️'
                    })
        
        # Add spending trend alert
        if 'spending_trends' in insights:
            trends = insights['spending_trends']
            if 'daily_trend' in trends:
                trend = trends['daily_trend'].get('trend_direction', 'stable')
                if trend == 'increasing':
                    suggestions.append({
                        'type': 'trend',
                        'title': '📈 Spending Trend: Increasing',
                        'message': 'Your daily spending has been increasing. Consider reviewing your budget.',
                        'action': 'View Trends',
                        'priority': 'warning',
                        'icon': '📈'
                    })
        
        return suggestions
    
    def display_live_suggestions(self, suggestions):
        """Display the live suggestions in the panel"""
        # Clear loading state
        for widget in self.suggestions_container.winfo_children():
            widget.destroy()
        
        if not suggestions:
            no_suggestions = tk.Label(self.suggestions_container,
                                     text="✅ All good! No urgent suggestions at the moment.",
                                     font=('Segoe UI', 10),
                                     fg=self.colors['success'],
                                     bg=self.colors['white'])
            no_suggestions.pack(pady=10)
            return
        
        # Display each suggestion as a card
        for i, suggestion in enumerate(suggestions):
            self.create_suggestion_card(self.suggestions_container, suggestion, i)
        
        # Add quick stats
        self.display_quick_stats()
    
    def create_suggestion_card(self, parent, suggestion, index):
        """Create a suggestion card widget"""
        # Color mapping for priorities
        color_map = {
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'success': '#27ae60',
            'info': '#3498db'
        }
        
        bg_color_map = {
            'danger': '#fdf2f2',
            'warning': '#fef9e7',
            'success': '#f0f9f4',
            'info': '#eff8ff'
        }
        
        priority = suggestion.get('priority', 'info')
        accent_color = color_map.get(priority, '#3498db')
        bg_color = bg_color_map.get(priority, '#eff8ff')
        
        # Card frame
        card_frame = tk.Frame(parent, bg=bg_color, relief='solid', bd=1)
        card_frame.pack(fill='x', padx=5, pady=2)
        
        # Left accent bar
        accent_bar = tk.Frame(card_frame, bg=accent_color, width=4)
        accent_bar.pack(side='left', fill='y')
        
        # Content frame
        content_frame = tk.Frame(card_frame, bg=bg_color)
        content_frame.pack(side='left', fill='both', expand=True, padx=10, pady=8)
        
        # Title with icon
        title_frame = tk.Frame(content_frame, bg=bg_color)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(title_frame,
                              text=f"{suggestion.get('icon', '💡')} {suggestion.get('title', 'Suggestion')}",
                              font=('Segoe UI', 10, 'bold'),
                              fg=accent_color,
                              bg=bg_color,
                              anchor='w')
        title_label.pack(side='left', fill='x', expand=True)
        
        # Message
        message_label = tk.Label(content_frame,
                                text=suggestion.get('message', ''),
                                font=('Segoe UI', 9),
                                fg=self.colors['dark'],
                                bg=bg_color,
                                anchor='w',
                                wraplength=400)
        message_label.pack(fill='x', pady=(2, 0))
        
        # Action button (if applicable)
        action = suggestion.get('action')
        if action and action not in ['Learn More', 'Learn more']:
            action_btn = tk.Button(content_frame,
                                  text=f"→ {action}",
                                  command=lambda: self.handle_suggestion_action(suggestion),
                                  bg=accent_color,
                                  fg='white',
                                  font=('Segoe UI', 8, 'bold'),
                                  relief='flat',
                                  padx=10)
            action_btn.pack(anchor='w', pady=(5, 0))
    
    def handle_suggestion_action(self, suggestion):
        """Handle suggestion action clicks"""
        suggestion_type = suggestion.get('type', '')
        
        if suggestion_type == 'health':
            self.show_ai_insights()
        elif suggestion_type == 'recommendation':
            self.show_ai_insights()
        elif suggestion_type == 'anomaly':
            # Filter transactions to show only high-value ones
            self.filter_high_value_transactions()
        elif suggestion_type == 'trend':
            self.open_dashboard()
        else:
            # Default action - show insights
            self.show_ai_insights()
    
    def filter_high_value_transactions(self):
        """Filter and highlight high-value transactions"""
        if not self.expenses:
            return
        
        # Calculate average transaction amount
        amounts = [float(expense['amount']) for expense in self.expenses]
        avg_amount = statistics.mean(amounts)
        threshold = avg_amount * 2  # Transactions 2x above average
        
        # Filter tree view to show only high-value transactions
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        high_value_count = 0
        for expense in self.expenses:
            if float(expense['amount']) > threshold:
                amount_color = 'red' if float(expense['amount']) > threshold * 1.5 else 'orange'
                item = self.tree.insert('', 'end', values=(
                    expense['date'],
                    expense['category'],
                    expense['description'],
                    f"₹{float(expense['amount']):.2f}"
                ))
                # Highlight high-value transactions
                self.tree.set(item, 'amount', f"⚠️ ₹{float(expense['amount']):.2f}")
                high_value_count += 1
        
        # Show message about filtering
        messagebox.showinfo("High-Value Transactions", 
                           f"Showing {high_value_count} transactions above ₹{threshold:.0f}\n\n"
                           f"Click 'Refresh' to show all transactions again.")
    
    def display_quick_stats(self):
        """Display quick financial stats"""
        if not self.expenses:
            return
        
        try:
            # Calculate quick stats
            total_spending = sum(float(expense['amount']) for expense in self.expenses)
            transaction_count = len(self.expenses)
            avg_transaction = total_spending / transaction_count if transaction_count > 0 else 0
            
            # This month's spending
            current_month = datetime.now().replace(day=1)
            this_month_expenses = [
                expense for expense in self.expenses 
                if datetime.strptime(expense['date'], '%Y-%m-%d') >= current_month
            ]
            this_month_total = sum(float(expense['amount']) for expense in this_month_expenses)
            
            # Create stats cards
            stats_data = [
                ('💰', 'Total Spent', f'₹{total_spending:,.0f}'),
                ('📊', 'This Month', f'₹{this_month_total:,.0f}'),
                ('🧮', 'Avg Transaction', f'₹{avg_transaction:,.0f}'),
                ('📈', 'Total Transactions', f'{transaction_count}')
            ]
            
            for icon, label, value in stats_data:
                stat_frame = tk.Frame(self.quick_stats_frame, bg='#f8f9fa', relief='solid', bd=1)
                stat_frame.pack(side='left', fill='both', expand=True, padx=2, pady=2)
                
                # Icon
                icon_label = tk.Label(stat_frame, text=icon, font=('Segoe UI', 16), 
                                     bg='#f8f9fa', fg=self.colors['primary'])
                icon_label.pack(pady=(5, 0))
                
                # Value
                value_label = tk.Label(stat_frame, text=value, font=('Segoe UI', 10, 'bold'),
                                      bg='#f8f9fa', fg=self.colors['dark'])
                value_label.pack()
                
                # Label
                label_label = tk.Label(stat_frame, text=label, font=('Segoe UI', 8),
                                      bg='#f8f9fa', fg='gray')
                label_label.pack(pady=(0, 5))
        
        except Exception as e:
            print(f"Error displaying quick stats: {e}")
    
    def display_suggestion_error(self, error_msg):
        """Display error in suggestions panel"""
        for widget in self.suggestions_container.winfo_children():
            widget.destroy()
        
        error_label = tk.Label(self.suggestions_container,
                              text=f"⚠️ Unable to generate suggestions: {error_msg}",
                              font=('Segoe UI', 10),
                              fg=self.colors['danger'],
                              bg=self.colors['white'])
        error_label.pack(pady=10)
    
    def schedule_ai_updates(self):
        """Schedule periodic AI suggestion updates"""
        # Update suggestions every 30 seconds
        self.root.after(30000, self.auto_update_suggestions)
    
    def auto_update_suggestions(self):
        """Auto-update suggestions periodically"""
        if hasattr(self, 'ai_panel') and self.ai_panel.winfo_exists():
            self.update_ai_suggestions()
            self.schedule_ai_updates()  # Schedule next update
    
    def show_urgent_ai_notification(self, suggestion):
        """Show urgent AI notifications as popup banners"""
        if suggestion.get('priority') not in ['danger', 'warning']:
            return
        
        # Create notification banner
        banner = tk.Toplevel(self.root)
        banner.title("🚨 AI Alert")
        banner.geometry("400x150")
        banner.resizable(False, False)
        banner.configure(bg=self.colors['danger'])
        
        # Position in top-right corner
        banner.geometry("+{}+{}".format(
            self.root.winfo_x() + self.root.winfo_width() - 420,
            self.root.winfo_y() + 50
        ))
        
        # Make it stay on top
        banner.attributes('-topmost', True)
        
        # Content
        content_frame = tk.Frame(banner, bg=self.colors['danger'])
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title
        title_label = tk.Label(content_frame,
                              text=f"{suggestion.get('icon', '🚨')} {suggestion.get('title', 'AI Alert')}",
                              font=('Segoe UI', 12, 'bold'),
                              fg='white',
                              bg=self.colors['danger'])
        title_label.pack(anchor='w')
        
        # Message
        message_label = tk.Label(content_frame,
                                text=suggestion.get('message', ''),
                                font=('Segoe UI', 10),
                                fg='white',
                                bg=self.colors['danger'],
                                wraplength=350,
                                justify='left')
        message_label.pack(anchor='w', pady=(5, 10))
        
        # Buttons
        btn_frame = tk.Frame(content_frame, bg=self.colors['danger'])
        btn_frame.pack(fill='x')
        
        action_btn = tk.Button(btn_frame,
                              text=suggestion.get('action', 'View Details'),
                              command=lambda: [self.handle_suggestion_action(suggestion), banner.destroy()],
                              bg='white',
                              fg=self.colors['danger'],
                              font=('Segoe UI', 9, 'bold'),
                              relief='flat',
                              padx=15)
        action_btn.pack(side='left')
        
        dismiss_btn = tk.Button(btn_frame,
                               text="Dismiss",
                               command=banner.destroy,
                               bg=self.colors['white'],
                               fg=self.colors['dark'],
                               font=('Segoe UI', 9),
                               relief='flat',
                               padx=15)
        dismiss_btn.pack(side='right')
        
        # Auto-dismiss after 10 seconds
        banner.after(10000, banner.destroy)
    
    def check_for_urgent_alerts(self):
        """Check for urgent AI alerts and show notifications"""
        if not AI_FEATURES_AVAILABLE or not self.expenses:
            return
        
        try:
            # Quick analysis for urgent alerts
            insights = self.financial_ai.analyze_spending_patterns(self.expenses)
            suggestions = self.extract_actionable_suggestions(insights)
            
            for suggestion in suggestions:
                if suggestion.get('priority') == 'danger':
                    self.show_urgent_ai_notification(suggestion)
                    break  # Show only one urgent notification at a time
                    
        except Exception as e:
            print(f"Error checking urgent alerts: {e}")

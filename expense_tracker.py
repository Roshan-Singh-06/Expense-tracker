
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
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(main_container)
        
        # Create notebook for tabs with modern styling
        self.notebook = ttk.Notebook(main_container, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, pady=(20, 0))
        
        # Create tabs
        self.create_add_expense_tab()
        self.create_view_expenses_tab()
        self.create_analytics_tab()
        
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
        """Add a new expense with enhanced validation"""
        try:
            # Validate inputs
            if not self.amount_var.get() or not self.category_var.get():
                messagebox.showerror("❌ Error", "Please fill in amount and category")
                return
            
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("❌ Error", "Amount must be positive")
                return
            
            # Clean category (remove emoji)
            category = self.category_var.get()
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
                "description": self.description_var.get() or "No description",
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
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", alpha=0.8))

  
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

def main():
    """Main function to run the expense tracker"""
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()

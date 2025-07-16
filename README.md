# Expense Tracker

A simple and intuitive expense tracking application built with Python Tkinter that helps you manage your daily expenses with categorization and visualization.

## Features

### 📊 Core Functionality
- **Add Expenses**: Record daily expenses with amount, category, date, and description
- **View Transactions**: Browse all past expenses with filtering and sorting options
- **Data Persistence**: All data is automatically saved to a JSON file
- **Delete Expenses**: Remove unwanted expense entries

### 🎯 Categorization
- Pre-defined categories: Food, Transportation, Entertainment, Shopping, Bills, Healthcare, Education, Other
- Filter expenses by category
- Category-wise expense analysis

### 📈 Sorting Options
- Date (Recent to Oldest)
- Date (Oldest to Recent)
- Amount (High to Low)
- Amount (Low to High)
- Category (Alphabetical)

### 📊 Analytics & Visualization
- **Daily Expense Chart**: Bar chart showing daily spending for the month
- **Category Distribution**: Pie chart showing expense breakdown by category
- **Weekly Trends**: Line chart displaying weekly spending patterns
- **Category Comparison**: Horizontal bar chart of top spending categories
- **Monthly Summary Stats**: Key metrics and insights
- **Monthly Reports**: View expenses for any specific month
- **Interactive Charts**: Zoom, pan, and navigate through visualizations

### 🔔 Smart Notifications
- **Toast Notifications**: In-app popup notifications with different types (success, warning, error, info)
- **System Notifications**: OS-level notifications that appear in system tray
- **Budget Alerts**: Automatic notifications when daily spending exceeds set budget
- **Achievement Notifications**: Milestone celebrations for transaction counts and spending amounts
- **Weekly Summaries**: Automatic weekly spending reports
- **Real-time Feedback**: Instant notifications for all user actions
- **Customizable Settings**: Enable/disable notifications and set daily budget limits

### 💡 User Interface
- **Tabbed Interface**: Organized into Add Expense, View Expenses, and Analytics tabs
- **Recent Expenses Preview**: Quick view of latest transactions
- **Summary Statistics**: Total expenses and transaction count
- **Modern Design**: Clean and intuitive user interface with professional styling
- **Responsive Layout**: Adapts to different window sizes
- **Toast Notifications**: Beautiful in-app notifications for user feedback
- **Dark Theme Elements**: Modern color scheme with gradient effects
- **Interactive Elements**: Hover effects and smooth animations

## Installation

1. **Clone or Download** this project to your local machine

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python expense_tracker.py
   ```

## Requirements

- Python 3.7 or higher
- matplotlib 3.7.2
- numpy 1.24.3
- seaborn 0.12.2 (for enhanced visualizations)
- plyer 2.1.0 (for system notifications)
- tkinter (usually included with Python)

## Usage

### Adding Expenses
1. Open the "Add Expense" tab
2. Enter the date (defaults to today)
3. Input the amount in rupees
4. Select a category from the dropdown
5. Add an optional description
6. Click "Add Expense"

### Viewing Expenses
1. Go to the "View Expenses" tab
2. Use the sort dropdown to organize expenses
3. Filter by category using the category dropdown
4. Select any expense and click "Delete Selected" to remove it

### Analytics
1. Navigate to the "Analytics" tab
2. View the current month's spending patterns
3. Change the month field (YYYY-MM format) to view different months
4. Click "Refresh Charts" to update the visualizations
5. Use "Export Data" to save your expenses as CSV

### Notifications
1. Click the 🔔 button in the header to access notification settings
2. Enable/disable notifications as needed
3. Set your daily budget for automatic alerts
4. Test notifications to ensure they're working
5. Receive automatic weekly summaries and achievement notifications

## Data Storage

- All expense data is stored in `expenses.json` in the same directory as the application
- The JSON file is created automatically when you first add an expense
- Data includes: date, amount, category, description, and timestamp

## File Structure

```
expense-tracker/
│
├── expense_tracker.py    # Main application file
├── requirements.txt      # Python dependencies
├── expenses.json        # Data storage (created automatically)
└── README.md           # This file
```

## Features Breakdown

### Add Expense Tab
- Date picker (defaults to current date)
- Amount input with validation
- Category selection dropdown
- Description field
- Recent expenses preview
- Form validation and error handling

### View Expenses Tab
- Complete transaction history
- Multiple sorting options
- Category filtering
- Delete functionality
- Summary statistics (total amount and count)

### Analytics Tab
- Daily spending bar chart
- Category-wise pie chart
- Weekly trend line chart
- Month selection capability
- Visual insights into spending patterns

## Tips for Use

1. **Regular Updates**: Add expenses daily for the most accurate tracking
2. **Consistent Categories**: Use the same categories consistently for better analysis
3. **Descriptive Notes**: Add meaningful descriptions to remember what each expense was for
4. **Monthly Reviews**: Use the analytics tab to review your spending patterns each month
5. **Backup**: Periodically backup your `expenses.json` file

## Troubleshooting

- **Application won't start**: Make sure all dependencies are installed
- **Charts not displaying**: Ensure matplotlib is properly installed
- **Data not saving**: Check file permissions in the application directory

## Future Enhancements

Potential features for future versions:
- Budget setting and tracking
- Export to CSV/Excel
- Income tracking
- Multiple currency support
- Data import/export
- Advanced filtering options
- Expense forecasting

---

**Note**: This application stores data locally in a JSON file. Make sure to backup your `expenses.json` file regularly to prevent data loss.

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
from tkinter import *
from tkinter import ttk, messagebox
import tkinter as tk

class ExpenseTracker:
    def __init__(self):
        self.data_file = 'expenses.json'
        self.expenses = self.load_expenses()

    def load_expenses(self):
        """Load expenses from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                return json.load(file)
        return []

    def save_expenses(self):
        """Save expenses to JSON file"""
        with open(self.data_file, 'w') as file:
            json.dump(self.expenses, file, indent=4)

    def add_expense(self, amount, category, date, notes):
        """Add a new expense"""
        expense = {
            'amount': float(amount),
            'category': category,
            'date': date,
            'notes': notes
        }
        self.expenses.append(expense)
        self.save_expenses()
        return True

    def get_expenses(self, start_date=None, end_date=None, category=None):
        """Get filtered expenses"""
        df = pd.DataFrame(self.expenses)
        if len(df) == 0:
            return pd.DataFrame(columns=['amount', 'category', 'date', 'notes'])
        
        df['date'] = pd.to_datetime(df['date'])
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
        if category:
            df = df[df['category'] == category]
        
        return df

    def get_monthly_summary(self, year, month):
        """Get monthly summary of expenses"""
        df = pd.DataFrame(self.expenses)
        if len(df) == 0:
            return None, None
        
        df['date'] = pd.to_datetime(df['date'])
        monthly_data = df[
            (df['date'].dt.year == int(year)) & 
            (df['date'].dt.month == int(month))
        ]
        
        total_spending = monthly_data['amount'].sum()
        category_spending = monthly_data.groupby('category')['amount'].sum()
        
        return total_spending, category_spending

    def plot_category_distribution(self, year, month):
        """Plot expense distribution by category"""
        _, category_spending = self.get_monthly_summary(year, month)
        if category_spending is not None and not category_spending.empty:
            plt.figure(figsize=(10, 8))
            plt.pie(category_spending, labels=category_spending.index, autopct='%1.1f%%')
            plt.title(f'Expense Distribution by Category ({month}/{year})')
            plt.axis('equal')
            plt.show()

class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.tracker = ExpenseTracker()
        self.root.title("Personal Expense Tracker")
        self.root.geometry("800x600")
        self.setup_gui()

    def setup_gui(self):
        # Create tabs
        self.tab_control = ttk.Notebook(self.root)
        
        # Add Expense Tab
        self.add_expense_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.add_expense_tab, text='Add Expense')
        self.setup_add_expense_tab()

        # View Expenses Tab
        self.view_expenses_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.view_expenses_tab, text='View Expenses')
        self.setup_view_expenses_tab()

        # Monthly Summary Tab
        self.summary_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.summary_tab, text='Monthly Summary')
        self.setup_summary_tab()

        self.tab_control.pack(expand=1, fill='both')

    def setup_add_expense_tab(self):
        # Amount
        ttk.Label(self.add_expense_tab, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.add_expense_tab)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Category
        ttk.Label(self.add_expense_tab, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Other']
        self.category_combo = ttk.Combobox(self.add_expense_tab, values=categories)
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)

        # Date
        ttk.Label(self.add_expense_tab, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(self.add_expense_tab)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Notes
        ttk.Label(self.add_expense_tab, text="Notes:").grid(row=3, column=0, padx=5, pady=5)
        self.notes_entry = ttk.Entry(self.add_expense_tab)
        self.notes_entry.grid(row=3, column=1, padx=5, pady=5)

        # Submit Button
        ttk.Button(self.add_expense_tab, text="Add Expense", 
                  command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=20)

    def setup_view_expenses_tab(self):
        # Create Treeview
        self.expense_tree = ttk.Treeview(self.view_expenses_tab, 
                                       columns=('Date', 'Amount', 'Category', 'Notes'),
                                       show='headings')
        
        self.expense_tree.heading('Date', text='Date')
        self.expense_tree.heading('Amount', text='Amount')
        self.expense_tree.heading('Category', text='Category')
        self.expense_tree.heading('Notes', text='Notes')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.view_expenses_tab, orient=VERTICAL, command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=scrollbar.set)
        
        self.expense_tree.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)
        scrollbar.grid(row=0, column=4, sticky='ns')

        # Filter frame
        filter_frame = ttk.LabelFrame(self.view_expenses_tab, text="Filters")
        filter_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky='ew')

        # Date filters
        ttk.Label(filter_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = ttk.Entry(filter_frame)
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = ttk.Entry(filter_frame)
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        # Category filter
        ttk.Label(filter_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        categories = ['All', 'Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Other']
        self.filter_category = ttk.Combobox(filter_frame, values=categories)
        self.filter_category.set('All')
        self.filter_category.grid(row=1, column=1, padx=5, pady=5)

        # Apply filter button
        ttk.Button(filter_frame, text="Apply Filters", 
                  command=self.refresh_expenses).grid(row=1, column=2, columnspan=2, pady=5)

    def setup_summary_tab(self):
        # Year and Month selection
        ttk.Label(self.summary_tab, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        self.year_entry = ttk.Entry(self.summary_tab)
        self.year_entry.insert(0, str(datetime.now().year))
        self.year_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.summary_tab, text="Month:").grid(row=1, column=0, padx=5, pady=5)
        self.month_entry = ttk.Entry(self.summary_tab)
        self.month_entry.insert(0, str(datetime.now().month))
        self.month_entry.grid(row=1, column=1, padx=5, pady=5)

        # Generate Summary Button
        ttk.Button(self.summary_tab, text="Generate Summary", 
                  command=self.show_monthly_summary).grid(row=2, column=0, columnspan=2, pady=20)

        # Summary Text Area
        self.summary_text = Text(self.summary_tab, height=10, width=50)
        self.summary_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Plot Button
        ttk.Button(self.summary_tab, text="Show Plot", 
                  command=self.show_plot).grid(row=4, column=0, columnspan=2, pady=10)

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_combo.get()
            date = self.date_entry.get()
            notes = self.notes_entry.get()

            if not all([amount, category, date]):
                messagebox.showerror("Error", "Please fill all required fields")
                return

            if self.tracker.add_expense(amount, category, date, notes):
                messagebox.showinfo("Success", "Expense added successfully!")
                
                # Clear entries
                self.amount_entry.delete(0, END)
                self.category_combo.set('')
                self.notes_entry.delete(0, END)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid amount")

    def refresh_expenses(self):
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)

        # Get filter values
        start_date = self.start_date.get() if self.start_date.get() else None
        end_date = self.end_date.get() if self.end_date.get() else None
        category = self.filter_category.get()
        category = None if category == 'All' else category

        # Load and display expenses
        df = self.tracker.get_expenses(start_date, end_date, category)
        for _, row in df.iterrows():
            self.expense_tree.insert('', 'end', values=(
                row['date'].strftime('%Y-%m-%d'),
                f"${row['amount']:.2f}",
                row['category'],
                row['notes']
            ))

    def show_monthly_summary(self):
        try:
            year = int(self.year_entry.get())
            month = int(self.month_entry.get())
            
            total, category_spending = self.tracker.get_monthly_summary(year, month)
            
            if total is None:
                self.summary_text.delete(1.0, END)
                self.summary_text.insert(END, "No data available for selected period")
                return

            summary = f"Monthly Summary for {month}/{year}\n\n"
            summary += f"Total Spending: ${total:.2f}\n\n"
            summary += "Category Breakdown:\n"
            
            for category, amount in category_spending.items():
                summary += f"{category}: ${amount:.2f}\n"
            
            self.summary_text.delete(1.0, END)
            self.summary_text.insert(END, summary)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid year and month")

    def show_plot(self):
        try:
            year = int(self.year_entry.get())
            month = int(self.month_entry.get())
            self.tracker.plot_category_distribution(year, month)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid year and month")

def main():
    root = Tk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
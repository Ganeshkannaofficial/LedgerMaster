import sqlite3
import time
from datetime import datetime
from abc import ABC, abstractmethod


# Base class for common database operations (Abstraction)
class DBEntity:
    def __init__(self, db):
        self.db = db

    def create(self, table, fields, values):
        placeholders = ', '.join(['?'] * len(values))
        sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders});"
        self.db.cursor.execute(sql, values)
        self.db.connection.commit()

    def update(self, table, fields, values, condition, condition_values):
        set_clause = ', '.join([f"{field} = ?" for field in fields])
        sql = f"UPDATE {table} SET {set_clause} WHERE {condition};"
        self.db.cursor.execute(sql, values + condition_values)
        self.db.connection.commit()

    def select(self, table, fields, condition=None, condition_values=None):
        sql = f"SELECT {', '.join(fields)} FROM {table}"
        if condition:
            sql += f" WHERE {condition}"
        self.db.cursor.execute(sql, condition_values or [])
        return self.db.cursor.fetchall()


# Abstract Entity Class (Polymorphism)
class Entity(ABC):
    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def view(self):
        pass


# Database connection and initialization
class Database:
    def __init__(self):
        self.connection = sqlite3.connect('ledgermaster.db', timeout=10)  # Set timeout to 10 seconds
        self.connection.row_factory = sqlite3.Row  # Allow accessing columns by name
        self.cursor = self.connection.cursor()
        self.initialize_database()

    def initialize_database(self):
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        self.cursor.execute("PRAGMA busy_timeout = 3000;")  # 3 seconds timeout
        
        # Accounts table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_name TEXT PRIMARY KEY,
                account_type TEXT,
                balance REAL
            );
        """)
        # Inventory table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                item_name TEXT PRIMARY KEY,
                quantity INTEGER,
                price REAL
            );
        """)
        # Bills table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                bill_number TEXT PRIMARY KEY,
                customer_name TEXT,
                amount_due REAL,
                due_date TEXT,
                status TEXT
            );
        """)
        # Budgets table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                account_name TEXT PRIMARY KEY,
                budgeted_amount REAL,
                actual_amount REAL,
                budget_type TEXT
            );
        """)
        # Vouchers table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vouchers (
                voucher_number TEXT PRIMARY KEY,
                voucher_type TEXT,
                amount REAL,
                date TEXT
            );
        """)

        # Voucher log table to store voucher history
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS voucher_log (
                voucher_number TEXT PRIMARY KEY,
                voucher_type TEXT,
                amount REAL,
                date TEXT
            );
        """)

        self.connection.commit()


# Account Class inheriting DBEntity
class Account(DBEntity):
    def __init__(self, db):
        super().__init__(db)  # Call the parent class constructor

    def create_account(self, account_name, account_type, balance):
        self.create("accounts", ["account_name", "account_type", "balance"], 
                    [account_name, account_type, balance])
        print(f"Account '{account_name}' created successfully.")

    def credit_account(self, account_name, amount):
        self.update("accounts", ["balance"], [amount], "account_name = ?", [account_name])
        print(f"Credited {amount} to {account_name}.")
        
    def view_account(self, account_name):
        result = self.select("accounts", ["account_name", "account_type", "balance"], 
                             "account_name = ?", [account_name])
        if result:
            account = result[0]
            print(f"Account: {account[0]} | Type: {account[1]} | Balance: {account[2]}")
        else:
            print("Account not found.")


# Inventory Class inheriting DBEntity
class Inventory(DBEntity):
    def __init__(self, db):
        super().__init__(db)

    def create_inventory_item(self, item_name, quantity, price):
        self.create("inventory", ["item_name", "quantity", "price"], 
                    [item_name, quantity, price])
        print(f"Item '{item_name}' added to inventory.")

    def view_inventory(self):
        items = self.select("inventory", ["item_name", "quantity", "price"])
        for item in items:
            print(f"Item: {item[0]} | Quantity: {item[1]} | Price: {item[2]}")


# Bill Class inheriting DBEntity
class Bill(DBEntity):
    def __init__(self, db):
        super().__init__(db)

    def create_bill(self, bill_number, customer_name, amount_due, due_date):
        self.create("bills", ["bill_number", "customer_name", "amount_due", "due_date", "status"], 
                    [bill_number, customer_name, amount_due, due_date, "Unpaid"])
        print(f"Bill #{bill_number} created successfully.")

    def pay_bill(self, bill_number):
        self.update("bills", ["status"], ["Paid"], "bill_number = ?", [bill_number])
        print(f"Bill #{bill_number} marked as paid.")

    def view_bills(self):
        bills = self.select("bills", ["bill_number", "customer_name", "amount_due", "due_date", "status"])
        for bill in bills:
            print(f"Bill #{bill[0]} | Customer: {bill[1]} | Amount: {bill[2]} | Due Date: {bill[3]} | Status: {bill[4]}")


# Budget Class inheriting DBEntity
class Budget(DBEntity):
    def __init__(self, db):
        super().__init__(db)

    def set_budget(self, account_name, amount, budget_type):
        self.create("budgets", ["account_name", "budgeted_amount", "actual_amount", "budget_type"], 
                    [account_name, amount, 0, budget_type])
        print(f"Budget for {account_name} set to {amount} ({budget_type}).")

    def update_actual_in_budget(self, account_name, amount):
        self.update("budgets", ["actual_amount"], [amount], "account_name = ?", [account_name])
        print(f"Updated actual amount for {account_name} by {amount}.")

    def view_budgets(self):
        budgets = self.select("budgets", ["account_name", "budgeted_amount", "actual_amount", "budget_type"])
        for budget in budgets:
            print(f"Account: {budget[0]} | Budgeted: {budget[1]} | Actual: {budget[2]} | Type: {budget[3]}")


# Voucher Class inheriting DBEntity
class Voucher(DBEntity):
    def __init__(self, db):
        super().__init__(db)

    def create_voucher(self, voucher_number, voucher_type, amount):
        self.create("vouchers", ["voucher_number", "voucher_type", "amount", "date"], 
                    [voucher_number, voucher_type, amount, datetime.now().strftime('%Y-%m-%d')])
        print(f"Voucher #{voucher_number} created successfully.")

    def view_vouchers(self):
        vouchers = self.select("vouchers", ["voucher_number", "voucher_type", "amount", "date"])
        for voucher in vouchers:
            print(f"Voucher #{voucher[0]} | Type: {voucher[1]} | Amount: {voucher[2]} | Date: {voucher[3]}")

    def view_voucher_log(self):
        log = self.select("voucher_log", ["voucher_number", "voucher_type", "amount", "date"])
        for entry in log:
            print(f"Voucher #{entry[0]} | Type: {entry[1]} | Amount: {entry[2]} | Date: {entry[3]}")


# Main Application
class LedgerMasterApp:
    def __init__(self):
        self.db = Database()
        self.account = Account(self.db)
        self.inventory = Inventory(self.db)
        self.bill = Bill(self.db)
        self.budget = Budget(self.db)
        self.voucher = Voucher(self.db)

    def menu(self):
        while True:
            print("\nLedger Master Menu")
            print("1. Manage Accounts")
            print("2. Manage Inventory")
            print("3. Manage Bills")
            print("4. Manage Budgets")
            print("5. Manage Vouchers")
            print("6. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.account_menu()
            elif choice == '2':
                self.inventory_menu()
            elif choice == '3':
                self.bill_menu()
            elif choice == '4':
                self.budget_menu()
            elif choice == '5':
                self.voucher_menu()
            elif choice == '6':
                print("Exiting the application.")
                break
            else:
                print("Invalid choice, please try again.")

    def account_menu(self):
        while True:
            print("\nAccount Menu")
            print("1. Create Account")
            print("2. View Account")
            print("3. Back")
            choice = input("Enter your choice: ")

            if choice == '1':
                name = input("Enter account name: ")
                type_ = input("Enter account type: ")
                balance = float(input("Enter balance: "))
                self.account.create_account(name, type_, balance)
            elif choice == '2':
                name = input("Enter account name: ")
                self.account.view_account(name)
            elif choice == '3':
                break
            else:
                print("Invalid choice, please try again.")

    def inventory_menu(self):
        while True:
            print("\nInventory Menu")
            print("1. Add Inventory Item")
            print("2. View Inventory")
            print("3. Back")
            choice = input("Enter your choice: ")

            if choice == '1':
                item_name = input("Enter item name: ")
                quantity = int(input("Enter quantity: "))
                price = float(input("Enter price: "))
                self.inventory.create_inventory_item(item_name, quantity, price)
            elif choice == '2':
                self.inventory.view_inventory()
            elif choice == '3':
                break
            else:
                print("Invalid choice, please try again.")

    def bill_menu(self):
        while True:
            print("\nBill Menu")
            print("1. Create Bill")
            print("2. Pay Bill")
            print("3. View Bills")
            print("4. Back")
            choice = input("Enter your choice: ")

            if choice == '1':
                bill_number = input("Enter bill number: ")
                customer_name = input("Enter customer name: ")
                amount_due = float(input("Enter amount due: "))
                due_date = input("Enter due date (YYYY-MM-DD): ")
                self.bill.create_bill(bill_number, customer_name, amount_due, due_date)
            elif choice == '2':
                bill_number = input("Enter bill number: ")
                self.bill.pay_bill(bill_number)
            elif choice == '3':
                self.bill.view_bills()
            elif choice == '4':
                break
            else:
                print("Invalid choice, please try again.")

    def budget_menu(self):
        while True:
            print("\nBudget Menu")
            print("1. Set Budget")
            print("2. Update Actual Budget")
            print("3. View Budgets")
            print("4. Back")
            choice = input("Enter your choice: ")

            if choice == '1':
                account_name = input("Enter account name: ")
                amount = float(input("Enter budgeted amount: "))
                budget_type = input("Enter budget type (Income/Expense): ")
                self.budget.set_budget(account_name, amount, budget_type)
            elif choice == '2':
                account_name = input("Enter account name: ")
                amount = float(input("Enter actual amount: "))
                self.budget.update_actual_in_budget(account_name, amount)
            elif choice == '3':
                self.budget.view_budgets()
            elif choice == '4':
                break
            else:
                print("Invalid choice, please try again.")

    def voucher_menu(self):
        while True:
            print("\nVoucher Menu")
            print("1. Create Voucher")
            print("2. View Vouchers")
            print("3. View Voucher Log")
            print("4. Back")
            choice = input("Enter your choice: ")

            if choice == '1':
                voucher_number = input("Enter voucher number: ")
                voucher_type = input("Enter voucher type: ")
                amount = float(input("Enter amount: "))
                self.voucher.create_voucher(voucher_number, voucher_type, amount)
            elif choice == '2':
                self.voucher.view_vouchers()
            elif choice == '3':
                self.voucher.view_voucher_log()
            elif choice == '4':
                break
            else:
                print("Invalid choice, please try again.")


if __name__ == '__main__':
    app = LedgerMasterApp()
    app.menu()

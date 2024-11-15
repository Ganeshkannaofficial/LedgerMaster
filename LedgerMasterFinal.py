import sqlite3
import time
from datetime import datetime

class LedgerMaster:
    def __init__(self):
        # Connect to the SQLite database (or create it if it doesn't exist)
        self.connection = sqlite3.connect('ledgermaster.db', timeout=10)  # Set timeout to 10 seconds
        self.connection.row_factory = sqlite3.Row  # Allow accessing columns by name
        self.cursor = self.connection.cursor()
        self.initialize_database()

    def initialize_database(self):
        # Set journal mode to WAL for better concurrency
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
        self.connection.commit()
        print("Database and tables initialized.")

    # Retry mechanism for database operations in case of lock
    def execute_query(self, query, params=(), retries=3):
        attempt = 0
        while attempt < retries:
            try:
                self.cursor.execute(query, params)
                self.connection.commit()
                return
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    print(f"Database locked, retrying... ({attempt + 1}/{retries})")
                    time.sleep(1)  # Wait for a second before retry
                    attempt += 1
                else:
                    print(f"Error: {e}")
                    break

    # Account Management
    def create_account(self, account_name, account_type, balance):
        try:
            self.execute_query("INSERT INTO accounts (account_name, account_type, balance) VALUES (?, ?, ?);",
                               (account_name, account_type, balance))
            print(f"Account '{account_name}' created successfully.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_account(self, account_name):
        self.cursor.execute("SELECT * FROM accounts WHERE account_name = ?;", (account_name,))
        account = self.cursor.fetchone()
        if account:
            print(f"Account: {account['account_name']} | Type: {account['account_type']} | Balance: {account['balance']}")
        else:
            print("Account not found.")

    def view_all_accounts(self):
        self.cursor.execute("SELECT * FROM accounts;")
        accounts = self.cursor.fetchall()
        if accounts:
            for account in accounts:
                print(f"Account: {account['account_name']} | Type: {account['account_type']} | Balance: {account['balance']}")
        else:
            print("No accounts found.")

    def credit_account(self, account_name, amount):
        self.execute_query("UPDATE accounts SET balance = balance + ? WHERE account_name = ?;", (amount, account_name))
        print(f"Credited {amount} to {account_name}.")

    def debit_account(self, account_name, amount):
        self.cursor.execute("SELECT balance FROM accounts WHERE account_name = ?;", (account_name,))
        balance = self.cursor.fetchone()
        if balance and balance[0] >= amount:
            self.execute_query("UPDATE accounts SET balance = balance - ? WHERE account_name = ?;", (amount, account_name))
            print(f"Debited {amount} from {account_name}.")
        else:
            print("Insufficient balance or account not found.")

    def delete_account(self, account_name):
        try:
            self.execute_query("DELETE FROM accounts WHERE account_name = ?;", (account_name,))
            print(f"Account '{account_name}' deleted successfully.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    # Inventory Management
    def create_inventory_item(self, item_name, quantity, price):
        try:
            self.execute_query("INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, ?);",
                               (item_name, quantity, price))
            print(f"Item '{item_name}' added to inventory.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_inventory(self):
        self.cursor.execute("SELECT * FROM inventory;")
        items = self.cursor.fetchall()
        if items:
            for item in items:
                print(f"Item: {item[0]} | Quantity: {item[1]} | Price: {item[2]}")
        else:
            print("No inventory items found.")

    # Bill Management
    def create_bill(self, bill_number, customer_name, amount_due, due_date):
        try:
            self.execute_query("INSERT INTO bills (bill_number, customer_name, amount_due, due_date, status) VALUES (?, ?, ?, ?, 'Unpaid');",
                               (bill_number, customer_name, amount_due, due_date))
            print(f"Bill #{bill_number} created successfully.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_bills(self):
        self.cursor.execute("SELECT * FROM bills;")
        bills = self.cursor.fetchall()
        for bill in bills:
            print(f"Bill #{bill[0]} | Customer: {bill[1]} | Amount: {bill[2]} | Due Date: {bill[3]} | Status: {bill[4]}")

    def pay_bill(self, bill_number):
        self.execute_query("UPDATE bills SET status = 'Paid' WHERE bill_number = ?;", (bill_number,))
        print(f"Bill #{bill_number} marked as paid.")

    # Budget Management
    def set_budget(self, account_name, amount, budget_type):
        try:
            self.execute_query("INSERT INTO budgets (account_name, budgeted_amount, actual_amount, budget_type) VALUES (?, ?, 0, ?) ON CONFLICT(account_name) DO UPDATE SET budgeted_amount = ?;",
                               (account_name, amount, budget_type, amount))
            print(f"Budget for {account_name} set to {amount} ({budget_type}).")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_budgets(self):
        self.cursor.execute("SELECT * FROM budgets;")
        budgets = self.cursor.fetchall()
        for budget in budgets:
            print(f"Account: {budget[0]} | Budgeted: {budget[1]} | Actual: {budget[2]} | Type: {budget[3]}")

    def update_actual_in_budget(self, account_name, amount):
        self.execute_query("UPDATE budgets SET actual_amount = actual_amount + ? WHERE account_name = ?;", (amount, account_name))
        print(f"Updated actual amount for {account_name} by {amount}.")

    # Voucher Management
    def create_voucher(self, voucher_number, voucher_type, amount):
        try:
            self.execute_query("INSERT INTO vouchers (voucher_number, voucher_type, amount, date) VALUES (?, ?, ?, ?);",
                               (voucher_number, voucher_type, amount, datetime.now().strftime('%Y-%m-%d')))
            print(f"Voucher #{voucher_number} created successfully.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_vouchers(self):
        self.cursor.execute("SELECT * FROM vouchers;")
        vouchers = self.cursor.fetchall()
        for voucher in vouchers:
            print(f"Voucher #{voucher[0]} | Type: {voucher[1]} | Amount: {voucher[2]} | Date: {voucher[3]}")

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

def main():
    ledger = LedgerMaster()
    while True:
        print("\nMenu:")
        print("1. Create Account")
        print("2. View Account")
        print("3. Credit Account")
        print("4. Debit Account")
        print("5. Create Inventory Item")
        print("6. View Inventory")
        print("7. Create Bill")
        print("8. View Bills")
        print("9. Pay Bill")
        print("10. Set Budget")
        print("11. View Budgets")
        print("12. Update Budget Actual")
        print("13. Delete Account")
        print("14. View All Accounts")
        print("15. Create Voucher")
        print("16. View Vouchers")
        print("17. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            name = input("Enter account name: ")
            acc_type = input("Enter account type: ")
            balance = float(input("Enter balance: "))
            ledger.create_account(name, acc_type, balance)
        elif choice == '2':
            name = input("Enter account name: ")
            ledger.view_account(name)
        elif choice == '3':
            name = input("Enter account name: ")
            amount = float(input("Enter amount to credit: "))
            ledger.credit_account(name, amount)
        elif choice == '4':
            name = input("Enter account name: ")
            amount = float(input("Enter amount to debit: "))
            ledger.debit_account(name, amount)
        elif choice == '5':
            item_name = input("Enter item name: ")
            quantity = int(input("Enter quantity: "))
            price = float(input("Enter price: "))
            ledger.create_inventory_item(item_name, quantity, price)
        elif choice == '6':
            ledger.view_inventory()
        elif choice == '7':
            bill_number = input("Enter bill number: ")
            customer_name = input("Enter customer name: ")
            amount_due = float(input("Enter amount due: "))
            due_date = input("Enter due date (YYYY-MM-DD): ")
            ledger.create_bill(bill_number, customer_name, amount_due, due_date)
        elif choice == '8':
            ledger.view_bills()
        elif choice == '9':
            bill_number = input("Enter bill number to mark as paid: ")
            ledger.pay_bill(bill_number)
        elif choice == '10':
            account_name = input("Enter account name: ")
            amount = float(input("Enter budget amount: "))
            budget_type = input("Enter budget type: ")
            ledger.set_budget(account_name, amount, budget_type)
        elif choice == '11':
            ledger.view_budgets()
        elif choice == '12':
            account_name = input("Enter account name: ")
            amount = float(input("Enter actual amount to update: "))
            ledger.update_actual_in_budget(account_name, amount)
        elif choice == '13':
            account_name = input("Enter account name to delete: ")
            ledger.delete_account(account_name)
        elif choice == '14':
            ledger.view_all_accounts()
        elif choice == '15':
            voucher_number = input("Enter voucher number: ")
            voucher_type = input("Enter voucher type: ")
            amount = float(input("Enter amount: "))
            ledger.create_voucher(voucher_number, voucher_type, amount)
        elif choice == '16':
            ledger.view_vouchers()
        elif choice == '17':
            ledger.close_connection()
            print("Exiting.")
            break

if __name__ == "__main__":
    main()

import sqlite3
from datetime import datetime

class LedgerMaster:
    def __init__(self):
        # Connect to the SQLite database (or create it if it doesn't exist)
        self.connection = sqlite3.connect('ledgermaster.db', timeout=10)  # Set timeout to 10 seconds
        self.cursor = self.connection.cursor()
        self.initialize_database()

    def initialize_database(self):
        # Set journal mode to WAL for better concurrency
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Set busy timeout to handle locked database
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
        # Vouchers table for payment and receipt transactions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vouchers (
                voucher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_name TEXT,
                voucher_type TEXT,  -- 'Receipt' or 'Payment'
                amount REAL,
                date TEXT,
                description TEXT
            );
        """)
        self.connection.commit()
        print("Database and tables initialized.")

    # Account Management
    def create_account(self, account_name, account_type, balance):
        try:
            self.cursor.execute("INSERT INTO accounts (account_name, account_type, balance) VALUES (?, ?, ?);",
                                (account_name, account_type, balance))
            self.connection.commit()
            print(f"Account '{account_name}' created successfully.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_account(self, account_name):
        self.cursor.execute("SELECT * FROM accounts WHERE account_name = ?;", (account_name,))
        account = self.cursor.fetchone()
        if account:
            print(f"Account: {account[0]} | Type: {account[1]} | Balance: {account[2]}")
        else:
            print("Account not found.")

    def view_all_accounts(self):
        self.cursor.execute("SELECT * FROM accounts;")
        accounts = self.cursor.fetchall()
        if accounts:
            for account in accounts:
                print(f"Account: {account[0]} | Type: {account[1]} | Balance: {account[2]}")
        else:
            print("No accounts found.")

    def delete_account(self, account_name):
        try:
            self.cursor.execute("DELETE FROM accounts WHERE account_name = ?;", (account_name,))
            self.connection.commit()
            print(f"Account '{account_name}' deleted successfully.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def credit_account(self, account_name, amount):
        self.cursor.execute("UPDATE accounts SET balance = balance + ? WHERE account_name = ?;", (amount, account_name))
        self.connection.commit()
        print(f"Credited {amount} to {account_name}.")

    def debit_account(self, account_name, amount):
        self.cursor.execute("SELECT balance FROM accounts WHERE account_name = ?;", (account_name,))
        balance = self.cursor.fetchone()
        if balance and balance[0] >= amount:
            self.cursor.execute("UPDATE accounts SET balance = balance - ? WHERE account_name = ?;", (amount, account_name))
            self.connection.commit()
            print(f"Debited {amount} from {account_name}.")
        else:
            print("Insufficient balance or account not found.")

    # Inventory Management
    def create_inventory_item(self, item_name, quantity, price):
        try:
            self.cursor.execute("INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, ?);",
                                (item_name, quantity, price))
            self.connection.commit()
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
            self.cursor.execute("INSERT INTO bills (bill_number, customer_name, amount_due, due_date, status) VALUES (?, ?, ?, ?, 'Unpaid');",
                                (bill_number, customer_name, amount_due, due_date))
            self.connection.commit()
            print(f"Bill #{bill_number} created successfully.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_bills(self):
        self.cursor.execute("SELECT * FROM bills;")
        bills = self.cursor.fetchall()
        for bill in bills:
            print(f"Bill #{bill[0]} | Customer: {bill[1]} | Amount: {bill[2]} | Due Date: {bill[3]} | Status: {bill[4]}")

    def pay_bill(self, bill_number):
        self.cursor.execute("UPDATE bills SET status = 'Paid' WHERE bill_number = ?;", (bill_number,))
        self.connection.commit()
        print(f"Bill #{bill_number} marked as paid.")

    # Budget Management
    def set_budget(self, account_name, amount, budget_type):
        try:
            self.cursor.execute("INSERT INTO budgets (account_name, budgeted_amount, actual_amount, budget_type) VALUES (?, ?, 0, ?) ON CONFLICT(account_name) DO UPDATE SET budgeted_amount = ?;",
                                (account_name, amount, budget_type, amount))
            self.connection.commit()
            print(f"Budget for {account_name} set to {amount} ({budget_type}).")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_budgets(self):
        self.cursor.execute("SELECT * FROM budgets;")
        budgets = self.cursor.fetchall()
        for budget in budgets:
            print(f"Account: {budget[0]} | Budgeted: {budget[1]} | Actual: {budget[2]} | Type: {budget[3]}")

    def update_actual_in_budget(self, account_name, amount):
        self.cursor.execute("UPDATE budgets SET actual_amount = actual_amount + ? WHERE account_name = ?;", (amount, account_name))
        self.connection.commit()
        print(f"Updated actual amount for {account_name} by {amount}.")

    # Voucher Entry Management
    def create_voucher(self, account_name, voucher_type, amount, description):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute("INSERT INTO vouchers (account_name, voucher_type, amount, date, description) VALUES (?, ?, ?, ?, ?);",
                                (account_name, voucher_type, amount, date, description))
            self.connection.commit()
            print(f"{voucher_type} voucher created for {account_name} of amount {amount}.")
        except sqlite3.Error as err:
            print(f"Error: {err}")

    def view_vouchers(self):
        self.cursor.execute("SELECT * FROM vouchers;")
        vouchers = self.cursor.fetchall()
        if vouchers:
            for voucher in vouchers:
                print(f"Voucher ID: {voucher[0]} | Account: {voucher[1]} | Type: {voucher[2]} | Amount: {voucher[3]} | Date: {voucher[4]} | Description: {voucher[5]}")
        else:
            print("No vouchers found.")

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
        print("13. Create Voucher")
        print("14. View Vouchers")
        print("15. View All Accounts")
        print("16. Delete Account")
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
            account_name = input("Enter account name: ")
            voucher_type = input("Enter voucher type (Receipt/Payment): ")
            amount = float(input("Enter amount: "))
            description = input("Enter description: ")
            ledger.create_voucher(account_name, voucher_type, amount, description)
        elif choice == '14':
            ledger.view_vouchers()
        elif choice == '15':
            ledger.view_all_accounts()
        elif choice == '16':
            account_name = input("Enter account name to delete: ")
            ledger.delete_account(account_name)
        elif choice == '17':
            ledger.close_connection()
            print("Exiting.")
            break

if __name__ == "__main__":
    main()

import json
from datetime import datetime

class LedgerAccount:
    def __init__(self, account_name, account_type, balance=0.0):
        self.account_name = account_name
        self.account_type = account_type
        self.balance = balance

    def credit(self, amount):
        self.balance += amount

    def debit(self, amount):
        if amount > self.balance:
            print(f"Insufficient balance in {self.account_name}")
            return
        self.balance -= amount

    def to_dict(self):
        return {
            "account_name": self.account_name,
            "account_type": self.account_type,
            "balance": self.balance
        }

class Bill:
    def __init__(self, bill_number, customer_name, amount_due, due_date):
        self.bill_number = bill_number
        self.customer_name = customer_name
        self.amount_due = amount_due
        self.due_date = due_date
        self.status = "Unpaid"

    def mark_as_paid(self):
        self.status = "Paid"

    def to_dict(self):
        return {
            "bill_number": self.bill_number,
            "customer_name": self.customer_name,
            "amount_due": self.amount_due,
            "due_date": self.due_date,
            "status": self.status
        }

class Budget:
    def __init__(self, account_name, amount, budget_type):
        self.account_name = account_name
        self.budgeted_amount = amount
        self.actual_amount = 0.0  # Track actual expenses or income
        self.budget_type = budget_type  # "Expense" or "Income"

    def update_actual(self, amount):
        self.actual_amount += amount

    def to_dict(self):
        return {
            "account_name": self.account_name,
            "budgeted_amount": self.budgeted_amount,
            "actual_amount": self.actual_amount,
            "budget_type": self.budget_type
        }

class LedgerMaster:
    def __init__(self, file_name="ledger_data.json"):
        self.accounts = {}  # Accounts will be stored here
        self.inventory = {}
        self.bills = []  # To manage bills
        self.budgets = {}  # To manage budgets
        self.file_name = file_name
        self.load_data()

    # Account Management
    def create_account(self, account_name, account_type, balance=0.0):
        if account_name in self.accounts:
            print(f"Account {account_name} already exists.")
        else:
            account = LedgerAccount(account_name, account_type, balance)
            self.accounts[account_name] = account
            print(f"Account {account_name} created with initial balance {balance}.")
            self.save_data()

    def view_account(self, account_name):
        account = self.accounts.get(account_name)
        if account:
            print(f"Account Name: {account.account_name} | Account Type: {account.account_type} | Balance: {account.balance}")
        else:
            print(f"Account {account_name} not found.")

    def credit_account(self, account_name, amount):
        account = self.accounts.get(account_name)
        if account:
            account.credit(amount)
            print(f"Account {account_name} credited with {amount}. New balance: {account.balance}")
            self.save_data()
        else:
            print(f"Account {account_name} not found.")

    def debit_account(self, account_name, amount):
        account = self.accounts.get(account_name)
        if account:
            account.debit(amount)
            print(f"Account {account_name} debited with {amount}. New balance: {account.balance}")
            self.save_data()
        else:
            print(f"Account {account_name} not found.")

    # Inventory Management (Simplified example)
    def create_inventory_item(self, item_name, quantity, price):
        self.inventory[item_name] = {"quantity": quantity, "price": price}
        print(f"Inventory item {item_name} created with quantity {quantity} and price {price}.")
        self.save_data()

    def view_inventory(self):
        if not self.inventory:
            print("No inventory items found.")
        for item, details in self.inventory.items():
            print(f"Item: {item} | Quantity: {details['quantity']} | Price: {details['price']}")

    # Bill Management
    def create_bill(self, bill_number, customer_name, amount_due, due_date):
        bill = Bill(bill_number, customer_name, amount_due, due_date)
        self.bills.append(bill)
        print(f"Bill #{bill_number} created for {customer_name}. Amount Due: {amount_due}")
        self.save_data()

    def view_bills(self):
        for bill in self.bills:
            print(f"Bill #{bill.bill_number} | Customer: {bill.customer_name} | Amount Due: {bill.amount_due} | Due Date: {bill.due_date} | Status: {bill.status}")

    def pay_bill(self, bill_number):
        for bill in self.bills:
            if bill.bill_number == bill_number:
                bill.mark_as_paid()
                print(f"Bill #{bill_number} marked as paid.")
                self.save_data()
                return
        print("Bill not found.")

    # Budget Management
    def set_budget(self, account_name, amount, budget_type):
        if account_name in self.budgets:
            print(f"Updating budget for {account_name} to {amount} as {budget_type}")
        else:
            print(f"Setting new budget for {account_name}: {amount} as {budget_type}")
        self.budgets[account_name] = Budget(account_name, amount, budget_type)
        self.save_data()

    def view_budgets(self):
        for budget in self.budgets.values():
            print(f"Account: {budget.account_name} | Budgeted: {budget.budgeted_amount} | Actual: {budget.actual_amount} | Type: {budget.budget_type}")

    def update_actual_in_budget(self, account_name, amount):
        if account_name in self.budgets:
            self.budgets[account_name].update_actual(amount)
            print(f"Updated actual for {account_name} by {amount}.")
            self.save_data()
        else:
            print(f"Budget for {account_name} not found.")

    # Banking & E-Payments
    def reconcile_bank(self, bank_name, bank_balance):
        account = self.accounts.get(bank_name)
        if account:
            difference = bank_balance - account.balance
            if difference != 0:
                print(f"Reconciling: Adjusting {bank_name} balance by {difference}.")
                account.credit(difference)
            else:
                print(f"{bank_name} is already reconciled.")
            self.save_data()
        else:
            print("Bank account not found.")

    def e_payment(self, sender_account, receiver_account, amount):
        sender = self.accounts.get(sender_account)
        receiver = self.accounts.get(receiver_account)
        if sender and receiver:
            if sender.balance >= amount:
                sender.debit(amount)
                receiver.credit(amount)
                print(f"E-payment of {amount} from {sender_account} to {receiver_account} completed.")
                self.save_data()
            else:
                print(f"Insufficient funds in {sender_account}.")
        else:
            print("One or both accounts not found.")

    # Existing Data Functions & Save Changes
    def load_data(self):
        try:
            with open(self.file_name, 'r') as file:
                data = json.load(file)
                self.accounts = {account_name: LedgerAccount(**account_data) for account_name, account_data in data.get('accounts', {}).items()}
                self.bills = [Bill(**bill_data) for bill_data in data.get('bills', [])]
                self.budgets = {account_name: Budget(**budget_data) for account_name, budget_data in data.get('budgets', {}).items()}
                print("Data loaded from file.")
        except FileNotFoundError:
            print(f"{self.file_name} not found. Starting fresh.")
        except json.JSONDecodeError as e:
            print(f"Error loading data: {e}")
        except Exception as e:
            print(f"Unexpected error while loading data: {e}")

    def save_data(self):
        try:
            data = {
                "accounts": {account_name: account.to_dict() for account_name, account in self.accounts.items()},
                "bills": [bill.to_dict() for bill in self.bills],
                "budgets": {account_name: budget.to_dict() for account_name, budget in self.budgets.items()}
            }
            with open(self.file_name, 'w') as file:
                json.dump(data, file, indent=4)
            print("Data saved to file.")
        except Exception as e:
            print(f"Error saving data: {e}")

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
        print("12. Update Actual in Budget")
        print("13. Reconcile Bank")
        print("14. E-payment")
        print("15. View All Accounts")
        print("16. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            account_name = input("Enter account name: ")
            account_type = input("Enter account type (Savings/Checking): ")
            balance = float(input("Enter initial balance: "))
            ledger.create_account(account_name, account_type, balance)

        elif choice == '2':
            account_name = input("Enter account name to view: ")
            ledger.view_account(account_name)

        elif choice == '3':
            account_name = input("Enter account name to credit: ")
            amount = float(input("Enter amount to credit: "))
            ledger.credit_account(account_name, amount)

        elif choice == '4':
            account_name = input("Enter account name to debit: ")
            amount = float(input("Enter amount to debit: "))
            ledger.debit_account(account_name, amount)

        elif choice == '5':
            item_name = input("Enter inventory item name: ")
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
            bill_number = input("Enter bill number to pay: ")
            ledger.pay_bill(bill_number)

        elif choice == '10':
            account_name = input("Enter account name to set budget for: ")
            amount = float(input("Enter budgeted amount: "))
            budget_type = input("Enter budget type (Expense/Income): ")
            ledger.set_budget(account_name, amount, budget_type)

        elif choice == '11':
            ledger.view_budgets()

        elif choice == '12':
            account_name = input("Enter account name to update actual expenses for: ")
            amount = float(input("Enter amount to update: "))
            ledger.update_actual_in_budget(account_name, amount)

        elif choice == '13':
            bank_name = input("Enter bank account name to reconcile: ")
            bank_balance = float(input("Enter actual bank balance: "))
            ledger.reconcile_bank(bank_name, bank_balance)

        elif choice == '14':
            sender_account = input("Enter sender account name: ")
            receiver_account = input("Enter receiver account name: ")
            amount = float(input("Enter amount to transfer: "))
            ledger.e_payment(sender_account, receiver_account, amount)

        elif choice == '15':
            ledger.view_all_accounts()

        elif choice == '16':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()

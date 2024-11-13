import json

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

class InventoryItem:
    def __init__(self, item_name, item_price, item_quantity=0):
        self.item_name = item_name
        self.item_price = item_price
        self.item_quantity = item_quantity

    def update_quantity(self, quantity):
        self.item_quantity += quantity

    def to_dict(self):
        return {
            "item_name": self.item_name,
            "item_price": self.item_price,
            "item_quantity": self.item_quantity
        }

class Transaction:
    def __init__(self, account_name, transaction_type, amount):
        self.account_name = account_name
        self.transaction_type = transaction_type
        self.amount = amount

class Tax:
    def __init__(self, rate):
        self.rate = rate

    def calculate_tax(self, amount):
        return (self.rate / 100) * amount

class LedgerMaster:
    def __init__(self, file_name="ledger_data.json"):
        self.accounts = {}
        self.inventory = {}
        self.transactions = []
        self.tax_rate = Tax(18)  # Default tax rate of 18%
        self.file_name = file_name
        self.load_data()

    def load_data(self):
        try:
            with open(self.file_name, 'r') as file:
                data = json.load(file)
                for account_data in data.get("accounts", []):
                    account = LedgerAccount(
                        account_data['account_name'], 
                        account_data['account_type'], 
                        account_data['balance']
                    )
                    self.accounts[account_data['account_name']] = account
                for item_data in data.get("inventory", []):
                    item = InventoryItem(
                        item_data['item_name'], 
                        item_data['item_price'], 
                        item_data['item_quantity']
                    )
                    self.inventory[item_data['item_name']] = item
            print("Data loaded successfully.")
        except FileNotFoundError:
            print("No previous data found. Starting fresh.")
        except json.JSONDecodeError:
            print("Error loading data. Starting with fresh data.")

    def save_data(self):
        data = {
            "accounts": [account.to_dict() for account in self.accounts.values()],
            "inventory": [item.to_dict() for item in self.inventory.values()],
        }
        with open(self.file_name, 'w') as file:
            json.dump(data, file, indent=4)
        print("Data saved successfully.")

    def create_account(self, name, account_type, initial_balance=0.0):
        if name in self.accounts:
            print(f"Account with name '{name}' already exists.")
            return
        self.accounts[name] = LedgerAccount(name, account_type, initial_balance)
        print(f"Account '{name}' created successfully.")
        self.save_data()

    def view_account(self, name):
        account = self.accounts.get(name)
        if account:
            print(f"Account Name: {account.account_name}")
            print(f"Account Type: {account.account_type}")
            print(f"Balance: {account.balance}")
        else:
            print("Account not found.")

    def credit_account(self, name, amount):
        account = self.accounts.get(name)
        if account:
            account.credit(amount)
            print(f"Credited {amount} to {name}")
            self.save_data()
        else:
            print("Account not found.")

    def debit_account(self, name, amount):
        account = self.accounts.get(name)
        if account:
            account.debit(amount)
            print(f"Debited {amount} from {name}")
            self.save_data()
        else:
            print("Account not found.")

    def create_inventory_item(self, name, price, quantity=0):
        if name in self.inventory:
            print(f"Item '{name}' already exists.")
            return
        self.inventory[name] = InventoryItem(name, price, quantity)
        print(f"Inventory item '{name}' added successfully.")
        self.save_data()

    def view_inventory(self):
        for item_name, item in self.inventory.items():
            print(f"Item Name: {item.item_name}, Price: {item.item_price}, Quantity: {item.item_quantity}")

    def apply_tax_on_purchase(self, purchase_amount):
        tax = self.tax_rate.calculate_tax(purchase_amount)
        print(f"Tax on purchase of {purchase_amount}: {tax}")
        return tax

    def apply_tax_on_sale(self, sale_amount):
        tax = self.tax_rate.calculate_tax(sale_amount)
        print(f"Tax on sale of {sale_amount}: {tax}")
        return tax

    def display_all_accounts(self):
        for account_name, account in self.accounts.items():
            print(f"Account Name: {account.account_name}, Type: {account.account_type}, Balance: {account.balance}")

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
        print("7. Apply Tax on Purchase")
        print("8. Apply Tax on Sale")
        print("9. Display All Accounts")
        print("10. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            name = input("Enter account name: ")
            account_type = input("Enter account type (Asset/Liability/Income/Expense): ")
            initial_balance = float(input("Enter initial balance: "))
            ledger.create_account(name, account_type, initial_balance)

        elif choice == '2':
            name = input("Enter account name to view: ")
            ledger.view_account(name)

        elif choice == '3':
            name = input("Enter account name to credit: ")
            amount = float(input("Enter amount to credit: "))
            ledger.credit_account(name, amount)

        elif choice == '4':
            name = input("Enter account name to debit: ")
            amount = float(input("Enter amount to debit: "))
            ledger.debit_account(name, amount)

        elif choice == '5':
            name = input("Enter inventory item name: ")
            price = float(input("Enter price of the item: "))
            quantity = int(input("Enter quantity of the item: "))
            ledger.create_inventory_item(name, price, quantity)

        elif choice == '6':
            ledger.view_inventory()

        elif choice == '7':
            purchase_amount = float(input("Enter purchase amount: "))
            ledger.apply_tax_on_purchase(purchase_amount)

        elif choice == '8':
            sale_amount = float(input("Enter sale amount: "))
            ledger.apply_tax_on_sale(sale_amount)

        elif choice == '9':
            ledger.display_all_accounts()

        elif choice == '10':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

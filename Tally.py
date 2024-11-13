class Ledger:
    def __init__(self, name):
        self.name = name
        self.balance = 0
        self.transactions = []

    def add_transaction(self, amount, transaction_type):
        if transaction_type.lower() == "debit":
            self.balance -= amount
            self.transactions.append({"type": "debit", "amount": amount})
        elif transaction_type.lower() == "credit":
            self.balance += amount
            self.transactions.append({"type": "credit", "amount": amount})
        else:
            print("Invalid transaction type. Use 'debit' or 'credit'.")

    def display_ledger(self):
        print(f"\nLedger: {self.name}")
        print(f"Balance: {self.balance}")
        print("Transactions:")
        for transaction in self.transactions:
            print(f"  - {transaction['type'].capitalize()} of {transaction['amount']}")
        print("\n")


class Voucher:
    def __init__(self, voucher_type, amount, from_ledger, to_ledger):
        self.voucher_type = voucher_type
        self.amount = amount
        self.from_ledger = from_ledger
        self.to_ledger = to_ledger

    def process_voucher(self):
        print(f"Processing {self.voucher_type} voucher for amount {self.amount}")
        self.from_ledger.add_transaction(self.amount, "debit")
        self.to_ledger.add_transaction(self.amount, "credit")
        print(f"{self.voucher_type} voucher processed successfully.\n")


class TallyPrimeSystem:
    def __init__(self):
        self.ledgers = {}

    def create_ledger(self, ledger_name):
        if ledger_name in self.ledgers:
            print(f"Ledger '{ledger_name}' already exists.")
        else:
            ledger = Ledger(ledger_name)
            self.ledgers[ledger_name] = ledger
            print(f"Ledger '{ledger_name}' created successfully.")

    def display_ledger(self, ledger_name):
        if ledger_name in self.ledgers:
            self.ledgers[ledger_name].display_ledger()
        else:
            print(f"No ledger found with name '{ledger_name}'.")

    def display_all_ledgers(self):
        if self.ledgers:
            print("\nDisplaying all ledgers:")
            for ledger_name, ledger in self.ledgers.items():
                ledger.display_ledger()
        else:
            print("No ledgers available.")

    def create_voucher(self, voucher_type, amount, from_ledger_name, to_ledger_name):
        if from_ledger_name not in self.ledgers or to_ledger_name not in self.ledgers:
            print("Both ledgers must exist to create a voucher.")
            return

        from_ledger = self.ledgers[from_ledger_name]
        to_ledger = self.ledgers[to_ledger_name]
        voucher = Voucher(voucher_type, amount, from_ledger, to_ledger)
        voucher.process_voucher()


def main():
    tally_system = TallyPrimeSystem()
    while True:
        print("\n=== Tally Prime Console Application ===")
        print("1. Create Ledger")
        print("2. Display Ledger")
        print("3. Display All Ledgers")
        print("4. Create Voucher")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            ledger_name = input("Enter ledger name: ")
            tally_system.create_ledger(ledger_name)

        elif choice == "2":
            ledger_name = input("Enter ledger name to display: ")
            tally_system.display_ledger(ledger_name)

        elif choice == "3":
            tally_system.display_all_ledgers()

        elif choice == "4":
            voucher_type = input("Enter voucher type (e.g., 'Sales', 'Purchase'): ")
            try:
                amount = float(input("Enter voucher amount: "))
            except ValueError:
                print("Invalid amount. Please enter a valid number.")
                continue
            from_ledger_name = input("Enter 'from' ledger name: ")
            to_ledger_name = input("Enter 'to' ledger name: ")
            tally_system.create_voucher(voucher_type, amount, from_ledger_name, to_ledger_name)

        elif choice == "5":
            print("Exiting the application.")
            break

        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main()

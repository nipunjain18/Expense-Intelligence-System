import json
import os
import sys
from datetime import date

# Ensure the console can display non-ASCII characters like ₹
sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = "data"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")

VALID_ACCOUNT_TYPES = ["Cash", "Bank", "UPI", "Investment", "Credit Card"]

TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
VALID_TRANSACTION_TYPES = ["Income", "Expense"]
REQUIRED_TRANSACTION_KEYS = {"transaction_id", "account_id", "type", "amount", "description", "date"}


def load_accounts():
    """Return all accounts from the JSON file, or [] if none exist."""

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(ACCOUNTS_FILE):
        return []

    with open(ACCOUNTS_FILE, "r") as file:
        content = file.read()

    if not content.strip():
        return []

    return json.loads(content)


def save_accounts(accounts):
    """Write the full accounts list to accounts.json."""

    with open(ACCOUNTS_FILE, "w") as file:
        json.dump(accounts, file, indent=4)


def generate_account_id(accounts):
    """Return the next account ID (highest existing + 1, starting from 1)."""

    if len(accounts) == 0:
        return 1

    return max(account["account_id"] for account in accounts) + 1


def load_transactions():
    """Return all transactions from the JSON file, or [] if none exist."""

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(TRANSACTIONS_FILE):
        return []

    with open(TRANSACTIONS_FILE, "r") as file:
        content = file.read()

    if not content.strip():
        return []

    return json.loads(content)


def save_transactions(transactions):
    """Write the full transactions list to transactions.json."""

    with open(TRANSACTIONS_FILE, "w") as file:
        json.dump(transactions, file, indent=4)


def generate_transaction_id(transactions):
    """Return the next transaction ID (highest existing + 1, starting from 1)."""

    if len(transactions) == 0:
        return 1

    return max(transaction["transaction_id"] for transaction in transactions) + 1


def is_duplicate_name(accounts, name):
    """Case-insensitive check for duplicate account name."""

    for account in accounts:
        if account["name"].lower() == name.lower():
            return True

    return False


def get_valid_account_type():
    """Prompt the user to pick an account type from the allowed list."""

    print("\nAvailable Account Types:")
    for i, account_type in enumerate(VALID_ACCOUNT_TYPES, start=1):
        print(f"  {i}. {account_type}")

    while True:
        choice = input("Enter the number of your account type: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice_number = int(choice)

        if choice_number < 1 or choice_number > len(VALID_ACCOUNT_TYPES):
            print(f"Please enter a number between 1 and {len(VALID_ACCOUNT_TYPES)}.")
            continue

        return VALID_ACCOUNT_TYPES[choice_number - 1]


def get_valid_balance():
    """Prompt the user for a non-negative starting balance."""

    while True:
        balance_input = input("Enter starting balance: ").strip()

        try:
            balance = float(balance_input)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if balance < 0:
            print("Balance cannot be negative.")
            continue

        return balance


def select_account(accounts):
    """Prompt the user to pick an account from a numbered list."""

    sorted_accounts = sorted(accounts, key=lambda a: a["account_id"])

    print("\nSelect an account:")
    for i, account in enumerate(sorted_accounts, start=1):
        print(f"  {i}. {account['name']} ({format_currency(account['balance'])})")

    while True:
        choice = input("Enter the number of your account: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice_number = int(choice)

        if choice_number < 1 or choice_number > len(sorted_accounts):
            print(f"Please enter a number between 1 and {len(sorted_accounts)}.")
            continue

        return sorted_accounts[choice_number - 1]


def get_valid_transaction_type():
    """Prompt the user to pick a transaction type from the allowed list."""

    print("\nTransaction Types:")
    for i, transaction_type in enumerate(VALID_TRANSACTION_TYPES, start=1):
        print(f"  {i}. {transaction_type}")

    while True:
        choice = input("Enter the number of your transaction type: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice_number = int(choice)

        if choice_number < 1 or choice_number > len(VALID_TRANSACTION_TYPES):
            print(f"Please enter a number between 1 and {len(VALID_TRANSACTION_TYPES)}.")
            continue

        return VALID_TRANSACTION_TYPES[choice_number - 1]


def get_valid_amount(transaction_type, balance):
    """Prompt the user for a valid transaction amount."""

    while True:
        amount_input = input("Enter amount: ").strip()

        try:
            amount = float(amount_input)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if amount <= 0:
            print("Amount must be greater than zero.")
            continue

        if transaction_type == "Expense" and amount > balance:
            print("Insufficient balance.")
            continue

        return amount


def add_account():
    """Create and save a new account via CLI prompts."""

    print("\n--- Add New Account ---")

    accounts = load_accounts()

    while True:
        name = input("Enter account name: ").strip()

        if len(name) == 0:
            print("Account name cannot be empty.")
            continue

        if is_duplicate_name(accounts, name):
            print(f"An account with the name '{name}' already exists.")
            continue

        break

    account_type = get_valid_account_type()
    balance = get_valid_balance()

    new_account = {
        "account_id": generate_account_id(accounts),
        "name": name,
        "account_type": account_type,
        "balance": balance,
        "created_at": str(date.today())
    }

    accounts.append(new_account)
    save_accounts(accounts)

    print(f"\nAccount '{name}' created successfully!")
    print(f"  ID:      {new_account['account_id']}")
    print(f"  Type:    {new_account['account_type']}")
    print(f"  Balance: {new_account['balance']}")
    print(f"  Date:    {new_account['created_at']}")


def format_currency(amount):
    """Format a number as ₹ currency. Example: 15000 → '₹15,000.00'"""

    return f"₹{amount:,.2f}"


def format_transaction_amount(amount, transaction_type):
    """Format amount with +/- sign and ₹ symbol. Example: 500, 'Expense' → '-₹500.00'"""

    if transaction_type == "Income":
        return f"+₹{amount:,.2f}"

    return f"-₹{amount:,.2f}"


def validate_transaction(transaction):
    """Check if a single transaction record is valid for display."""

    if not isinstance(transaction, dict):
        return False

    if not REQUIRED_TRANSACTION_KEYS.issubset(transaction.keys()):
        return False

    if transaction["type"] not in VALID_TRANSACTION_TYPES:
        return False

    if not isinstance(transaction["amount"], (int, float)):
        return False

    if not isinstance(transaction["description"], str) or not transaction["description"].strip():
        return False

    if not isinstance(transaction["date"], str) or not transaction["date"].strip():
        return False

    return True


def get_account_name(account_id, accounts):
    """Resolve an account_id to its name, or 'Deleted Account' if not found."""

    for account in accounts:
        if account["account_id"] == account_id:
            return account["name"]

    return "Deleted Account"


def display_transaction_table(transactions, accounts):
    """Print formatted transaction table with header and rows."""

    header = f"  {'ID':<6}{'Date':<13}{'Type':<11}{'Account':<20}{'Amount':>15}  {'Description'}"
    print(f"\n{header}")
    print("  " + "-" * (len(header) - 2))

    for transaction in transactions:
        account_name = get_account_name(transaction["account_id"], accounts)
        formatted_amount = format_transaction_amount(transaction["amount"], transaction["type"])

        print(
            f"  {transaction['transaction_id']:<6}"
            f"{transaction['date']:<13}"
            f"{transaction['type']:<11}"
            f"{account_name:<20}"
            f"{formatted_amount:>15}  "
            f"{transaction['description']}"
        )


def display_accounts_summary(accounts):
    """Print account count and total balance."""

    total_accounts = len(accounts)
    total_balance = sum(account["balance"] for account in accounts)

    print(f"\n  Total Accounts : {total_accounts}")
    print(f"  Total Balance  : {format_currency(total_balance)}")


def view_accounts():
    """Display all accounts in a formatted table. Read-only."""

    print("\n--- View Accounts ---")

    accounts = load_accounts()

    if len(accounts) == 0:
        print("\nNo accounts found.")
        return

    sorted_accounts = sorted(accounts, key=lambda a: a["account_id"])

    display_accounts_summary(sorted_accounts)

    header = f"  {'ID':<6}{'Name':<25}{'Type':<18}{'Balance':>15}"
    print(f"\n{header}")
    print("  " + "-" * (len(header) - 2))

    for account in sorted_accounts:
        print(
            f"  {account['account_id']:<6}"
            f"{account['name']:<25}"
            f"{account['account_type']:<18}"
            f"{format_currency(account['balance']):>15}"
        )


def add_transaction():
    """Record a new income or expense transaction."""

    print("\n--- Add Transaction ---")

    accounts = load_accounts()

    if len(accounts) == 0:
        print("\nNo accounts found. Create an account first.")
        return

    transactions = load_transactions()

    account = select_account(accounts)
    transaction_type = get_valid_transaction_type()

    if transaction_type == "Expense" and account["balance"] == 0:
        print("\nThis account has no available balance for expenses.")
        return

    amount = get_valid_amount(transaction_type, account["balance"])

    while True:
        description = input("Enter description: ").strip()

        if len(description) == 0:
            print("Description cannot be empty.")
            continue

        break

    old_balance = account["balance"]

    if transaction_type == "Income":
        new_balance = round(old_balance + amount, 2)
    else:
        new_balance = round(old_balance - amount, 2)

    account["balance"] = new_balance

    new_transaction = {
        "transaction_id": generate_transaction_id(transactions),
        "account_id": account["account_id"],
        "type": transaction_type,
        "amount": amount,
        "description": description,
        "date": str(date.today())
    }

    transactions.append(new_transaction)
    save_transactions(transactions)
    save_accounts(accounts)

    print("\nTransaction recorded successfully!")
    print(f"  ID:               {new_transaction['transaction_id']}")
    print(f"  Account:          {account['name']}")
    print(f"  Type:             {new_transaction['type']}")
    print(f"  Amount:           {format_currency(new_transaction['amount'])}")
    print(f"  Description:      {new_transaction['description']}")
    print(f"  Date:             {new_transaction['date']}")
    print(f"  Previous Balance: {format_currency(old_balance)}")
    print(f"  New Balance:      {format_currency(new_balance)}")


def view_transactions():
    """Display all transactions in a formatted table. Read-only."""

    print("\n--- View Transactions ---")

    transactions = load_transactions()

    if len(transactions) == 0:
        print("\nNo transactions found.")
        print("Please add a transaction first.")
        return

    accounts = load_accounts()

    valid_transactions = []
    invalid_count = 0

    for transaction in transactions:
        if validate_transaction(transaction):
            valid_transactions.append(transaction)
        else:
            invalid_count += 1

    if invalid_count == 1:
        print("\nSkipped 1 invalid transaction record.")
    elif invalid_count > 1:
        print(f"\nSkipped {invalid_count} invalid transaction records.")

    if len(valid_transactions) == 0:
        print("\nNo transactions found.")
        print("Please add a transaction first.")
        return

    sorted_transactions = sorted(
        valid_transactions,
        key=lambda t: (t["date"], t["transaction_id"]),
        reverse=True
    )

    display_transaction_table(sorted_transactions, accounts)

    total_income = round(sum(
        t["amount"] for t in valid_transactions if t["type"] == "Income"
    ), 2)

    total_expense = round(sum(
        t["amount"] for t in valid_transactions if t["type"] == "Expense"
    ), 2)

    print(f"\n  Total Income  : {format_currency(total_income)}")
    print(f"  Total Expense : {format_currency(total_expense)}")


def main():
    """Main menu loop."""

    print("=" * 45)
    print("   Welcome to Expense Intelligence System")
    print("=" * 45)

    while True:
        print("\n--- Main Menu ---")
        print("1. Add Account")
        print("2. View Accounts")
        print("3. Add Transaction")
        print("4. View Transactions")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_account()
        elif choice == "2":
            view_accounts()
        elif choice == "3":
            add_transaction()
        elif choice == "4":
            view_transactions()
        elif choice == "5":
            print("\nGoodbye! See you next time.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()

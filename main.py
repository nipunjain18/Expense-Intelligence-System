import json
import os
import sys
from datetime import date

# Ensure the console can display non-ASCII characters like ₹
sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = "data"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")

VALID_ACCOUNT_TYPES = ["Cash", "Bank", "UPI", "Investment", "Credit Card"]


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


def main():
    """Main menu loop."""

    print("=" * 45)
    print("   Welcome to Expense Intelligence System")
    print("=" * 45)

    while True:
        print("\n--- Main Menu ---")
        print("1. Add Account")
        print("2. View Accounts")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            add_account()
        elif choice == "2":
            view_accounts()
        elif choice == "3":
            print("\nGoodbye! See you next time.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")


if __name__ == "__main__":
    main()

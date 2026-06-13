import json
import os
from datetime import date

DATA_DIR = "data"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")

VALID_ACCOUNT_TYPES = ["Cash", "Bank", "UPI", "Investment", "Credit Card"]


def load_accounts():
    """Load all accounts from accounts.json. Returns an empty list if
    the file is missing or empty."""

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(ACCOUNTS_FILE):
        return []

    with open(ACCOUNTS_FILE, "r") as file:
        content = file.read()

    # Handle empty or whitespace-only file gracefully
    if not content.strip():
        return []

    accounts = json.loads(content)
    return accounts


def save_accounts(accounts):
    """Write the full accounts list to accounts.json."""

    with open(ACCOUNTS_FILE, "w") as file:
        json.dump(accounts, file, indent=4)


def generate_account_id(accounts):
    """Return the next account ID by incrementing the current highest ID.
    First account starts with ID 1."""

    if len(accounts) == 0:
        return 1

    all_ids = []
    for account in accounts:
        all_ids.append(account["account_id"])

    return max(all_ids) + 1


def is_duplicate_name(accounts, name):
    """Check whether an account name already exists.
    Comparison is case-insensitive so 'SBI' and 'sbi' are treated as duplicates."""

    for account in accounts:
        if account["name"].lower() == name.lower():
            return True

    return False


def get_valid_account_type():
    """Prompt the user to pick an account type from the allowed list.
    Keeps asking until a valid selection is made."""

    print("\nAvailable Account Types:")
    for i in range(len(VALID_ACCOUNT_TYPES)):
        print(f"  {i + 1}. {VALID_ACCOUNT_TYPES[i]}")

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
    """Prompt the user for a starting balance.
    Keeps asking until a non-negative number is entered."""

    while True:
        balance_input = input("Enter starting balance: ").strip()

        try:
            balance = float(balance_input)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        # Business rule: balance cannot be negative
        if balance < 0:
            print("Balance cannot be negative.")
            continue

        return balance


def add_account():
    """Walk the user through creating a new account: collect inputs,
    validate against business rules, and save to accounts.json."""

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


def main():
    """Entry point. Display the main menu in a loop until the user exits."""

    print("=" * 45)
    print("   Welcome to Expense Intelligence System")
    print("=" * 45)

    while True:
        print("\n--- Main Menu ---")
        print("1. Add Account")
        print("2. Exit")

        choice = input("Enter your choice (1 or 2): ").strip()

        if choice == "1":
            add_account()
        elif choice == "2":
            print("\nGoodbye! See you next time.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()

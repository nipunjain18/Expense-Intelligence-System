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
REQUIRED_TRANSACTION_KEYS = {"transaction_id", "account_id", "category_id", "type", "amount", "description", "date"}

CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
VALID_CATEGORY_TYPES = ["Income", "Expense"]
DEFAULT_EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Education", "Bills",
                              "Health", "Entertainment", "Subscription", "Travel", "Other Expense"]
DEFAULT_INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment Income",
                             "Gift", "Refund", "Other Income"]


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


def load_categories():
    """Return all categories from the JSON file, or [] if none exist."""

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(CATEGORIES_FILE):
        return []

    try:
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            return []

        return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_categories(categories):
    """Write the full categories list to categories.json."""

    with open(CATEGORIES_FILE, "w", encoding="utf-8") as file:
        json.dump(categories, file, indent=4)


def generate_category_id(categories):
    """Return the next category ID (highest existing + 1, starting from 1)."""

    if len(categories) == 0:
        return 1

    return max(category["category_id"] for category in categories) + 1


def ensure_default_categories():
    """Seed the system with default categories if the list is empty."""

    categories = load_categories()

    if len(categories) > 0:
        return categories

    for name in DEFAULT_EXPENSE_CATEGORIES:
        new_category = {
            "category_id": generate_category_id(categories),
            "name": name,
            "type": "Expense",
            "is_default": True,
            "is_deleted": False
        }
        categories.append(new_category)

    for name in DEFAULT_INCOME_CATEGORIES:
        new_category = {
            "category_id": generate_category_id(categories),
            "name": name,
            "type": "Income",
            "is_default": True,
            "is_deleted": False
        }
        categories.append(new_category)

    save_categories(categories)
    return categories


def view_categories():
    """Display all categories, grouped by type, sorted alphabetically."""

    print("\n--- View Categories ---")

    categories = load_categories()

    if len(categories) == 0:
        print("\nNo categories found.")
        return

    expense_categories = [c for c in categories if c["type"] == "Expense"]
    income_categories = [c for c in categories if c["type"] == "Income"]

    def sort_key(c):
        return (c["is_deleted"], c["name"].lower())

    expense_categories.sort(key=sort_key)
    income_categories.sort(key=sort_key)

    if expense_categories:
        print("\nExpense Categories:\n")
        print(f"  {'#':<4}{'Name'}")
        print("  --- --------------------")
        for i, c in enumerate(expense_categories, start=1):
            name_display = f"{c['name']} (Deleted)" if c["is_deleted"] else c["name"]
            print(f"  {i:<4}{name_display}")

    if income_categories:
        print("\nIncome Categories:\n")
        print(f"  {'#':<4}{'Name'}")
        print("  --- --------------------")
        for i, c in enumerate(income_categories, start=1):
            name_display = f"{c['name']} (Deleted)" if c["is_deleted"] else c["name"]
            print(f"  {i:<4}{name_display}")


def validate_category_name(name):
    """Trim whitespace and return None if empty, else return trimmed name."""

    trimmed = name.strip()
    if len(trimmed) == 0:
        return None
    return trimmed


def is_duplicate_category_name(categories, name, exclude_id=None):
    """Case-insensitive uniqueness check globally across active categories."""

    name_lower = name.lower()
    for c in categories:
        if c["is_deleted"]:
            continue
        if exclude_id is not None and c["category_id"] == exclude_id:
            continue
        if c["name"].lower() == name_lower:
            return True
    return False


def select_category(categories, filter_fn, empty_message):
    """Unified selection helper for categories."""

    filtered_categories = [c for c in categories if filter_fn(c)]

    if len(filtered_categories) == 0:
        print(f"\n{empty_message}")
        return None

    print("\nSelect a category:")
    for i, category in enumerate(filtered_categories, start=1):
        name_display = f"{category['name']} (Deleted)" if category["is_deleted"] else category["name"]
        print(f"  {i}. {name_display}")

    while True:
        choice = input("Enter the number of the category: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice_number = int(choice)

        if choice_number < 1 or choice_number > len(filtered_categories):
            print(f"Please enter a number between 1 and {len(filtered_categories)}.")
            continue

        return filtered_categories[choice_number - 1]


def create_category(category_type):
    """Create or restore a category of the specified type."""

    print(f"\n--- Add {category_type} Category ---")

    categories = load_categories()

    while True:
        name_input = input("Enter category name: ").strip()

        name = validate_category_name(name_input)
        if name is None:
            print("Category name cannot be empty.")
            continue

        deleted_match = None
        for c in categories:
            if c["name"].lower() == name.lower() and c["is_deleted"]:
                deleted_match = c
                break

        if deleted_match is not None:
            if deleted_match["type"] != category_type:
                print(f"Category '{name}' already exists as a deleted {deleted_match['type']} category.")
                print("New category name must be unique across all types.")
                continue

            if is_duplicate_category_name(categories, name):
                print(f"Cannot restore. Active category '{name}' already exists.")
                continue

            deleted_match["is_deleted"] = False
            save_categories(categories)
            print(f"\nCategory '{name}' restored automatically!")
            return

        if is_duplicate_category_name(categories, name):
            print(f"Category '{name}' already exists.")
            continue

        new_category = {
            "category_id": generate_category_id(categories),
            "name": name,
            "type": category_type,
            "is_default": False,
            "is_deleted": False
        }
        categories.append(new_category)
        save_categories(categories)
        print(f"\nCategory '{name}' created successfully!")
        return


def rename_category():
    """Rename a custom category."""

    print("\n--- Rename Category ---")

    categories = load_categories()

    def filter_fn(c):
        return not c["is_default"]

    category = select_category(categories, filter_fn, "No custom categories to rename.")
    if category is None:
        return

    current_name = category["name"]

    while True:
        name_input = input("Enter new name: ").strip()

        new_name = validate_category_name(name_input)
        if new_name is None:
            print("Category name cannot be empty.")
            continue

        if new_name.lower() == current_name.lower():
            print("\nNew category name must be different from current name.")
            return

        if is_duplicate_category_name(categories, new_name, exclude_id=category["category_id"]):
            print(f"Category '{new_name}' already exists.")
            continue

        category["name"] = new_name
        save_categories(categories)
        print(f"\nCategory renamed from '{current_name}' to '{new_name}'.")
        return


def delete_category():
    """Soft delete a custom category after confirmation."""

    print("\n--- Delete Category ---")

    categories = load_categories()

    def filter_fn(c):
        return not c["is_default"] and not c["is_deleted"]

    category = select_category(categories, filter_fn, "No custom categories to delete.")
    if category is None:
        return

    choice = input(f"\nDelete category '{category['name']}'? (y/n): ").strip()

    if choice.lower() == "y":
        category["is_deleted"] = True
        save_categories(categories)
        print(f"\nCategory '{category['name']}' deleted.")
    else:
        print("\nDeletion cancelled.")


def restore_category():
    """Restore a deleted category."""

    print("\n--- Restore Category ---")

    categories = load_categories()

    def filter_fn(c):
        return c["is_deleted"]

    category = select_category(categories, filter_fn, "No deleted categories to restore.")
    if category is None:
        return

    name = category["name"]

    if is_duplicate_category_name(categories, name):
        print(f"\nCannot restore. Active category '{name}' already exists.")
        return

    category["is_deleted"] = False
    save_categories(categories)
    print(f"\nCategory '{name}' restored.")


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

    if not isinstance(transaction["category_id"], int):
        return False

    return True


def get_account_name(account_id, accounts):
    """Resolve an account_id to its name, or 'Deleted Account' if not found."""

    for account in accounts:
        if account["account_id"] == account_id:
            return account["name"]

    return "Deleted Account"


def get_category_name(category_id, categories):
    """Resolve a category_id to its display name, with deleted/unknown handling."""

    for category in categories:
        if category["category_id"] == category_id:
            if category["is_deleted"]:
                return f"{category['name']} (Deleted)"
            return category["name"]

    return "Unknown Category"


def select_transaction_category(transaction_type):
    """Present active categories matching the transaction type and return the selection."""

    categories = load_categories()

    def filter_fn(c):
        return c["type"] == transaction_type and not c["is_deleted"]

    sorted_categories = sorted(categories, key=lambda c: c["name"].lower())

    return select_category(
        sorted_categories,
        filter_fn,
        f"No active {transaction_type} categories available. Please add or restore a category first."
    )


def display_transaction_table(transactions, accounts, categories):
    """Print formatted transaction table with header and rows."""

    header = f"  {'ID':<6}{'Date':<13}{'Type':<11}{'Account':<20}{'Category':<20}{'Amount':>15}  {'Description'}"
    print(f"\n{header}")
    print("  " + "-" * (len(header) - 2))

    for transaction in transactions:
        account_name = get_account_name(transaction["account_id"], accounts)
        category_name = get_category_name(transaction["category_id"], categories)
        formatted_amount = format_transaction_amount(transaction["amount"], transaction["type"])

        print(
            f"  {transaction['transaction_id']:<6}"
            f"{transaction['date']:<13}"
            f"{transaction['type']:<11}"
            f"{account_name:<20}"
            f"{category_name:<20}"
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


def _add_transaction(transaction_type):
    """Record a new transaction of the specified type (Income or Expense)."""

    print(f"\n--- Add {transaction_type} ---")

    ensure_default_categories()

    accounts = load_accounts()

    if len(accounts) == 0:
        print("\nNo accounts found. Create an account first.")
        return

    account = select_account(accounts)

    if transaction_type == "Expense" and account["balance"] == 0:
        print("\nThis account has no available balance for expenses.")
        return

    category = select_transaction_category(transaction_type)
    if category is None:
        return

    transactions = load_transactions()

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
        "category_id": category["category_id"],
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
    print(f"  Category:         {category['name']}")
    print(f"  Amount:           {format_currency(new_transaction['amount'])}")
    print(f"  Description:      {new_transaction['description']}")
    print(f"  Date:             {new_transaction['date']}")
    print(f"  Previous Balance: {format_currency(old_balance)}")
    print(f"  New Balance:      {format_currency(new_balance)}")


def add_income():
    """Entry point for adding an income transaction."""

    _add_transaction("Income")


def add_expense():
    """Entry point for adding an expense transaction."""

    _add_transaction("Expense")


def view_transactions():
    """Display all transactions in a formatted table. Read-only."""

    print("\n--- View Transactions ---")

    transactions = load_transactions()

    if len(transactions) == 0:
        print("\nNo transactions found.")
        print("Please add a transaction first.")
        return

    accounts = load_accounts()
    categories = load_categories()

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

    display_transaction_table(sorted_transactions, accounts, categories)

    total_income = round(sum(
        t["amount"] for t in valid_transactions if t["type"] == "Income"
    ), 2)

    total_expense = round(sum(
        t["amount"] for t in valid_transactions if t["type"] == "Expense"
    ), 2)

    print(f"\n  Total Income  : {format_currency(total_income)}")
    print(f"  Total Expense : {format_currency(total_expense)}")


def manage_categories():
    """Category submenu loop."""

    ensure_default_categories()

    while True:
        print("\n--- Manage Categories ---")
        print("1. View Categories")
        print("2. Add Expense Category")
        print("3. Add Income Category")
        print("4. Rename Category")
        print("5. Delete Category")
        print("6. Restore Category")
        print("7. Back to Main Menu")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            view_categories()
        elif choice == "2":
            create_category("Expense")
        elif choice == "3":
            create_category("Income")
        elif choice == "4":
            rename_category()
        elif choice == "5":
            delete_category()
        elif choice == "6":
            restore_category()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


def main():
    """Main menu loop."""

    print("=" * 45)
    print("   Welcome to Expense Intelligence System")
    print("=" * 45)

    while True:
        print("\n--- Main Menu ---")
        print("1. Add Account")
        print("2. View Accounts")
        print("3. Add Income")
        print("4. Add Expense")
        print("5. View Transactions")
        print("6. Manage Categories")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            add_account()
        elif choice == "2":
            view_accounts()
        elif choice == "3":
            add_income()
        elif choice == "4":
            add_expense()
        elif choice == "5":
            view_transactions()
        elif choice == "6":
            manage_categories()
        elif choice == "7":
            print("\nGoodbye! See you next time.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


if __name__ == "__main__":
    main()

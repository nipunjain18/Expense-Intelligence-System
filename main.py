import json
import os
import sys
from datetime import date
import copy

# Ensure the console can display non-ASCII characters like ₹
sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = "data"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")

VALID_ACCOUNT_TYPES = ["Cash", "Bank", "UPI", "Investment", "Credit Card"]

TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
VALID_TRANSACTION_TYPES = ["Income", "Expense", "Transfer"]
REQUIRED_TRANSACTION_KEYS = {"transaction_id", "account_id", "category_id", "type", "amount", "description", "date"}

CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
VALID_CATEGORY_TYPES = ["Income", "Expense"]
DEBT_LENT_CATEGORY = "Debt Lent"
DEBT_BORROWED_CATEGORY = "Debt Borrowed"
DEBT_REPAYMENT_RECEIVED_CATEGORY = "Debt Repayment Received"
DEBT_REPAYMENT_PAID_CATEGORY = "Debt Repayment Paid"

DEFAULT_EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Education", "Bills",
                              "Health", "Entertainment", "Subscription", "Travel", "Other Expense",
                              DEBT_LENT_CATEGORY, DEBT_REPAYMENT_PAID_CATEGORY]
DEFAULT_INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment Income",
                             "Gift", "Refund", "Other Income",
                             DEBT_BORROWED_CATEGORY, DEBT_REPAYMENT_RECEIVED_CATEGORY]

DEBTS_FILE = os.path.join(DATA_DIR, "debts.json")
VALID_DEBT_TYPES = ["LENT", "BORROWED"]
VALID_DEBT_STATUSES = ["ACTIVE", "CLOSED"]

REPAYMENTS_FILE = os.path.join(DATA_DIR, "repayments.json")


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


def load_debts():
    """Return all debts from the JSON file, or [] if none exist."""

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(DEBTS_FILE):
        return []

    try:
        with open(DEBTS_FILE, "r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            return []

        return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_debts(debts):
    """Write the full debts list to debts.json."""

    with open(DEBTS_FILE, "w", encoding="utf-8") as file:
        json.dump(debts, file, indent=4)


def generate_debt_id(debts):
    """Return the next debt ID."""

    if len(debts) == 0:
        return 1

    return max(debt["debt_id"] for debt in debts) + 1


def load_repayments():
    """Return all repayments from the JSON file, or [] if none exist."""

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(REPAYMENTS_FILE):
        return []

    try:
        with open(REPAYMENTS_FILE, "r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            return []

        return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_repayments(repayments):
    """Write the full repayments list to repayments.json."""

    with open(REPAYMENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(repayments, file, indent=4)


def generate_repayment_id(repayments):
    """Return the next repayment ID."""

    if len(repayments) == 0:
        return 1

    return max(repayment["repayment_id"] for repayment in repayments) + 1


def ensure_default_categories():
    """Seed the system with default categories if the list is empty."""

    categories = load_categories()
    
    changed = False

    for name in DEFAULT_EXPENSE_CATEGORIES:
        exists = any(c["name"] == name and c["type"] == "Expense" for c in categories)
        if not exists:
            new_category = {
                "category_id": generate_category_id(categories),
                "name": name,
                "type": "Expense",
                "is_default": True,
                "is_deleted": False
            }
            categories.append(new_category)
            changed = True

    for name in DEFAULT_INCOME_CATEGORIES:
        exists = any(c["name"] == name and c["type"] == "Income" for c in categories)
        if not exists:
            new_category = {
                "category_id": generate_category_id(categories),
                "name": name,
                "type": "Income",
                "is_default": True,
                "is_deleted": False
            }
            categories.append(new_category)
            changed = True

    if changed:
        save_categories(categories)
        
    return categories


def get_or_create_debt_categories():
    """Ensure debt categories exist. Creates them if they don't, even if other categories exist."""
    categories = load_categories()
    
    debt_categories_to_ensure = [
        (DEBT_LENT_CATEGORY, "Expense"),
        (DEBT_BORROWED_CATEGORY, "Income"),
        (DEBT_REPAYMENT_RECEIVED_CATEGORY, "Income"),
        (DEBT_REPAYMENT_PAID_CATEGORY, "Expense")
    ]
    
    changed = False
    for name, type_ in debt_categories_to_ensure:
        exists = any(c["name"] == name and c["type"] == type_ and not c["is_deleted"] for c in categories)
        if not exists:
            # Check if it exists but is deleted, then restore it
            restored = False
            for c in categories:
                if c["name"] == name and c["type"] == type_ and c["is_deleted"]:
                    c["is_deleted"] = False
                    restored = True
                    changed = True
                    break
            
            if not restored:
                new_category = {
                    "category_id": generate_category_id(categories),
                    "name": name,
                    "type": type_,
                    "is_default": True,
                    "is_deleted": False
                }
                categories.append(new_category)
                changed = True
                
    if changed:
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

    if transaction.get("type") not in VALID_TRANSACTION_TYPES:
        return False

    if transaction["type"] == "Transfer":
        required_keys = {"transaction_id", "type", "from_account_id", "to_account_id", "amount", "notes", "date"}
        if not required_keys.issubset(transaction.keys()):
            return False
        if not isinstance(transaction["amount"], (int, float)):
            return False
        if not isinstance(transaction["date"], str) or not transaction["date"].strip():
            return False
        if not isinstance(transaction["from_account_id"], int) or not isinstance(transaction["to_account_id"], int):
            return False
        return True

    if not REQUIRED_TRANSACTION_KEYS.issubset(transaction.keys()):
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
        is_debt_category = c["name"] in [DEBT_LENT_CATEGORY, DEBT_BORROWED_CATEGORY, DEBT_REPAYMENT_RECEIVED_CATEGORY, DEBT_REPAYMENT_PAID_CATEGORY]
        return c["type"] == transaction_type and not c["is_deleted"] and not is_debt_category

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
        if transaction["type"] == "Transfer":
            from_name = get_account_name(transaction["from_account_id"], accounts)
            to_name = get_account_name(transaction["to_account_id"], accounts)
            account_display = f"{from_name} -> {to_name}"
            category_display = "Transfer"
            formatted_amount = f"₹{transaction['amount']:,.2f}"
            description = transaction.get("notes", "")
        else:
            account_display = get_account_name(transaction["account_id"], accounts)
            category_display = get_category_name(transaction["category_id"], categories)
            formatted_amount = format_transaction_amount(transaction["amount"], transaction["type"])
            description = transaction['description']

        print(
            f"  {transaction['transaction_id']:<6}"
            f"{transaction['date']:<13}"
            f"{transaction['type']:<11}"
            f"{account_display:<20}"
            f"{category_display:<20}"
            f"{formatted_amount:>15}  "
            f"{description}"
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


def format_signed_currency(amount):
    """Format currency with a + sign for positive values."""

    if amount > 0:
        return f"+{format_currency(amount)}"

    if amount < 0:
        return f"-{format_currency(abs(amount))}"

    return format_currency(amount)


def get_valid_transactions(transactions):
    """Return only transaction records that are safe to calculate and display."""

    return [transaction for transaction in transactions if validate_transaction(transaction)]


def calculate_total_balance(accounts):
    """Return the combined balance across all accounts."""

    if not isinstance(accounts, list):
        return 0.0

    total = 0.0
    for account in accounts:
        if isinstance(account, dict) and isinstance(account.get("balance"), (int, float)):
            total += account["balance"]

    return round(total, 2)


def calculate_income_expense_summary(transactions):
    """Return total income, total expenses, and net cash flow."""

    valid_transactions = get_valid_transactions(transactions)
    total_income = 0.0
    total_expenses = 0.0
    
    for transaction in valid_transactions:
        if transaction["type"] == "Income":
            total_income += transaction["amount"]
        elif transaction["type"] == "Expense":
            total_expenses += transaction["amount"]
            
    total_income = round(total_income, 2)
    total_expenses = round(total_expenses, 2)
    net_cash_flow = round(total_income - total_expenses, 2)

    return total_income, total_expenses, net_cash_flow


def calculate_account_summary(accounts):
    """Return accounts sorted by balance from highest to lowest."""

    if not isinstance(accounts, list):
        return []
        
    valid_accounts = [
        acc for acc in accounts 
        if isinstance(acc, dict) and "name" in acc and isinstance(acc.get("balance"), (int, float))
    ]

    return sorted(valid_accounts, key=lambda account: account["balance"], reverse=True)


def calculate_debt_summary(debts):
    """Return debt totals and counts for active and closed debts."""

    total_lent_remaining = 0.0
    total_borrowed_remaining = 0.0
    active_count = 0
    closed_count = 0

    if not isinstance(debts, list):
        return 0.0, 0.0, 0, 0
        
    for debt in debts:
        if not isinstance(debt, dict):
            continue
            
        status = debt.get("status")
        debt_type = debt.get("type")
        remaining = debt.get("remaining_amount", 0)
        
        if not isinstance(remaining, (int, float)):
            remaining = 0.0
            
        if status == "ACTIVE":
            active_count += 1
            if debt_type == "LENT":
                total_lent_remaining += remaining
            elif debt_type == "BORROWED":
                total_borrowed_remaining += remaining
        elif status == "CLOSED":
            closed_count += 1

    return round(total_lent_remaining, 2), round(total_borrowed_remaining, 2), active_count, closed_count


def calculate_top_expense_categories(transactions):
    """Return the top 3 expense category totals."""

    valid_transactions = get_valid_transactions(transactions)
    category_totals = {}

    for transaction in valid_transactions:
        if transaction["type"] != "Expense":
            continue

        category_id = transaction["category_id"]
        category_totals[category_id] = round(
            category_totals.get(category_id, 0) + transaction["amount"],
            2
        )

    sorted_categories = sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return sorted_categories[:3]


def get_recent_transactions(transactions):
    """Return the latest 5 valid transactions."""

    valid_transactions = get_valid_transactions(transactions)

    return sorted(
        valid_transactions,
        key=lambda transaction: (transaction["date"], transaction["transaction_id"]),
        reverse=True
    )[:5]


def calculate_net_debt_position(total_lent_remaining, total_borrowed_remaining):
    """Return money owed to you minus money you owe."""

    return round(total_lent_remaining - total_borrowed_remaining, 2)


def show_dashboard():
    """Display a read-only high-level financial overview."""

    print("\n--- Dashboard ---")

    accounts = load_accounts()
    transactions = load_transactions()
    debts = load_debts()
    categories = load_categories()

    total_balance = calculate_total_balance(accounts)
    total_income, total_expenses, net_cash_flow = calculate_income_expense_summary(transactions)

    print("\n## Financial Overview")
    print(f"  Total Balance        : {format_currency(total_balance)}")
    print(f"  Total Account Count  : {len(accounts)}")
    print(f"  Total Income         : {format_currency(total_income)}")
    print(f"  Total Expenses       : {format_currency(total_expenses)}")
    print(f"  Net Cash Flow        : {format_signed_currency(net_cash_flow)}")

    print("\n## Account Summary")
    account_summary = calculate_account_summary(accounts)
    if len(account_summary) == 0:
        print("  No accounts found.")
    else:
        header = f"  {'Account Name':<25}{'Balance':>15}"
        print(f"\n{header}")
        print("  " + "-" * (len(header) - 2))
        for account in account_summary:
            print(f"  {account['name']:<25}{format_currency(account['balance']):>15}")

    total_lent_remaining, total_borrowed_remaining, active_debt_count, closed_debt_count = calculate_debt_summary(debts)

    print("\n## Debt Summary")
    print(f"  Total Lent Amount Remaining     : {format_currency(total_lent_remaining)}")
    print(f"  Total Borrowed Amount Remaining : {format_currency(total_borrowed_remaining)}")
    print(f"  Active Debt Count               : {active_debt_count}")
    print(f"  Closed Debt Count               : {closed_debt_count}")

    print("\n## Top Expense Categories")
    top_expense_categories = calculate_top_expense_categories(transactions)
    if len(top_expense_categories) == 0:
        print("  No expense data available.")
    else:
        header = f"  {'Category Name':<25}{'Total Amount':>15}"
        print(f"\n{header}")
        print("  " + "-" * (len(header) - 2))
        for category_id, total_amount in top_expense_categories:
            category_name = get_category_name(category_id, categories)
            print(f"  {category_name:<25}{format_currency(total_amount):>15}")

    print("\n## Recent Activity")
    recent_transactions = get_recent_transactions(transactions)
    if len(recent_transactions) == 0:
        print("  No transactions found.")
    else:
        header = f"  {'Date':<13}{'Type':<11}{'Category':<25}{'Amount':>15}"
        print(f"\n{header}")
        print("  " + "-" * (len(header) - 2))

        for transaction in recent_transactions:
            if transaction["type"] == "Transfer":
                from_name = get_account_name(transaction["from_account_id"], accounts)
                to_name = get_account_name(transaction["to_account_id"], accounts)
                category_display = f"{from_name} -> {to_name}"
                formatted_amount = f"₹{transaction['amount']:,.2f}"
            else:
                category_display = get_category_name(transaction["category_id"], categories)
                formatted_amount = format_transaction_amount(transaction["amount"], transaction["type"])

            print(
                f"  {transaction['date']:<13}"
                f"{transaction['type']:<11}"
                f"{category_display:<25}"
                f"{formatted_amount:>15}"
            )

    net_debt_position = calculate_net_debt_position(total_lent_remaining, total_borrowed_remaining)

    print("\n## Net Debt Position")
    print(f"  Money Owed To You : {format_currency(total_lent_remaining)}")
    print(f"  Money You Owe     : {format_currency(total_borrowed_remaining)}")
    print(f"  Net Position      : {format_signed_currency(net_debt_position)}")


def find_active_debts_by_person(debts, person_name):
    name_lower = person_name.strip().lower()
    return [d for d in debts if d["person_name"].strip().lower() == name_lower and d["status"] == "ACTIVE"]


def create_debt_transaction(transactions, account, debt_type, amount, person_name, purpose, date_str):
    categories = get_or_create_debt_categories()
    if debt_type == "LENT":
        trans_type = "Expense"
        category_name = DEBT_LENT_CATEGORY
        account["balance"] = round(account["balance"] - amount, 2)
    else:
        trans_type = "Income"
        category_name = DEBT_BORROWED_CATEGORY
        account["balance"] = round(account["balance"] + amount, 2)
        
    category_id = next(c["category_id"] for c in categories if c["name"] == category_name and c["type"] == trans_type and not c["is_deleted"])
    
    desc_suffix = f" - {purpose}" if purpose else ""
    new_transaction = {
        "transaction_id": generate_transaction_id(transactions),
        "account_id": account["account_id"],
        "category_id": category_id,
        "type": trans_type,
        "amount": amount,
        "description": f"Debt {debt_type} - {person_name}{desc_suffix}",
        "date": date_str
    }
    transactions.append(new_transaction)
    return new_transaction["transaction_id"]


def create_repayment_transaction(transactions, account, selected_debt, amount, date_str):
    categories = get_or_create_debt_categories()
    if selected_debt["type"] == "LENT":
        trans_type = "Income"
        category_name = DEBT_REPAYMENT_RECEIVED_CATEGORY
        account["balance"] = round(account["balance"] + amount, 2)
    else:
        trans_type = "Expense"
        category_name = DEBT_REPAYMENT_PAID_CATEGORY
        account["balance"] = round(account["balance"] - amount, 2)
        
    category_id = next(c["category_id"] for c in categories if c["name"] == category_name and c["type"] == trans_type and not c["is_deleted"])
    
    new_transaction = {
        "transaction_id": generate_transaction_id(transactions),
        "account_id": account["account_id"],
        "category_id": category_id,
        "type": trans_type,
        "amount": amount,
        "description": f"Repayment for Debt {selected_debt['type']} - {selected_debt['person_name']}",
        "date": date_str
    }
    transactions.append(new_transaction)
    return new_transaction["transaction_id"]


def update_debt_status(debt):
    if debt["remaining_amount"] == 0:
        debt["status"] = "CLOSED"
    else:
        debt["status"] = "ACTIVE"



def add_debt():
    print("\n--- Add New Debt ---")
    get_or_create_debt_categories()
    
    accounts = load_accounts()
    if len(accounts) == 0:
        print("\nNo accounts found. Create an account first.")
        return
        
    print("\nDebt Types:")
    for i, t in enumerate(VALID_DEBT_TYPES, start=1):
        print(f"  {i}. {t}")
        
    while True:
        choice = input("Enter the number of your debt type: ").strip()
        if choice == "1":
            debt_type = "LENT"
            break
        elif choice == "2":
            debt_type = "BORROWED"
            break
        else:
            print("Invalid choice.")
            
    account = select_account(accounts)
    
    if debt_type == "LENT" and account["balance"] == 0:
        print("\nThis account has no available balance for lending.")
        return
        
    debts = load_debts()
    
    while True:
        person_name = input("Enter person name: ").strip()
        if not person_name:
            print("Person name cannot be empty.")
            continue
            
        active_debts = find_active_debts_by_person(debts, person_name)
        if active_debts:
            print(f"\nWarning: Active debt(s) already exist for '{person_name}'.")
            for d in active_debts:
                print(f"  - {d['type']} | Remaining: {format_currency(d['remaining_amount'])} | Created: {d['created_date']}")
            print("\nOptions:")
            print("  1. Create New Debt")
            print("  2. Cancel")
            action = input("Choose option (1-2): ").strip()
            if action != "1":
                print("Cancelled.")
                return
        break
        
    amount = get_valid_amount("Expense" if debt_type == "LENT" else "Income", account["balance"])
    
    purpose = input("Enter purpose (optional): ").strip()
    notes = input("Enter notes (optional): ").strip()
    
    date_str = input(f"Enter date (YYYY-MM-DD) [default {date.today()}]: ").strip()
    if not date_str:
        date_str = str(date.today())
    else:
        try:
            date.fromisoformat(date_str)
        except ValueError:
            print("Invalid date format. Using today's date.")
            date_str = str(date.today())
            
    transactions = load_transactions()
    
    transaction_id = create_debt_transaction(
        transactions, account, debt_type, amount, person_name, purpose, date_str
    )
    
    new_debt = {
        "debt_id": generate_debt_id(debts),
        "transaction_id": transaction_id,
        "account_id": account["account_id"],
        "person_name": person_name,
        "type": debt_type,
        "status": "ACTIVE",
        "original_amount": amount,
        "remaining_amount": amount,
        "purpose": purpose,
        "notes": notes,
        "created_date": date_str
    }
    debts.append(new_debt)
    
    save_transactions(transactions)
    save_accounts(accounts)
    save_debts(debts)
    
    print("\nDebt recorded successfully!")


def view_debts():
    print("\n--- View Debts ---")
    debts = load_debts()
    
    if len(debts) == 0:
        print("\nNo debts found.")
        return
        
    active_debts = [d for d in debts if d["status"] == "ACTIVE"]
    closed_debts = [d for d in debts if d["status"] == "CLOSED"]
    
    accounts = load_accounts()
    
    def display_debts_table(debt_list):
        header = f"  {'ID':<6}{'Date':<13}{'Person':<15}{'Type':<11}{'Account':<15}{'Remaining':>12}{'Original':>12}  {'Purpose'}"
        print(f"\n{header}")
        print("  " + "-" * (len(header) - 2))
        for d in debt_list:
            account_name = get_account_name(d["account_id"], accounts)
            p_name = d["person_name"][:13] + ".." if len(d["person_name"]) > 15 else d["person_name"]
            acct_name = account_name[:13] + ".." if len(account_name) > 15 else account_name
            rem_amt = format_currency(d["remaining_amount"])
            orig_amt = format_currency(d["original_amount"])
            print(f"  {d['debt_id']:<6}{d['created_date']:<13}{p_name:<15}{d['type']:<11}{acct_name:<15}{rem_amt:>12}{orig_amt:>12}  {d['purpose']}")
            if d.get('notes'):
                print(f"  {'':<76}Notes: {d['notes']}")

    if active_debts:
        print("\n## Active Debts")
        display_debts_table(active_debts)
    else:
        print("\n## Active Debts\n  None.")
        
    if closed_debts:
        print("\n## Closed Debts")
        display_debts_table(closed_debts)

def add_repayment():
    print("\n--- Record Repayment ---")
    debts = load_debts()
    active_debts = [d for d in debts if d["status"] == "ACTIVE"]
    
    if not active_debts:
        print("\nNo active debts found.")
        return
        
    print("\nSelect Active Debt:")
    for i, d in enumerate(active_debts, start=1):
        print(f"  {i}. {d['person_name']} | {d['type']} | Remaining: {format_currency(d['remaining_amount'])} | Created: {d['created_date']}")
        
    while True:
        choice = input("Enter the number of the debt: ").strip()
        if not choice.isdigit():
            print("Please enter a valid number.")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(active_debts):
            selected_debt = active_debts[idx]
            break
        print("Invalid selection.")
        
    accounts = load_accounts()
    if not accounts:
        print("\nNo accounts found.")
        return
        
    account = select_account(accounts)
    
    date_str = input(f"Enter repayment date (YYYY-MM-DD) [default {date.today()}]: ").strip()
    if not date_str:
        date_str = str(date.today())
    else:
        try:
            date.fromisoformat(date_str)
        except ValueError:
            print("Invalid date format. Using today's date.")
            date_str = str(date.today())
            
    repayment_date = date.fromisoformat(date_str)
    debt_date = date.fromisoformat(selected_debt["created_date"])
    
    if repayment_date < debt_date:
        print(f"\nError: Repayment date ({date_str}) cannot be earlier than debt creation date ({selected_debt['created_date']}).")
        return
        
    while True:
        amount_str = input("Enter repayment amount: ").strip()
        try:
            amount = float(amount_str)
        except ValueError:
            print("Invalid amount.")
            continue
            
        if amount <= 0:
            print("Amount must be greater than zero.")
            continue
            
        if amount > selected_debt["remaining_amount"]:
            print(f"\nOverpayment detected. Remaining debt is only {format_currency(selected_debt['remaining_amount'])}.")
            print("1. Record exact remaining amount only")
            print("2. Cancel")
            action = input("Choose option (1-2): ").strip()
            if action == "1":
                amount = selected_debt["remaining_amount"]
                break
            else:
                print("Cancelled.")
                return
                
        # Optional: block paying back if balance < amount
        if selected_debt["type"] == "BORROWED" and amount > account["balance"]:
            print(f"\nError: Insufficient balance in {account['name']} to pay {format_currency(amount)}.")
            return

        break
        
    transactions = load_transactions()
    
    transaction_id = create_repayment_transaction(
        transactions, account, selected_debt, amount, date_str
    )
    
    repayments = load_repayments()
    new_repayment = {
        "repayment_id": generate_repayment_id(repayments),
        "debt_id": selected_debt["debt_id"],
        "transaction_id": transaction_id,
        "account_id": account["account_id"],
        "amount": amount,
        "date": date_str
    }
    repayments.append(new_repayment)
    
    selected_debt["remaining_amount"] = round(selected_debt["remaining_amount"] - amount, 2)
    update_debt_status(selected_debt)
        
    save_transactions(transactions)
    save_accounts(accounts)
    save_debts(debts)
    save_repayments(repayments)
    
    print("\nRepayment recorded successfully!")

def delete_linked_transaction(transaction_id):
    transactions = load_transactions()
    accounts = load_accounts()
    
    trans_to_delete = None
    for i, t in enumerate(transactions):
        if t["transaction_id"] == transaction_id:
            trans_to_delete = t
            del transactions[i]
            break
            
    if trans_to_delete:
        for account in accounts:
            if account["account_id"] == trans_to_delete["account_id"]:
                if trans_to_delete["type"] == "Income":
                    account["balance"] = round(account["balance"] - trans_to_delete["amount"], 2)
                else:
                    account["balance"] = round(account["balance"] + trans_to_delete["amount"], 2)
                break
        save_transactions(transactions)
        save_accounts(accounts)

def delete_repayment():
    print("\n--- Delete Repayment ---")
    repayments = load_repayments()
    if not repayments:
        print("\nNo repayments found.")
        return
        
    debts = load_debts()
    
    print("\nSelect Repayment to Delete:")
    for i, r in enumerate(repayments, start=1):
        debt = next((d for d in debts if d["debt_id"] == r["debt_id"]), None)
        d_info = f"Debt {debt['type']} - {debt['person_name']}" if debt else "Unknown Debt"
        print(f"  {i}. {r['date']} | {format_currency(r['amount'])} | {d_info}")
        
    while True:
        choice = input("Enter the number of the repayment: ").strip()
        if not choice.isdigit():
            print("Please enter a valid number.")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(repayments):
            selected_rep = repayments.pop(idx)
            break
        print("Invalid selection.")
        
    confirm = input(f"Are you sure you want to delete repayment of {format_currency(selected_rep['amount'])}? (y/n): ").strip()
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return
        
    delete_linked_transaction(selected_rep["transaction_id"])
    
    debt = next((d for d in debts if d["debt_id"] == selected_rep["debt_id"]), None)
    if debt:
        debt["remaining_amount"] = round(debt["remaining_amount"] + selected_rep["amount"], 2)
        if debt["remaining_amount"] > debt["original_amount"]:
            debt["remaining_amount"] = debt["original_amount"]
        if debt["status"] == "CLOSED":
            debt["status"] = "ACTIVE"
            
    save_debts(debts)
    save_repayments(repayments)
    print("\nRepayment deleted successfully.")

def delete_debt():
    print("\n--- Delete Debt ---")
    debts = load_debts()
    if not debts:
        print("\nNo debts found.")
        return
        
    repayments = load_repayments()
    
    print("\nSelect Debt to Delete:")
    for i, d in enumerate(debts, start=1):
        print(f"  {i}. {d['person_name']} | {d['type']} | {d['status']} | Orig: {format_currency(d['original_amount'])}")
        
    while True:
        choice = input("Enter the number of the debt: ").strip()
        if not choice.isdigit():
            print("Please enter a valid number.")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(debts):
            selected_debt = debts[idx]
            break
        print("Invalid selection.")
        
    has_repayments = any(r["debt_id"] == selected_debt["debt_id"] for r in repayments)
    if has_repayments:
        print("\nError: Cannot delete debt with repayment history. Delete repayments first.")
        return
        
    confirm = input("Are you sure you want to delete this debt? (y/n): ").strip()
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return
        
    delete_linked_transaction(selected_debt["transaction_id"])
    
    debts.remove(selected_debt)
    save_debts(debts)
    print("\nDebt deleted successfully.")

def view_repayments():
    print("\n--- View Repayments ---")
    repayments = load_repayments()
    if not repayments:
        print("\nNo repayments found.")
        return
        
    debts = load_debts()
    accounts = load_accounts()
    
    header = f"  {'RepID':<7}{'Date':<13}{'Person':<15}{'Type':<11}{'Amount':>12}  {'Account':<15}{'DebtID'}"
    print(f"\n{header}")
    print("  " + "-" * (len(header) - 2))
    
    for r in repayments:
        debt = next((d for d in debts if d["debt_id"] == r["debt_id"]), None)
        account_name = get_account_name(r["account_id"], accounts)
        
        p_name = debt["person_name"][:13] + ".." if debt and len(debt["person_name"]) > 15 else (debt["person_name"] if debt else "Unknown")
        d_type = debt["type"] if debt else "Unknown"
        acct_name = account_name[:13] + ".." if len(account_name) > 15 else account_name
        amt = format_currency(r["amount"])
        
        print(f"  {r['repayment_id']:<7}{r['date']:<13}{p_name:<15}{d_type:<11}{amt:>12}  {acct_name:<15}{r['debt_id']}")

def manage_debts():
    """Debt tracking submenu."""
    while True:
        print("\n--- Manage Debts ---")
        print("1. View Debts")
        print("2. View Repayments")
        print("3. Add Debt")
        print("4. Record Repayment")
        print("5. Delete Repayment")
        print("6. Delete Debt")
        print("7. Back to Main Menu")
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            view_debts()
        elif choice == "2":
            view_repayments()
        elif choice == "3":
            add_debt()
        elif choice == "4":
            add_repayment()
        elif choice == "5":
            delete_repayment()
        elif choice == "6":
            delete_debt()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


def is_account_referenced_by_transfers(account_id):
    """Helper for future feature: check if an account is part of any transfer."""
    transactions = load_transactions()
    for t in transactions:
        if t["type"] == "Transfer":
            if t["from_account_id"] == account_id or t["to_account_id"] == account_id:
                return True
    return False


def transfer_money():
    """Transfer money between two different accounts."""
    print("\n--- Transfer Money ---")
    
    accounts = load_accounts()
    if len(accounts) < 2:
        print("\nYou need at least two accounts to make a transfer.")
        return
        
    print("\nSelect Source Account:")
    from_account = select_account(accounts)
    
    print("\nSelect Destination Account:")
    to_account = select_account(accounts)
    
    if from_account["account_id"] == to_account["account_id"]:
        print("\nError: Source and destination accounts must be different.")
        return
        
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
            
        if from_account["account_type"] != "Credit Card" and amount > from_account["balance"]:
            print(f"Error: Insufficient balance in {from_account['name']}. Available: {format_currency(from_account['balance'])}.")
            continue
            
        break
        
    while True:
        date_str = input(f"Enter date (YYYY-MM-DD) [default {date.today()}]: ").strip()
        if not date_str:
            date_str = str(date.today())
            break
        try:
            parsed_date = date.fromisoformat(date_str)
            if parsed_date > date.today():
                print("Error: Transfer date cannot be in the future. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid date format. Please try again.")
            
    notes = input("Enter notes (optional): ").strip()
    
    print("\n--- Transfer Summary ---")
    print(f"From: {from_account['name']}")
    print(f"To: {to_account['name']}")
    print(f"Amount: {format_currency(amount)}")
    print(f"Date: {date_str}")
    if notes:
        print(f"Notes: {notes}")
        
    confirm = input("\nConfirm Transfer? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print("\nTransfer cancelled. No changes were made.")
        return
        
    old_accounts = copy.deepcopy(accounts)
    transactions = load_transactions()
    old_transactions = copy.deepcopy(transactions)

    # Execute transfer atomically
    from_account["balance"] = round(from_account["balance"] - amount, 2)
    to_account["balance"] = round(to_account["balance"] + amount, 2)
    
    new_transaction = {
        "transaction_id": generate_transaction_id(transactions),
        "type": "Transfer",
        "from_account_id": from_account["account_id"],
        "to_account_id": to_account["account_id"],
        "amount": amount,
        "date": date_str,
        "notes": notes
    }
    
    transactions.append(new_transaction)
    
    # Save all updates
    try:
        save_transactions(transactions)
        save_accounts(accounts)
        print("\nTransfer executed successfully!")
    except Exception as e:
        save_transactions(old_transactions)
        save_accounts(old_accounts)
        print(f"\nSystem error during transfer: {e}")
        print("Transfer aborted. No changes were saved.")


def delete_transfer():
    """Delete a transfer and safely reverse balances."""
    print("\n--- Delete Transfer ---")
    
    transactions = load_transactions()
    transfers = [t for t in transactions if t["type"] == "Transfer"]
    
    if not transfers:
        print("\nNo transfers found.")
        return
        
    accounts = load_accounts()
    
    print("\nSelect Transfer to Delete:")
    header = f"  {'ID':<6}{'Date':<13}{'Account':<30}{'Amount':>15}  {'Notes'}"
    print(f"\n{header}")
    print("  " + "-" * (len(header) - 2))
    
    # Sort for display, latest first
    sorted_transfers = sorted(transfers, key=lambda t: (t["date"], t["transaction_id"]), reverse=True)
    
    for i, t in enumerate(sorted_transfers, start=1):
        from_name = get_account_name(t["from_account_id"], accounts)
        to_name = get_account_name(t["to_account_id"], accounts)
        acc_display = f"{from_name} -> {to_name}"
        if len(acc_display) > 28:
            acc_display = acc_display[:26] + ".."
        notes_display = t.get("notes", "")
        formatted_amount = f"₹{t['amount']:,.2f}"
        print(f"  {i:<4}. {t['date']:<13}{acc_display:<30}{formatted_amount:>15}  {notes_display}")
        
    while True:
        choice = input("\nEnter the number of the transfer to delete: ").strip()
        if not choice.isdigit():
            print("Please enter a valid number.")
            continue
            
        idx = int(choice) - 1
        if 0 <= idx < len(sorted_transfers):
            selected_transfer = sorted_transfers[idx]
            break
        print("Invalid selection.")
        
    from_account = next((a for a in accounts if a["account_id"] == selected_transfer["from_account_id"]), None)
    to_account = next((a for a in accounts if a["account_id"] == selected_transfer["to_account_id"]), None)
    
    if to_account and to_account["account_type"] != "Credit Card":
        if to_account["balance"] < selected_transfer["amount"]:
            print(f"\nError: Cannot reverse transfer. Reversal would create an invalid negative balance in {to_account['name']}.")
            print(f"Current balance: {format_currency(to_account['balance'])}, Transfer amount: {format_currency(selected_transfer['amount'])}")
            return
            
    confirm = input(f"\nDelete Transfer #{selected_transfer['transaction_id']}? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print("\nDeletion cancelled.")
        return
        
    old_accounts = copy.deepcopy(accounts)
    old_transactions = copy.deepcopy(transactions)

    # Reverse balances
    if from_account:
        from_account["balance"] = round(from_account["balance"] + selected_transfer["amount"], 2)
    if to_account:
        to_account["balance"] = round(to_account["balance"] - selected_transfer["amount"], 2)
        
    # Remove transaction
    for idx_t, t in enumerate(transactions):
        if t["transaction_id"] == selected_transfer["transaction_id"]:
            del transactions[idx_t]
            break
    
    try:
        save_transactions(transactions)
        save_accounts(accounts)
        print("\nTransfer deleted and balances reversed successfully.")
    except Exception as e:
        save_transactions(old_transactions)
        save_accounts(old_accounts)
        print(f"\nSystem error during deletion: {e}")
        print("Deletion aborted. No changes were saved.")


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
        print("5. Transfer Money")
        print("6. View Transactions")
        print("7. Manage Categories")
        print("8. Debt Tracking")
        print("9. Dashboard")
        print("10. Delete Transfer")
        print("11. Exit")

        choice = input("Enter your choice (1-11): ").strip()

        if choice == "1":
            add_account()
        elif choice == "2":
            view_accounts()
        elif choice == "3":
            add_income()
        elif choice == "4":
            add_expense()
        elif choice == "5":
            transfer_money()
        elif choice == "6":
            view_transactions()
        elif choice == "7":
            manage_categories()
        elif choice == "8":
            manage_debts()
        elif choice == "9":
            show_dashboard()
        elif choice == "10":
            delete_transfer()
        elif choice == "11":
            print("\nGoodbye! See you next time.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 11.")


if __name__ == "__main__":
    main()

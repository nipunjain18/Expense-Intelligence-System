import json
import os
import sys
from datetime import date
import copy
import math

sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = "data"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")

VALID_ACCOUNT_TYPES = ["Cash", "Bank", "UPI", "Investment", "Credit Card"]

TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
VALID_TRANSACTION_TYPES = ["Income", "Expense", "Transfer"]
REQUIRED_TRANSACTION_KEYS = {"transaction_id", "account_id", "category_id", "type", "amount", "description", "date"}

CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
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

REPAYMENTS_FILE = os.path.join(DATA_DIR, "repayments.json")


def load_json_file(filepath):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            return []

        return json.loads(content)
    except json.JSONDecodeError:
        print(f"\nWarning: {os.path.basename(filepath)} contains invalid JSON.")
        print("Loading empty dataset.")
        return []
    except OSError as e:
        print(f"\nWarning: Error reading {os.path.basename(filepath)}: {e}")
        print("Loading empty dataset.")
        return []


def load_accounts():
    return load_json_file(ACCOUNTS_FILE)


def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def generate_id(items, id_key):
    if len(items) == 0:
        return 1

    return max(item[id_key] for item in items) + 1


def select_from_list(items, prompt, display_func=None):
    if not items:
        print("\nNo items available.")
        return None
        
    for i, item in enumerate(items, start=1):
        if display_func:
            print(f"  {i}. {display_func(item)}")
        else:
            print(f"  {i}. {item}")
            
    while True:
        choice = input(f"{prompt} ").strip()
        if not choice.isdigit():
            print("Please enter a valid number.")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx]
        print("Invalid selection.")


def load_transactions():
    return load_json_file(TRANSACTIONS_FILE)


def load_categories():
    return load_json_file(CATEGORIES_FILE)


def load_debts():
    return load_json_file(DEBTS_FILE)


def load_repayments():
    return load_json_file(REPAYMENTS_FILE)


def _ensure_category_exists(categories, name, category_type, is_default=True):
    for c in categories:
        if c["name"] == name and c["type"] == category_type and not c["is_deleted"]:
            return False
            
    for c in categories:
        if c["name"] == name and c["type"] == category_type and c["is_deleted"]:
            c["is_deleted"] = False
            return True
            
    new_category = {
        "category_id": generate_id(categories, "category_id"),
        "name": name,
        "type": category_type,
        "is_default": is_default,
        "is_deleted": False
    }
    categories.append(new_category)
    return True


def ensure_default_categories():
    categories = load_categories()
    
    changed = False

    for name in DEFAULT_EXPENSE_CATEGORIES:
        if _ensure_category_exists(categories, name, "Expense"):
            changed = True

    for name in DEFAULT_INCOME_CATEGORIES:
        if _ensure_category_exists(categories, name, "Income"):
            changed = True

    if changed:
        save_json_file(CATEGORIES_FILE, categories)
        
    return categories


def get_or_create_debt_categories():
    categories = load_categories()
    
    debt_categories_to_ensure = [
        (DEBT_LENT_CATEGORY, "Expense"),
        (DEBT_BORROWED_CATEGORY, "Income"),
        (DEBT_REPAYMENT_RECEIVED_CATEGORY, "Income"),
        (DEBT_REPAYMENT_PAID_CATEGORY, "Expense")
    ]
    
    changed = False
    for name, type_ in debt_categories_to_ensure:
        if _ensure_category_exists(categories, name, type_):
            changed = True
                
    if changed:
        save_json_file(CATEGORIES_FILE, categories)
    
    return categories


def view_categories():
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
    trimmed = name.strip()
    if len(trimmed) == 0:
        return None
    return trimmed


def is_duplicate_category_name(categories, name, exclude_id=None):
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
            save_json_file(CATEGORIES_FILE, categories)
            print(f"\nCategory '{name}' restored automatically!")
            return

        if is_duplicate_category_name(categories, name):
            print(f"Category '{name}' already exists.")
            continue

        new_category = {
            "category_id": generate_id(categories, "category_id"),
            "name": name,
            "type": category_type,
            "is_default": False,
            "is_deleted": False
        }
        categories.append(new_category)
        save_json_file(CATEGORIES_FILE, categories)
        print(f"\nCategory '{name}' created successfully!")
        return


def rename_category():
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
        save_json_file(CATEGORIES_FILE, categories)
        print(f"\nCategory renamed from '{current_name}' to '{new_name}'.")
        return


def delete_category():
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
        save_json_file(CATEGORIES_FILE, categories)
        print(f"\nCategory '{category['name']}' deleted.")
    else:
        print("\nDeletion cancelled.")


def restore_category():
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
    save_json_file(CATEGORIES_FILE, categories)
    print(f"\nCategory '{name}' restored.")


def is_duplicate_name(accounts, name):
    for account in accounts:
        if account["name"].lower() == name.lower():
            return True

    return False


def get_valid_account_type():
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
    while True:
        balance_input = input("Enter starting balance: ").strip()

        try:
            balance = float(balance_input)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if not math.isfinite(balance):
            print("Invalid balance. Please enter a finite number.")
            continue

        if balance < 0:
            print("Balance cannot be negative.")
            continue

        return balance


def get_valid_date(prompt_suffix="", min_date=None):
    # Date validation
    today = date.today()
    prompt = f"Enter date (YYYY-MM-DD) [default {today}]{prompt_suffix}: "

    while True:
        date_input = input(prompt).strip()

        if not date_input:
            return str(today)

        try:
            parsed = date.fromisoformat(date_input)
        except ValueError:
            print("Invalid date format. Please enter a date in YYYY-MM-DD format.")
            continue

        if parsed > today:
            print(f"Error: Date cannot be in the future. Today is {today}.")
            continue

        if min_date is not None and parsed < min_date:
            print(f"Error: Date cannot be earlier than the debt creation date ({min_date}).")
            continue

        return date_input


def select_account(accounts):
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



def get_valid_amount(transaction_type, balance):
    while True:
        amount_input = input("Enter amount: ").strip()

        try:
            amount = float(amount_input)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if not math.isfinite(amount):
            print("Invalid amount. Please enter a finite number.")
            continue

        if amount <= 0:
            print("Amount must be greater than zero.")
            continue

        if transaction_type == "Expense" and amount > balance:
            print("Insufficient balance.")
            continue

        return amount


def add_account():
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
        "account_id": generate_id(accounts, "account_id"),
        "name": name,
        "account_type": account_type,
        "balance": balance,
        "created_at": str(date.today())
    }

    accounts.append(new_account)
    save_json_file(ACCOUNTS_FILE, accounts)

    print(f"\nAccount '{name}' created successfully!")
    print(f"  ID:      {new_account['account_id']}")
    print(f"  Type:    {new_account['account_type']}")
    print(f"  Balance: {new_account['balance']}")
    print(f"  Date:    {new_account['created_at']}")


def format_currency(amount):
    return f"₹{amount:,.2f}"


def format_transaction_amount(amount, transaction_type):
    if transaction_type == "Income":
        return f"+₹{amount:,.2f}"

    return f"-₹{amount:,.2f}"


def validate_transaction(transaction):
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
    for account in accounts:
        if account["account_id"] == account_id:
            return account["name"]

    return "Deleted Account"


def get_category_name(category_id, categories):
    for category in categories:
        if category["category_id"] == category_id:
            if category["is_deleted"]:
                return f"{category['name']} (Deleted)"
            return category["name"]

    return "Unknown Category"


def select_transaction_category(transaction_type):
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
    total_accounts = len(accounts)
    total_balance = sum(account["balance"] for account in accounts)

    print(f"\n  Total Accounts : {total_accounts}")
    print(f"  Total Balance  : {format_currency(total_balance)}")


def view_accounts():
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

    old_transactions = copy.deepcopy(transactions)
    old_accounts = copy.deepcopy(accounts)

    account["balance"] = new_balance

    new_transaction = {
        "transaction_id": generate_id(transactions, "transaction_id"),
        "account_id": account["account_id"],
        "category_id": category["category_id"],
        "type": transaction_type,
        "amount": amount,
        "description": description,
        "date": str(date.today())
    }

    transactions.append(new_transaction)

    try:
        save_json_file(TRANSACTIONS_FILE, transactions)
        save_json_file(ACCOUNTS_FILE, accounts)
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
    except Exception as e:
        try:
            save_json_file(TRANSACTIONS_FILE, old_transactions)
            save_json_file(ACCOUNTS_FILE, old_accounts)
        except Exception as rollback_error:
            print("\nCRITICAL SYSTEM ERROR")
            print(f"Original Error: {e}")
            print(f"Rollback Error: {rollback_error}")
            print("Application could not guarantee data consistency.")
            print("Please restore from backup and inspect data files.")
            
        print(f"\nSystem error during transaction creation: {e}")
        print("Transaction creation aborted. No changes were saved.")


def add_income():
    _add_transaction("Income")


def add_expense():
    _add_transaction("Expense")


def view_transactions():
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
    if amount > 0:
        return f"+{format_currency(amount)}"

    if amount < 0:
        return f"-{format_currency(abs(amount))}"

    return format_currency(amount)


def get_valid_transactions(transactions):
    return [transaction for transaction in transactions if validate_transaction(transaction)]


def calculate_total_balance(accounts):
    if not isinstance(accounts, list):
        return 0.0

    total = 0.0
    for account in accounts:
        if isinstance(account, dict) and isinstance(account.get("balance"), (int, float)):
            total += account["balance"]

    return round(total, 2)


def calculate_income_expense_summary(transactions):
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
    if not isinstance(accounts, list):
        return []
        
    valid_accounts = [
        acc for acc in accounts 
        if isinstance(acc, dict) and "name" in acc and isinstance(acc.get("balance"), (int, float))
    ]

    return sorted(valid_accounts, key=lambda account: account["balance"], reverse=True)


def calculate_debt_summary(debts):
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
    valid_transactions = get_valid_transactions(transactions)

    return sorted(
        valid_transactions,
        key=lambda transaction: (transaction["date"], transaction["transaction_id"]),
        reverse=True
    )[:5]


def calculate_net_debt_position(total_lent_remaining, total_borrowed_remaining):
    return round(total_lent_remaining - total_borrowed_remaining, 2)


def _display_financial_overview(total_balance, account_count, total_income, total_expenses, net_cash_flow):
    print("\n## Financial Overview")
    print(f"  Total Balance        : {format_currency(total_balance)}")
    print(f"  Total Account Count  : {account_count}")
    print(f"  Total Income         : {format_currency(total_income)}")
    print(f"  Total Expenses       : {format_currency(total_expenses)}")
    print(f"  Net Cash Flow        : {format_signed_currency(net_cash_flow)}")


def _display_account_summary(accounts):
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


def _display_debt_summary(total_lent_remaining, total_borrowed_remaining, active_debt_count, closed_debt_count):
    print("\n## Debt Summary")
    print(f"  Total Lent Amount Remaining     : {format_currency(total_lent_remaining)}")
    print(f"  Total Borrowed Amount Remaining : {format_currency(total_borrowed_remaining)}")
    print(f"  Active Debt Count               : {active_debt_count}")
    print(f"  Closed Debt Count               : {closed_debt_count}")


def _display_top_expense_categories(transactions, categories):
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


def _display_recent_activity(transactions, accounts, categories):
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


def _display_net_debt_position(total_lent_remaining, total_borrowed_remaining):
    net_debt_position = calculate_net_debt_position(total_lent_remaining, total_borrowed_remaining)

    print("\n## Net Debt Position")
    print(f"  Money Owed To You : {format_currency(total_lent_remaining)}")
    print(f"  Money You Owe     : {format_currency(total_borrowed_remaining)}")
    print(f"  Net Position      : {format_signed_currency(net_debt_position)}")


def show_dashboard():
    print("\n--- Dashboard ---")

    accounts = load_accounts()
    transactions = load_transactions()
    debts = load_debts()
    categories = load_categories()

    total_balance = calculate_total_balance(accounts)
    total_income, total_expenses, net_cash_flow = calculate_income_expense_summary(transactions)

    _display_financial_overview(total_balance, len(accounts), total_income, total_expenses, net_cash_flow)
    _display_account_summary(accounts)

    total_lent_remaining, total_borrowed_remaining, active_debt_count, closed_debt_count = calculate_debt_summary(debts)
    _display_debt_summary(total_lent_remaining, total_borrowed_remaining, active_debt_count, closed_debt_count)

    _display_top_expense_categories(transactions, categories)
    _display_recent_activity(transactions, accounts, categories)
    _display_net_debt_position(total_lent_remaining, total_borrowed_remaining)


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
        "transaction_id": generate_id(transactions, "transaction_id"),
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
        "transaction_id": generate_id(transactions, "transaction_id"),
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



def _get_valid_debt_type():
    print("\nDebt Types:")
    for i, t in enumerate(VALID_DEBT_TYPES, start=1):
        print(f"  {i}. {t}")
        
    while True:
        choice = input("Enter the number of your debt type: ").strip()
        if choice == "1":
            return "LENT"
        elif choice == "2":
            return "BORROWED"
        else:
            print("Invalid choice.")


def _get_valid_person_name(debts):
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
                return None
        return person_name


def add_debt():
    print("\n--- Add New Debt ---")
    get_or_create_debt_categories()
    
    accounts = load_accounts()
    if len(accounts) == 0:
        print("\nNo accounts found. Create an account first.")
        return
        
    debt_type = _get_valid_debt_type()
            
    account = select_account(accounts)
    
    if debt_type == "LENT" and account["balance"] == 0:
        print("\nThis account has no available balance for lending.")
        return
        
    debts = load_debts()
    
    person_name = _get_valid_person_name(debts)
    if not person_name:
        return
        
    amount = get_valid_amount("Expense" if debt_type == "LENT" else "Income", account["balance"])
    
    purpose = input("Enter purpose (optional): ").strip()
    notes = input("Enter notes (optional): ").strip()
    
    date_str = get_valid_date()
            
    transactions = load_transactions()
    old_transactions = copy.deepcopy(transactions)
    old_accounts = copy.deepcopy(accounts)
    old_debts = copy.deepcopy(debts)

    transaction_id = create_debt_transaction(
        transactions, account, debt_type, amount, person_name, purpose, date_str
    )
    
    new_debt = {
        "debt_id": generate_id(debts, "debt_id"),
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

    try:
        save_json_file(TRANSACTIONS_FILE, transactions)
        save_json_file(ACCOUNTS_FILE, accounts)
        save_json_file(DEBTS_FILE, debts)
        print("\nDebt recorded successfully!")
    except Exception as e:
        try:
            save_json_file(TRANSACTIONS_FILE, old_transactions)
            save_json_file(ACCOUNTS_FILE, old_accounts)
            save_json_file(DEBTS_FILE, old_debts)
        except Exception as rollback_error:
            print("\nCRITICAL SYSTEM ERROR")
            print(f"Original Error: {e}")
            print(f"Rollback Error: {rollback_error}")
            print("Application could not guarantee data consistency.")
            print("Please restore from backup and inspect data files.")
            
        print(f"\nSystem error during debt creation: {e}")
        print("Debt creation aborted. No changes were saved.")


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

def _get_valid_repayment_amount(selected_debt, account):
    while True:
        amount_str = input("Enter repayment amount: ").strip()
        try:
            amount = float(amount_str)
        except ValueError:
            print("Invalid amount.")
            continue
            
        if not math.isfinite(amount):
            print("Invalid amount. Please enter a finite number.")
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
                return None
                
        if selected_debt["type"] == "BORROWED" and amount > account["balance"]:
            print(f"\nError: Insufficient balance in {account['name']} to pay {format_currency(amount)}.")
            return None

        return amount

def add_repayment():
    print("\n--- Record Repayment ---")
    debts = load_debts()
    active_debts = [d for d in debts if d["status"] == "ACTIVE"]
    
    if not active_debts:
        print("\nNo active debts found.")
        return
        
    print("\nSelect Active Debt:")
    selected_debt = select_from_list(
        active_debts,
        "Enter the number of the debt:",
        lambda d: f"{d['person_name']} | {d['type']} | Remaining: {format_currency(d['remaining_amount'])} | Created: {d['created_date']}"
    )
        
    accounts = load_accounts()
    if not accounts:
        print("\nNo accounts found.")
        return
        
    account = select_account(accounts)
    
    debt_date = date.fromisoformat(selected_debt["created_date"])
    date_str = get_valid_date(
        prompt_suffix=f", not before {selected_debt['created_date']}",
        min_date=debt_date
    )
        
    amount = _get_valid_repayment_amount(selected_debt, account)
    if amount is None:
        return
        
    transactions = load_transactions()
    repayments = load_repayments()

    old_transactions = copy.deepcopy(transactions)
    old_accounts = copy.deepcopy(accounts)
    old_debts = copy.deepcopy(debts)
    old_repayments = copy.deepcopy(repayments)

    transaction_id = create_repayment_transaction(
        transactions, account, selected_debt, amount, date_str
    )

    new_repayment = {
        "repayment_id": generate_id(repayments, "repayment_id"),
        "debt_id": selected_debt["debt_id"],
        "transaction_id": transaction_id,
        "account_id": account["account_id"],
        "amount": amount,
        "date": date_str
    }
    repayments.append(new_repayment)

    selected_debt["remaining_amount"] = round(selected_debt["remaining_amount"] - amount, 2)
    update_debt_status(selected_debt)

    try:
        save_json_file(TRANSACTIONS_FILE, transactions)
        save_json_file(ACCOUNTS_FILE, accounts)
        save_json_file(DEBTS_FILE, debts)
        save_json_file(REPAYMENTS_FILE, repayments)
        print("\nRepayment recorded successfully!")
    except Exception as e:
        try:
            save_json_file(TRANSACTIONS_FILE, old_transactions)
            save_json_file(ACCOUNTS_FILE, old_accounts)
            save_json_file(DEBTS_FILE, old_debts)
            save_json_file(REPAYMENTS_FILE, old_repayments)
        except Exception as rollback_error:
            print("\nCRITICAL SYSTEM ERROR")
            print(f"Original Error: {e}")
            print(f"Rollback Error: {rollback_error}")
            print("Application could not guarantee data consistency.")
            print("Please restore from backup and inspect data files.")
            
        print(f"\nSystem error during repayment creation: {e}")
        print("Repayment creation aborted. No changes were saved.")


def _reverse_transaction(transactions, accounts, transaction_id):
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


def delete_repayment():
    print("\n--- Delete Repayment ---")
    repayments = load_repayments()
    if not repayments:
        print("\nNo repayments found.")
        return
        
    debts = load_debts()
    
    print("\nSelect Repayment to Delete:")
    def format_rep(r):
        debt = next((d for d in debts if d["debt_id"] == r["debt_id"]), None)
        d_info = f"Debt {debt['type']} - {debt['person_name']}" if debt else "Unknown Debt"
        return f"{r['date']} | {format_currency(r['amount'])} | {d_info}"
        
    selected_rep = select_from_list(
        repayments,
        "Enter the number of the repayment:",
        format_rep
    )
    if not selected_rep:
        return
        
    confirm = input(f"Are you sure you want to delete repayment of {format_currency(selected_rep['amount'])}? (y/n): ").strip()
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    transactions = load_transactions()
    accounts = load_accounts()

    old_transactions = copy.deepcopy(transactions)
    old_accounts = copy.deepcopy(accounts)
    old_debts = copy.deepcopy(debts)
    old_repayments = copy.deepcopy(repayments)

    _reverse_transaction(transactions, accounts, selected_rep["transaction_id"])

    repayments.remove(selected_rep)

    debt = next((d for d in debts if d["debt_id"] == selected_rep["debt_id"]), None)
    if debt:
        debt["remaining_amount"] = round(debt["remaining_amount"] + selected_rep["amount"], 2)
        if debt["remaining_amount"] > debt["original_amount"]:
            debt["remaining_amount"] = debt["original_amount"]
        if debt["status"] == "CLOSED":
            debt["status"] = "ACTIVE"

    try:
        save_json_file(TRANSACTIONS_FILE, transactions)
        save_json_file(ACCOUNTS_FILE, accounts)
        save_json_file(DEBTS_FILE, debts)
        save_json_file(REPAYMENTS_FILE, repayments)
        print("\nRepayment deleted successfully.")
    except Exception as e:
        try:
            save_json_file(TRANSACTIONS_FILE, old_transactions)
            save_json_file(ACCOUNTS_FILE, old_accounts)
            save_json_file(DEBTS_FILE, old_debts)
            save_json_file(REPAYMENTS_FILE, old_repayments)
        except Exception as rollback_error:
            print("\nCRITICAL SYSTEM ERROR")
            print(f"Original Error: {e}")
            print(f"Rollback Error: {rollback_error}")
            print("Application could not guarantee data consistency.")
            print("Please restore from backup and inspect data files.")
            
        print(f"\nSystem error during repayment deletion: {e}")
        print("Repayment deletion aborted. No changes were saved.")

def delete_debt():
    print("\n--- Delete Debt ---")
    debts = load_debts()
    if not debts:
        print("\nNo debts found.")
        return
        
    repayments = load_repayments()
    
    print("\nSelect Debt to Delete:")
    selected_debt = select_from_list(
        debts,
        "Enter the number of the debt:",
        lambda d: f"{d['person_name']} | {d['type']} | {d['status']} | Orig: {format_currency(d['original_amount'])}"
    )
    if not selected_debt:
        return
        
    has_repayments = any(r["debt_id"] == selected_debt["debt_id"] for r in repayments)
    if has_repayments:
        print("\nError: Cannot delete debt with repayment history. Delete repayments first.")
        return
        
    confirm = input("Are you sure you want to delete this debt? (y/n): ").strip()
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return
        
    transactions = load_transactions()
    accounts = load_accounts()
    old_transactions = copy.deepcopy(transactions)
    old_accounts = copy.deepcopy(accounts)
    old_debts = copy.deepcopy(debts)

    _reverse_transaction(transactions, accounts, selected_debt["transaction_id"])

    debts.remove(selected_debt)

    try:
        save_json_file(TRANSACTIONS_FILE, transactions)
        save_json_file(ACCOUNTS_FILE, accounts)
        save_json_file(DEBTS_FILE, debts)
        print("\nDebt deleted successfully.")
    except Exception as e:
        try:
            save_json_file(TRANSACTIONS_FILE, old_transactions)
            save_json_file(ACCOUNTS_FILE, old_accounts)
            save_json_file(DEBTS_FILE, old_debts)
        except Exception as rollback_error:
            print("\nCRITICAL SYSTEM ERROR")
            print(f"Original Error: {e}")
            print(f"Rollback Error: {rollback_error}")
            print("Application could not guarantee data consistency.")
            print("Please restore from backup and inspect data files.")
            
        print(f"\nSystem error during debt deletion: {e}")
        print("Debt deletion aborted. No changes were saved.")

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
    transactions = load_transactions()
    for t in transactions:
        if t["type"] == "Transfer":
            if t["from_account_id"] == account_id or t["to_account_id"] == account_id:
                return True
    return False


def _get_valid_transfer_amount(from_account):
    while True:
        amount_input = input("Enter amount: ").strip()
        try:
            amount = float(amount_input)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
            
        if not math.isfinite(amount):
            print("Invalid amount. Please enter a finite number.")
            continue

        if amount <= 0:
            print("Amount must be greater than zero.")
            continue
            
        if from_account["account_type"] != "Credit Card" and amount > from_account["balance"]:
            print(f"Error: Insufficient balance in {from_account['name']}. Available: {format_currency(from_account['balance'])}.")
            continue
            
        return amount

def _get_valid_transfer_date():
    while True:
        date_str = input(f"Enter date (YYYY-MM-DD) [default {date.today()}]: ").strip()
        if not date_str:
            return str(date.today())
        try:
            parsed_date = date.fromisoformat(date_str)
            if parsed_date > date.today():
                print("Error: Transfer date cannot be in the future. Please try again.")
                continue
            return date_str
        except ValueError:
            print("Invalid date format. Please try again.")

def transfer_money():
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
        
    amount = _get_valid_transfer_amount(from_account)
    date_str = _get_valid_transfer_date()
            
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

    from_account["balance"] = round(from_account["balance"] - amount, 2)
    to_account["balance"] = round(to_account["balance"] + amount, 2)
    
    new_transaction = {
        "transaction_id": generate_id(transactions, "transaction_id"),
        "type": "Transfer",
        "from_account_id": from_account["account_id"],
        "to_account_id": to_account["account_id"],
        "amount": amount,
        "date": date_str,
        "notes": notes
    }
    
    transactions.append(new_transaction)
    
    try:
        save_json_file(TRANSACTIONS_FILE, transactions)
        save_json_file(ACCOUNTS_FILE, accounts)
        print("\nTransfer executed successfully!")
    except Exception as e:
        try:
            save_json_file(TRANSACTIONS_FILE, old_transactions)
            save_json_file(ACCOUNTS_FILE, old_accounts)
        except Exception as rollback_error:
            print("\nCRITICAL SYSTEM ERROR")
            print(f"Original Error: {e}")
            print(f"Rollback Error: {rollback_error}")
            print("Application could not guarantee data consistency.")
            print("Please restore from backup and inspect data files.")
            
        print(f"\nSystem error during transfer: {e}")
        print("Transfer aborted. No changes were saved.")


def delete_transfer():
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
    
    sorted_transfers = sorted(transfers, key=lambda t: (t["date"], t["transaction_id"]), reverse=True)
    
    def format_transfer(t):
        from_name = get_account_name(t["from_account_id"], accounts)
        to_name = get_account_name(t["to_account_id"], accounts)
        acc_display = f"{from_name} -> {to_name}"
        if len(acc_display) > 28:
            acc_display = acc_display[:26] + ".."
        notes_display = t.get("notes", "")
        formatted_amount = f"₹{t['amount']:,.2f}"
        return f"  {t['date']:<13}{acc_display:<30}{formatted_amount:>15}  {notes_display}"
        
    selected_transfer = select_from_list(
        sorted_transfers,
        "\nEnter the number of the transfer to delete:",
        format_transfer
    )
    if not selected_transfer:
        return
        
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

    if from_account:
        from_account["balance"] = round(from_account["balance"] + selected_transfer["amount"], 2)
    if to_account:
        to_account["balance"] = round(to_account["balance"] - selected_transfer["amount"], 2)
        
    for idx_t, t in enumerate(transactions):
        if t["transaction_id"] == selected_transfer["transaction_id"]:
            del transactions[idx_t]
            break
    
    try:
        save_json_file(TRANSACTIONS_FILE, transactions)
        save_json_file(ACCOUNTS_FILE, accounts)
        print("\nTransfer deleted and balances reversed successfully.")
    except Exception as e:
        try:
            save_json_file(TRANSACTIONS_FILE, old_transactions)
            save_json_file(ACCOUNTS_FILE, old_accounts)
        except Exception as rollback_error:
            print("\nCRITICAL SYSTEM ERROR")
            print(f"Original Error: {e}")
            print(f"Rollback Error: {rollback_error}")
            print("Application could not guarantee data consistency.")
            print("Please restore from backup and inspect data files.")
            
        print(f"\nSystem error during deletion: {e}")
        print("Deletion aborted. No changes were saved.")


def manage_categories():
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

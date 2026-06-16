# Feature 1: Account Creation

## Purpose

Allow users to create financial accounts (Cash, Bank, UPI, Investment, Credit Card) via a CLI menu. Accounts are validated, assigned a unique ID, and saved to a JSON file.

---

## Business Rules

- Account name must be unique (case-insensitive — "SBI" and "sbi" count as duplicates)
- Account name cannot be empty
- Starting balance cannot be negative
- Account type must be one of 5 predefined types (selected by number, not free text)
- Account ID is auto-generated (highest existing ID + 1, starting from 1)
- Created date is set automatically using today's date
- `data/accounts.json` and its directory are created automatically if missing

---

## Functions

| Function | Purpose | Why Needed |
|----------|---------|------------|
| `load_accounts()` | Read accounts from JSON file into a list | Every operation needs the current data — duplicate checks, ID generation |
| `save_accounts(accounts)` | Write the full accounts list back to JSON | Centralizes file-writing so any future feature can reuse it |
| `generate_account_id(accounts)` | Return the next unique ID | IDs must auto-increment without user input |
| `is_duplicate_name(accounts, name)` | Check if a name already exists | Enforces the unique-name business rule |
| `get_valid_account_type()` | Show allowed types and validate the user's choice | Rejects invalid input in a loop until a valid type is picked |
| `get_valid_balance()` | Collect and validate a non-negative number | Uses try/except to handle non-numeric input safely |
| `add_account()` | Orchestrate the full creation workflow | Coordinates load → validate → build → save in one place |
| `main()` | Display menu and route user choices | Entry point; keeps running until user exits |

---

## Flow

1. `main()` shows a menu with "Add Account" and "Exit"
2. User picks "Add Account" → `add_account()` is called
3. Existing accounts are loaded from JSON
4. User enters a name → rejected if empty or duplicate
5. User picks an account type from a numbered list → rejected if invalid
6. User enters a balance → rejected if non-numeric or negative
7. A dictionary is built with all 5 fields (ID, name, type, balance, date)
8. Dictionary is appended to the list → full list is saved to JSON
9. Confirmation is printed → control returns to the menu

---

## Key Learnings

**Python concepts:**
- `json.loads()` (string → Python object) vs `json.dump()` (Python object → file)
- `with open()` guarantees file closure even on errors
- `try/except ValueError` catches type conversion failures without crashing
- `.strip()`, `.lower()`, `.isdigit()` — essential string methods for input handling
- `while True` + `break`/`continue`/`return` — the standard input validation loop pattern
- `os.path.join()` builds cross-platform file paths
- `if __name__ == "__main__"` prevents code from running on import
- f-strings for clean string formatting

**Software development concepts:**
- Separation of concerns — each function does exactly one thing
- Defensive programming — never trust user input, validate everything
- Constants at the top — single source of truth for config values
- JSON as a lightweight persistence layer for small projects (trade-off: no indexing, full rewrite on every save)

---

## Future Improvements

- ~~View~~, edit, and delete accounts
- Confirmation prompt before saving ("Are you sure?")
- UUID-based IDs to avoid gaps after deletions
- Backup `accounts.json` before overwriting
- Move account types to a config file

---
---

# Feature 2: View Accounts

## Purpose

Allow users to view all accounts stored in `accounts.json` in a formatted CLI table with a summary section. This feature is read-only — it never modifies account data.

---

## Business Rules

- Viewing accounts must never modify `accounts.json`
- If no accounts exist, display "No accounts found." — no crash, no empty table
- Accounts are displayed in ascending ID order (ID = creation order)
- Summary (total count + total balance) is calculated dynamically at display time
- Balances are displayed in Indian Rupee format with 2 decimal places

---

## Functions

| Function | Purpose | Why Needed |
|----------|---------|------------|
| `format_currency(amount)` | Convert a number to `₹15,000.00` format | Same formatting needed in summary and every table row — DRY |
| `display_accounts_summary(accounts)` | Print total count and combined balance | Separates summary logic from table display |
| `view_accounts()` | Orchestrate: load → empty check → sort → summary → table | Same orchestrator pattern as `add_account()` |

---

## Flow

1. `main()` shows menu with "View Accounts" as option 2
2. User picks "View Accounts" → `view_accounts()` is called
3. Accounts are loaded from JSON via `load_accounts()` (reused from Feature 1)
4. If the list is empty → print "No accounts found." and return
5. Accounts are sorted by ID (ascending) using `sorted()` — returns a new list, original untouched
6. `display_accounts_summary()` prints total count and total balance
7. Table header is built, separator width is computed from header length
8. Loop prints each account row with formatted currency
9. Control returns to the menu

---

## Key Learnings

**Python concepts:**
- `f"₹{amount:,.2f}"` — format spec with `,` for thousands separator and `.2f` for 2 decimal places
- `f"{'ID':<6}"` — f-string with `:<` for left-alignment and `:>` for right-alignment in fixed-width columns
- Single quotes inside double-quoted f-strings — outer and inner quotes must differ for compatibility
- `sorted(list, key=lambda x: x["field"])` — returns a new sorted list without modifying the original
- `lambda` — one-line anonymous function, used here to tell `sorted()` what to sort by
- `sum(x["field"] for x in list)` — generator expression inside `sum()` for memory-efficient totals
- `len(string)` — returns character count, used to compute dynamic separator width
- `sys.stdout.reconfigure(encoding="utf-8")` — ensures non-ASCII characters (₹) display correctly on Windows

**Software development concepts:**
- Read-only operations should never call write functions (`save_accounts` is never called)
- `sorted()` vs `.sort()` — `sorted()` is the safe choice for read-only features because it doesn't mutate
- DRY principle — `format_currency()` extracted because the same format appears in multiple places
- Avoiding magic numbers — separator width derived from `len(header)` instead of hardcoded `64`
- Storing intermediate results in variables (`header`) can serve dual purposes (display + computation)

---

## Known Limitations (V1)

- Long account names (>25 chars) may misalign table columns — won't crash, just looks off
- Feature 1 and Feature 2 use different balance formats (`25000.0` vs `₹25,000.00`)
- Indian numbering system (lakh/crore: `₹15,00,000`) not implemented — uses standard `₹1,500,000`

---
---

# Feature 3: Add Transaction

## Purpose

Allow users to record Income and Expense transactions against a selected account. It validates inputs, updates account balances, and saves transaction and account data to separate JSON files.

---

## Business Rules

- Account must exist before creating a transaction
- Transaction type must be Income or Expense
- Amount must be greater than zero
- Expense amount cannot exceed account balance
- Description cannot be empty
- Transaction ID is auto-generated (highest existing ID + 1, starting from 1)
- Transaction date is automatically generated using today's date
- Account balance must be updated and saved after transaction
- Transactions are saved in `transactions.json`
- Updated balances are saved in `accounts.json`
- If an account has a balance of exactly zero, expenses are blocked immediately

---

## Functions

| Function | Purpose | Why Needed |
|----------|---------|------------|
| `load_transactions()` | Read transactions from JSON file into a list | Every operation needs current transaction data — ID generation, list append |
| `save_transactions(transactions)` | Write the full transactions list back to JSON | Centralizes file writing for transaction records persistence |
| `generate_transaction_id(transactions)` | Return the next unique ID | Transaction IDs must auto-increment without user input |
| `select_account(accounts)` | Show accounts with balances and validate selection | Links the transaction to a specific account; reusable for transfers |
| `get_valid_transaction_type()` | Show allowed types and validate choice | Rejects invalid input in a loop until Income/Expense is chosen |
| `get_valid_amount(transaction_type, balance)` | Prompt for positive number; checks balance for expenses | Rejects invalid or insufficient amounts dynamically based on type |
| `add_transaction()` | Orchestrate the full transaction workflow | Coordinates load → validate → calculate → save in one place |

---

## Flow

1. `main()` shows menu with "Add Transaction" as option 3
2. User picks "Add Transaction" → `add_transaction()` is called
3. Accounts are loaded; if none exist, print message and exit
4. Transactions are loaded via `load_transactions()`
5. User selects an account via `select_account()`
6. User picks transaction type via `get_valid_transaction_type()`
7. If type is Expense and account balance is zero, print message and exit
8. User enters transaction amount via `get_valid_amount()`
9. User enters description → rejected if empty
10. `old_balance` is saved; `new_balance` is calculated and rounded to 2 decimals
11. Transaction record is created and appended to transaction list
12. Transactions are saved to `transactions.json` and updated accounts to `accounts.json`
13. Confirmation with details (previous vs new balance) is printed

---

## Key Learnings

**Python concepts:**
- `enumerate()` — returns index and item from a list, starting menu numbering at 1
- `sorted()` — returns a sorted copy of a list using a key, keeping original data order intact
- `lambda` — one-line anonymous function, used as a sort key for accounts
- `float()` — converts input strings into decimal numbers for currency arithmetic
- `try/except` — catches type conversion errors from invalid user input without crashing
- `round()` — rounds floats to 2 decimal places to prevent floating-point calculation errors
- List append — adds the new transaction dictionary to the existing transactions list
- Dictionary creation — builds the structured transaction record with six fields
- Function parameters — passing variables (type, balance) into input functions for custom validation
- Passing by reference — dictionary changes within functions update the parent list directly

**Software development concepts:**
- Single Responsibility Principle — separating logic into small helper functions with one task each
- Reusability — creating generic validation and selection functions for reuse in other features
- Separation of Concerns — separating data loading/saving from UI prompts and mathematical calculations
- Data Relationships — using `account_id` as a foreign key to link transactions to accounts
- Referential Integrity — ensuring transactions are only linked to valid, existing accounts
- Guard Clauses — exiting functions early if preconditions (like existing accounts) are not met
- Input Validation — looping indefinitely until valid data is entered to protect system integrity
- Data Persistence — saving data to separate JSON files to ensure state survives app restart

---

## Known Limitations (V1)

- Cannot view transactions
- Cannot edit transactions (no balance reversal logic)
- Cannot delete transactions (no balance reversal logic)
- No transaction categories (all transactions are uncategorized)
- No transfers between accounts
- No reports or summaries of transaction history

---

## Future Improvements

- Transaction categories (e.g., Food, Travel)
- View transactions in a tabular format
- Edit and delete transaction options
- Support transfers between accounts
- Transaction search and date filtering
- Monthly or category-wise expense reports

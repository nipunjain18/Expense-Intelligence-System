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

---
---

# Feature 4: View Transactions

## Purpose

Allow users to view all historical transactions in a formatted CLI table with a financial summary. Users can track where money came from (Income) and where it was spent (Expense), and verify previously entered records. This feature is read-only — it never modifies transaction or account data.

---

## Business Rules

- Viewing transactions must never modify `transactions.json` or `accounts.json`
- All transactions are displayed — no filtering, no search, no pagination
- Transactions are sorted by date (newest → oldest)
- If dates are equal, sorted by transaction ID (highest → lowest) for deterministic ordering
- Display columns: Transaction ID, Date, Type, Account, Amount, Description
- Account names are resolved from `account_id` using `accounts.json`
- If a transaction references an `account_id` that no longer exists, display "Deleted Account"
- Income amounts displayed as `+₹1,000.00`, Expense amounts as `-₹500.00`
- Type column is kept even though amount has +/- signs (future Transfer type will need it)
- Summary shows Total Income and Total Expense below the table
- Invalid records are skipped — not displayed, not included in summary calculations
- Aggregated count of invalid records is shown (e.g., "Skipped 3 invalid transaction records.")
- If no transactions exist, display "No transactions found." — no crash, no empty table
- If all transactions are invalid, display the skip count then the empty-state message
- Accounts are loaded only after confirming transactions exist — no unnecessary file I/O

---

## Functions

| Function | Purpose | Why Needed |
|----------|---------|------------|
| `format_transaction_amount(amount, transaction_type)` | Format amount with `+`/`-` sign and `₹` symbol | Separate from `format_currency()` because existing call sites (balances, summaries) don't need signs — avoids breaking 4 existing usages |
| `validate_transaction(transaction)` | Check if a single record has all required keys and valid values | Catches missing keys, invalid types ("Banana"), non-numeric amounts, empty descriptions, and empty dates before they cause silent errors |
| `get_account_name(account_id, accounts)` | Resolve an `account_id` to an account name via linear scan | Returns "Deleted Account" if no match — handles deleted accounts gracefully without crashing |
| `display_transaction_table(transactions, accounts)` | Print formatted table header and all transaction rows | Contains per-row logic (two helper calls + column formatting) — enough complexity to extract from the orchestrator |
| `view_transactions()` | Orchestrate: load → empty check → load accounts → validate → sort → display → summarize | Same orchestrator pattern as `add_transaction()` and `view_accounts()` |

---

## Flow

1. `main()` shows menu with "View Transactions" as option 4
2. User picks "View Transactions" → `view_transactions()` is called
3. Transactions are loaded from JSON via `load_transactions()` (reused from Feature 3)
4. If the list is empty → print "No transactions found." and return (accounts are NOT loaded)
5. Accounts are loaded from JSON via `load_accounts()` (deferred until needed)
6. Each transaction is validated via `validate_transaction()` — separated into valid and invalid lists
7. If any invalid records found → print "Skipped N invalid transaction record(s)."
8. If no valid records remain → print empty-state message and return
9. Valid transactions are sorted inline using `sorted()` — date descending, then transaction ID descending
10. `display_transaction_table()` prints the header and each row with resolved account names and signed amounts
11. Total Income and Total Expense are calculated from valid transactions using `sum()` with generator expressions
12. Summary is printed using `format_currency()` — control returns to the menu

---

## Key Learnings

**Python concepts:**
- `set` and `.issubset()` — checks if all required keys exist in a dictionary; more readable than checking each key individually
- `isinstance(value, (int, float))` — type checking with a tuple of types to accept multiple valid types
- `sorted()` with tuple key — `key=lambda t: (t["date"], t["transaction_id"])` sorts by primary then secondary key
- `reverse=True` — reverses the entire sort order (newest date and highest ID first)
- Generator expressions inside `sum()` — `sum(t["amount"] for t in list if t["type"] == "Income")` filters and sums in one pass without creating an intermediate list
- `round(value, 2)` — prevents floating-point drift when summing many decimal amounts
- f-string alignment — `:<6` for left-aligned, `:>15` for right-aligned columns in fixed-width table output
- List filtering with a loop — building `valid_transactions` by appending only records that pass validation
- Helper functions as pure functions — `validate_transaction()`, `get_account_name()`, and `format_transaction_amount()` have no side effects; they take input and return output
- Constants as a single source of truth — `REQUIRED_TRANSACTION_KEYS` and `VALID_TRANSACTION_TYPES` used by both input validation (Feature 3) and display validation (Feature 4)

**Software development concepts:**
- Data validation beyond key presence — checking that values are correct (type is Income/Expense, amount is numeric, description is non-empty) prevents silently incorrect summaries
- Defensive programming — invalid records are skipped with a warning, never crash the application
- Data integrity — invalid records are excluded from both display and calculations; summaries are always accurate
- Read-only operations — `save_transactions()` and `save_accounts()` are never called; data flows one direction (file → process → display)
- Separation of concerns — validation, display, formatting, and orchestration are each in separate functions
- Data relationships — `account_id` links transactions to accounts; `get_account_name()` resolves this foreign key at display time
- Graceful error handling — deleted accounts show "Deleted Account" instead of crashing; empty states show friendly messages
- Deterministic sorting — using a secondary sort key (transaction ID) ensures identical output every time, even when dates are equal
- Reusability — `format_currency()` from Feature 2 is reused for summary totals; `load_transactions()` and `load_accounts()` from earlier features are reused
- Single source of truth — transaction type validation uses the same `VALID_TRANSACTION_TYPES` constant as `get_valid_transaction_type()`; adding "Transfer" later requires changing only the constant

---

## Known Limitations (V1)

- No transaction filtering (by date, type, or account)
- No search functionality
- No pagination — all transactions displayed at once
- Long descriptions may push table rows beyond terminal width — won't crash, just looks off
- No category support — all transactions are uncategorized
- No edit or delete transaction support
- Indian numbering system (lakh/crore) not implemented — uses standard comma formatting

---

## Future Improvements

- Filter transactions by date range, type, or account
- Search transactions by description keyword
- Category-based views (once categories are implemented)
- Support Transfer transaction type (between accounts)
- Monthly or category-wise expense reports
- Analytics dashboard with spending trends
- Pagination for large transaction lists

---
---

# Feature 5: Category Management

## Purpose

Allow users to manage transaction categories via a CLI submenu. This feature establishes the foundational data structures required to group transactions logically, supporting future analytics and AI-driven insights. It includes the ability to view, create, rename, soft-delete, and restore categories.

---

## Business Rules

- Default categories are automatically seeded if the system is completely empty
- Category types (Expense/Income) are set at creation and can never be changed
- Category type is inferred from the menu path (e.g., "Add Expense Category")
- Default categories cannot be renamed
- Default categories cannot be deleted
- All category names must be globally unique across all types
- Uniqueness checks are strictly case-insensitive
- If a user attempts to create a new category with the exact name of a deleted category (of the same type), the system intelligently restores the old category instead of duplicating IDs
- All names have trailing and leading whitespace trimmed
- Empty category names are hard-rejected
- Renaming a category to its exact current name (case-insensitive) is explicitly blocked (e.g., renaming 'Gym' to 'gym' is rejected)
- Restoring a deleted category is blocked if an active category with the same name already exists
- Deleted categories are appended with a "(Deleted)" suffix in view lists
- Category IDs are kept completely hidden from the user interface
- Categories are sorted alphabetically, with active categories shown before deleted categories

---

## Functions

| Function | Purpose | Why Needed |
|----------|---------|------------|
| `load_categories()` | Read categories from JSON file into a list | Every operation needs the current data — duplicate checks, ID generation, validation |
| `save_categories(categories)` | Write the full categories list back to JSON | Centralizes persistent storage for category records |
| `generate_category_id(categories)` | Return the next unique ID | Category IDs must auto-increment without user input to act as stable foreign keys |
| `ensure_default_categories()` | Seed the system with default categories if empty | Speeds up user onboarding and ensures essential categories exist |
| `view_categories()` | Display all categories, grouped by type and sorted | Allows users to visually verify active and deleted categories |
| `validate_category_name(name)` | Trim whitespace and reject empty names | Centralizes sanitization so both creation and renaming share the same rules |
| `is_duplicate_category_name(categories, name, exclude_id)` | Case-insensitive global uniqueness check | Enforces the unique-name business rule, with an optional exclusion for renaming |
| `select_category(categories, filter_fn, empty_message)` | Unified selection helper for categories | DRY principle — reusable loop for rename, delete, and restore flows |
| `create_category(category_type)` | Create or auto-restore a category | Coordinates validation, global uniqueness, and intelligent auto-restoration |
| `rename_category()` | Rename a custom category | Updates category names while blocking redundant or duplicate renames |
| `delete_category()` | Soft delete a custom category after confirmation | Hides categories without breaking past transaction referential integrity |
| `restore_category()` | Restore a deleted category | Brings back hidden categories, checking for active name collisions first |
| `manage_categories()` | Category submenu loop | Sub-orchestrator; keeps running category operations until user exits back to main |

---

## Flow

**Main Flow**
1. `main()` shows menu with "Manage Categories" as option 5
2. User picks "Manage Categories" → `manage_categories()` is called
3. `ensure_default_categories()` runs to seed defaults if the system is completely empty
4. Submenu loop is displayed offering View, Add Expense, Add Income, Rename, Delete, Restore, and Back

**Create Category Flow**
1. User picks "Add Expense Category" or "Add Income Category"
2. Categories are loaded from JSON
3. User enters a name → whitespace is trimmed
4. Name is validated → rejected if empty
5. System checks for a deleted category with the exact name and same type → auto-restores if found
6. System checks for duplicate active categories across all types → rejected if duplicate
7. New category record is built and appended
8. Full list is saved to JSON and confirmation is printed

**Rename Category Flow**
1. User picks "Rename Category"
2. Categories are loaded from JSON
3. `select_category()` filters for non-default categories and displays numbered list
4. User selects a category
5. User enters new name → whitespace is trimmed, rejected if empty
6. New name is compared against current name case-insensitively → rejected if identical (e.g., "Gym" to "gym")
7. New name is checked for global duplicates (excluding itself) → rejected if exists
8. Category name is updated and saved to JSON

**Delete Category Flow**
1. User picks "Delete Category"
2. Categories are loaded from JSON
3. `select_category()` filters for active, non-default categories and displays numbered list
4. User selects a category
5. User is prompted for confirmation (`y/n`)
6. If 'y', the `is_deleted` flag is set to `True` (Soft Delete)
7. Full list is saved to JSON

**Restore Category Flow**
1. User picks "Restore Category"
2. Categories are loaded from JSON
3. `select_category()` filters for deleted categories and displays numbered list
4. User selects a category
5. System checks if an active category with the exact name already exists → blocks restore if true
6. `is_deleted` flag is set to `False`
7. Full list is saved to JSON

---

## Design Decisions

- **`category_id` instead of category name:** Names change over time. If a user renames "Gym" to "Fitness", using a stable numeric ID ensures that all past transactions pointing to ID `11` instantly reflect the new name. Linking by name would require updating every historical transaction during a rename.
- **Soft delete instead of hard delete:** Financial data relies on historical accuracy. Permanently deleting a category would break past transactions linked to it. Soft deletion preserves referential integrity by merely hiding the category from active selection menus while keeping the data intact for reporting.
- **Global uniqueness instead of type-based uniqueness:** Allowing identical names across types creates data ambiguity where an Expense category named "Food" and an Income category named "Food" could coexist simultaneously. Enforcing global uniqueness ensures that AI insights and analytics can group data purely by name without NLP confusion.
- **Type inferred from menu instead of asking the user:** The submenu directly routes to "Add Expense Category" and "Add Income Category" rather than asking the user for the type after they start the creation flow. This reduces prompts and minimizes user error by establishing intent upfront.
- **Unified `select_category()` helper instead of separate selection functions:** Consolidated the repetitive selection flow for renaming, deleting, and restoring into a highly flexible helper function. This enforces the DRY principle and dramatically reduces code duplication.

---

## Key Learnings

**Python concepts:**
- `json.load()` and `json.dump()` with `indent=4` for human-readable formatting, handling malformed files with `try-except json.JSONDecodeError`
- List filtering with comprehensions to cleanly separate data (e.g., `[c for c in categories if c["type"] == "Expense"]`)
- Multi-key sorting by passing a tuple to the `key` argument: `categories.sort(key=lambda c: (c["is_deleted"], c["name"].lower()))`
- Boolean sorting logic — because `False` evaluates to `0` and `True` to `1`, active categories (`False`) sort before deleted ones (`True`)
- Passing functions as arguments — `filter_fn` (a lambda or local function) passed to `select_category` dynamically dictates allowed selections
- Optional parameters — `exclude_id=None` allowed the same validation function to be used for both creation and renaming
- Modeling state using boolean flags (`is_default`, `is_deleted`) rather than separate lists to maintain a single source of truth

**Software development concepts:**
- Separation of concerns — distinct layers for Data I/O, Seeding, Validation, Selection, and Operations
- Single Responsibility Principle (DRY) — consolidated logic into a single `select_category()` helper to reduce code duplication across rename, delete, and restore
- Soft Delete vs Hard Delete — implemented Soft Delete pattern to preserve historical accuracy and referential integrity of past financial transactions
- Global uniqueness constraints — enforcing unique names across all types prevents ambiguous data states (e.g., conflicting Expense and Income categories)
- Defensive programming — wrapping numeric inputs in `isdigit()` and `try-except ValueError` blocks to prevent crashes

---

## Known Limitations (V1)

- Transactions do not yet use `category_id` (Feature 6 will integrate this)
- Category names can theoretically be very long, potentially misaligning the display table
- Categories cannot be merged (e.g., combining "Gym" and "Fitness" into a single category is not supported)
- No pagination for category views if the list becomes massive

---

## Future Improvements

- Integrate categories into the `add_transaction()` flow
- Spending analysis and pie charts grouped by category
- Income analysis reports
- Analytics dashboard with AI insights leveraging globally unique category names

---

# Feature 6: Category Integration

## Purpose

Connect categories with transactions by storing `category_id` in transaction records, rather than having no category relationship.

---

## Business Rules

**Transaction Structure:**
```json
{
"transaction_id": 1,
"account_id": 1,
"category_id": 3,
"type": "Expense",
"amount": 500,
"description": "Lunch",
"date": "2026-06-18"
}
```

- **Mandatory Field:** A transaction cannot be created without a category.
- **Type Matching:** Category type must match the transaction type (Income uses Income categories, Expense uses Expense categories).
- **Selection State:** Only active categories can be selected; deleted categories are hidden during creation. Default categories remain protected.
- **Data Normalization:** Store only `account_id` and `category_id` in transactions. Never store names to prevent data duplication.
- **Dynamic Display:** Active categories display normally (e.g., `Food`). Deleted categories append a suffix (e.g., `Food (Deleted)`).
- **Rename & Restore:** Renaming or restoring a category instantly updates past transactions since the ID never changes.

---

## Functions

**Functions Added:**
- `get_category_name()`
- `select_transaction_category()`
- `add_income()`
- `add_expense()`
- `_add_transaction()`

**Functions Modified:**
- `validate_transaction()`
- `display_transaction_table()`
- `view_transactions()`

---

## Flow

**Income**

Select Account
↓
Select Income Category
↓
Amount
↓
Description
↓
Save Transaction

**Expense**

Select Account
↓
Select Expense Category
↓
Amount
↓
Description
↓
Save Transaction

---

## Design Decisions

- **Separate user menus (`add_income`, `add_expense`) but shared internal logic (`_add_transaction`):** Provides a clean user experience while reusing code.
- **Use `category_id` instead of `category_name`:** Names can change; IDs remain stable.
- **Resolve category names dynamically when viewing transactions:** Supports renaming, deleting, and restoring categories without having to update old transaction records.
- **Display deleted categories as `[Name] (Deleted)`:** Keeps old transactions readable without breaking the UI.

---

## Key Learnings

- How IDs can be used to connect related data across multiple JSON files.
- Why `category_id` is better than `category_name` for long-term stability.
- How dynamic data lookup allows category renames and restores without modifying old transactions.
- How shared helper functions reduce duplicate code across similar features like adding income and expenses.
- How a soft delete approach impacts linked records, requiring special display rules to maintain historical clarity.

---

## Known Limitations (V1)

- No transaction filtering by category.
- No category-based analytics or charts.
- No quick selection for recently used categories.

---

## Future Improvements

- Filter transactions by category.
- Category spending summary.
- Recently used categories.
- Category-wise reports.
- Category spending trends.
- Dashboard widgets using category data.

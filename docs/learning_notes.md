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

1. User selects "Add Account" from the main menu.
2. User enters an account name.
3. System validates: account name is not empty
4. account name is unique (case-insensitive)
5. User selects an account type.
6. User enters a starting balance.
7. System validates that the balance is not negative.
8. Account ID is generated automatically.
9. Account record is created.
10. Account is saved to `accounts.json`.
11. Success confirmation is displayed.
12. Control returns to the main menu.

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
- Transaction must be assigned an active category matching the transaction type
- Amount must be greater than zero
- Expense amount cannot exceed account balance
- Description cannot be empty
- Transaction ID is auto-generated (highest existing ID + 1, starting from 1)
- Transaction date is automatically generated using today's date
- Account balance must be updated and saved after transaction
- Transactions are saved in `transactions.json`
- Updated balances are saved in `accounts.json`
- If an account has a balance of exactly zero, expenses are blocked immediately
- Financial writes use rollback-safe atomic save protection

---

## Functions

| Function | Purpose | Why Needed |
|----------|---------|------------|
| `load_transactions()` | Read transactions from JSON file into a list | Every operation needs current transaction data — ID generation, list append |
| `save_transactions(transactions)` | Write the full transactions list back to JSON | Centralizes file writing for transaction records persistence |
| `generate_transaction_id(transactions)` | Return the next unique ID | Transaction IDs must auto-increment without user input |
| `select_account(accounts)` | Show accounts with balances and validate selection | Links the transaction to a specific account; reusable for transfers |
| `select_transaction_category(transaction_type)` | Show only valid categories for the chosen transaction type | Keeps transaction categories aligned with the current schema and hides debt categories |
| `get_valid_amount(transaction_type, balance)` | Prompt for positive number; checks balance for expenses | Rejects invalid or insufficient amounts dynamically based on type |
| `add_income()` | Entry point for the Income flow | Routes the menu choice into the shared transaction helper |
| `add_expense()` | Entry point for the Expense flow | Routes the menu choice into the shared transaction helper |
| `_add_transaction(transaction_type)` | Orchestrate the full transaction workflow | Coordinates load → validate → calculate → save in one place |

---

## Flow

1. `main()` shows menu options for "Add Income" and "Add Expense"
2. User picks one option → `add_income()` or `add_expense()` calls `_add_transaction()`
3. Default categories are seeded if needed
4. Accounts are loaded; if none exist, print message and exit
5. User selects an account via `select_account()`
6. User selects a matching active category via `select_transaction_category()`
7. If type is Expense and account balance is zero, print message and exit
8. User enters transaction amount via `get_valid_amount()`
9. User enters description → rejected if empty
10. `old_balance` is saved; `new_balance` is calculated and rounded to 2 decimals
11. Transaction record is created and appended to transaction list
12. Transactions and accounts are saved inside an atomic `try/except` block with rollback copies
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

- Cannot edit transactions (no balance reversal logic)
- Cannot delete transactions (no balance reversal logic)
- No transaction search or filtering
- No reports or summaries of transaction history

---

## Future Improvements

- Edit and delete transaction options
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
- Display columns: Transaction ID, Date, Type, Account, Category, Amount, Description
- Account names are resolved from `account_id` using `accounts.json`
- If a transaction references an `account_id` that no longer exists, display "Deleted Account"
- Income amounts displayed as `+₹1,000.00`, Expense amounts as `-₹500.00`
- Type column is kept because Transfer rows share the same table and need explicit labeling
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
| `get_category_name(category_id, categories)` | Resolve a `category_id` to a category name via linear scan | Keeps renamed and deleted categories readable without rewriting old transactions |
| `display_transaction_table(transactions, accounts, categories)` | Print formatted table header and all transaction rows | Contains per-row logic (account lookup, category lookup, and column formatting) — enough complexity to extract from the orchestrator |
| `view_transactions()` | Orchestrate: load → empty check → load accounts/categories → validate → sort → display → summarize | Same orchestrator pattern as the add and view flows |

---

## Flow

1. `main()` shows menu with "View Transactions" as option 4
2. User picks "View Transactions" → `view_transactions()` is called
3. Transactions are loaded from JSON via `load_transactions()` (reused from Feature 3)
4. If the list is empty → print "No transactions found." and return (accounts are NOT loaded)
5. Accounts and categories are loaded from JSON (deferred until needed)
6. Each transaction is validated via `validate_transaction()` — separated into valid and invalid lists
7. If any invalid records found → print "Skipped N invalid transaction record(s)."
8. If no valid records remain → print empty-state message and return
9. Valid transactions are sorted inline using `sorted()` — date descending, then transaction ID descending
10. `display_transaction_table()` prints the header and each row with resolved account names, category names, and signed amounts
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
- Helper functions as pure functions — `validate_transaction()`, `get_account_name()`, `get_category_name()`, and `format_transaction_amount()` have no side effects; they take input and return output
- Constants as a single source of truth — `REQUIRED_TRANSACTION_KEYS` and `VALID_TRANSACTION_TYPES` keep transaction validation aligned with the current schema, including Transfer records

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
- Single source of truth — `VALID_TRANSACTION_TYPES` keeps transaction validation aligned with the current schema, including Transfer records

---

## Known Limitations (V1)

- No transaction filtering (by date, type, or account)
- No search functionality
- No pagination — all transactions displayed at once
- Long descriptions may push table rows beyond terminal width — won't crash, just looks off
- No edit or delete transaction support
- Indian numbering system (lakh/crore) not implemented — uses standard comma formatting

---

## Future Improvements

- Filter transactions by date range, type, or account
- Search transactions by description keyword
- Category-based filtering
- Transfer-specific filtering
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

- Category names can theoretically be very long, potentially misaligning the display table
- Categories cannot be merged (e.g., combining "Gym" and "Fitness" into a single category is not supported)
- No pagination for category views if the list becomes massive

---

## Future Improvements

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

---
---

# Feature 7: Debt Tracking

## Purpose

Debt Tracking solves the problem of keeping track of money given to or taken from others. Instead of relying on mental notes or loose paper, the system provides a central place to record "Money Lent" and "Money Borrowed." This ensures that personal debts are accurately tied to real financial accounts and balances stay perfectly synchronized when money moves.

---

## Business Rules

### Debt Types

* **LENT:** Money given to someone. Reduces account balance.
* **BORROWED:** Money received from someone. Increases account balance.

### Debt Status

* **ACTIVE:** The debt has a remaining balance greater than zero.
* **CLOSED:** The debt has been fully repaid (remaining balance is zero).

### One Debt = One Account

A single debt is permanently tied to the exact account that funded or received it. Splitting a debt across multiple accounts is not allowed to maintain strict tracking.

### Debt Creation Rules

* **Account required:** You cannot create a debt without selecting a valid account.
* **Amount must be positive:** Debts cannot be created for ₹0 or negative amounts.
* **LENT cannot exceed account balance:** You cannot lend money you do not have.
* **BORROWED has no balance restriction:** You can borrow any amount since it adds to your balance.

### Date Rules

* **Default to today's date:** If left blank, the system uses the current date.
* **Debt creation dates cannot be in the future.**
* **Repayment dates cannot be in the future.**
* **Repayment dates cannot be earlier than the debt creation date.**
* **Users may enter valid historical dates.**

### Repayment Rules

* **Must be linked to a specific debt:** Repayments are strictly linked to a specific `debt_id`.
* **Debt selected by debt_id:** Active debts are displayed as a numbered list; selection targets the underlying ID, not the person's name.
* **Repayment creates transaction:** Every repayment mathematically updates the account via a linked `transaction_id`.
* **Repayment updates account balance:** Income (for LENT) or Expense (for BORROWED) is accurately reflected.
* **Repayment updates remaining amount:** The repayment amount is subtracted from the debt's `remaining_amount`.

### Overpayment Rules

If a user tries to repay more than the remaining balance, the system detects the overpayment and offers two options:
* **Record remaining amount only:** Truncates the repayment to exactly match the remaining balance.
* **Cancel:** Aborts the operation entirely.

### Deletion Rules

* **Debt Deletion:** A debt cannot be deleted if any repayment history exists. Repayments must be deleted first.
* **Repayment Deletion:** Deleting a repayment perfectly reverses its effects: the linked transaction is removed, the account balance is restored, and the debt's remaining amount is increased. If the debt was CLOSED, it automatically re-opens as ACTIVE.

### Atomic Save Protection

* **Debt Creation:** Deep copies of transactions, accounts, and debts are stored before the save block so a failed write can be rolled back safely.
* **Repayment Creation:** Deep copies of transactions, accounts, debts, and repayments are stored before the save block so a failed write can be rolled back safely.
* **Repayment Deletion:** The previous transactions, accounts, debts, and repayments are restored if any save fails.
* **Debt Deletion:** The previous transactions, accounts, and debts are restored if any save fails.

### Data Integrity Rules

* **No debt merging:** If an active debt already exists for a person, the system issues a warning but forces the creation of a brand new, independent debt record.
* **Every debt remains independent:** Repayments explicitly target one debt at a time.
* **Person Name Normalization:** Names are stripped of leading/trailing whitespace before saving to prevent duplicate mismatches.
* **One Debt = One Account:** Strictly enforced across creation and repayment.

### Debt Record
```json
{
    "debt_id": 1,
    "transaction_id": 45,
    "account_id": 2,
    "person_name": "Rahul",
    "type": "LENT",
    "status": "ACTIVE",
    "original_amount": 5000.0,
    "remaining_amount": 2000.0,
    "purpose": "Bike Repair",
    "notes": "Will repay next week",
    "created_date": "2026-06-19"
}
```

### Repayment Record
```json
{
    "repayment_id": 1,
    "debt_id": 1,
    "transaction_id": 46,
    "account_id": 2,
    "amount": 3000.0,
    "date": "2026-06-25"
}
```

---

## Functions

### Functions Added

* `load_debts()`
* `save_debts()`
* `generate_debt_id()`
* `load_repayments()`
* `save_repayments()`
* `generate_repayment_id()`
* `add_debt()`
* `view_debts()`
* `add_repayment()`
* `delete_repayment()`
* `delete_debt()`
* `view_repayments()`
* `manage_debts()`
* `create_debt_transaction()`
* `create_repayment_transaction()`
* `update_debt_status()`
* `find_active_debts_by_person()`

### Functions Modified

* `ensure_default_categories()`: Added logic to dynamically seed the 4 system-level debt categories.
* `get_or_create_debt_categories()`: A dedicated safety function guaranteeing debt categories exist.
* `select_transaction_category()`: Updated `filter_fn` to proactively hide internal debt categories from manual income/expense workflows.
* `main()`: Updated the main menu loop to include the new Debt Tracking submenu option.

---

## Flow

### Add Debt
Debt Type
↓
Select Account
↓
Person Name
↓
Amount
↓
Purpose
↓
Notes
↓
Date (future dates blocked)
↓
Save Atomically

### Record Repayment
Select Debt
↓
Select Account
↓
Date (future dates blocked, not before debt creation)
↓
Repayment Amount
↓
Save Atomically

### Delete Repayment
Select Repayment
↓
Confirm
↓
Reverse Transaction
↓
Restore Debt Balance
↓
Save Atomically

### Delete Debt
Select Debt
↓
Check Repayment History
↓
Reverse Linked Transaction
↓
Restore Account Balance
↓
Delete Debt
↓
Save Atomically

---

## Design Decisions

**Decision:** One Debt = One Account
**Reason:** Allows strict, uncomplicated tracking of where the money went and where it should return to without complex fractional math across multiple bank accounts.

**Decision:** No Debt Merging
**Reason:** Merging two debts funded by different accounts would break the "One Debt = One Account" rule and corrupt balance tracking. Independent records logically prevent data cross-corruption.

**Decision:** Store transaction_id inside debts and repayments
**Reason:** Enforces referential integrity. When a debt or repayment is deleted, the system knows exactly which financial transaction to fetch and reverse to restore the core account balance.

**Decision:** Store account_id inside repayments
**Reason:** Allows rapid rendering of UI tables (like View Repayments) without needing to do computationally expensive lookups across the entire master transactions file.

**Decision:** Repayment records are immutable
**Reason:** Editing a repayment implies editing dates, amounts, and potentially accounts simultaneously. Reversing and recreating (deleting and adding a new one) is significantly safer than writing complex edit-in-place financial update logic.

**Decision:** Debt status uses ACTIVE/CLOSED
**Reason:** Prevents users from manually archiving or confusing the state. The system mathematically derives the status purely dynamically based on `remaining_amount == 0`.

**Decision:** Debt categories are system-generated
**Reason:** Financial reports and transaction histories need to categorize debt flows correctly (e.g., "Debt Lent" as Expense). Hiding them from manual selection prevents users from polluting the data by picking them for non-debt transactions.

**Decision:** Separate debt and repayment files
**Reason:** Normalizes the data structure. Storing an array of repayments nested inside a single debt record makes global searching, sorting, and specific ID updates much harder to track. 

---

## Key Learnings

* **Financial data consistency:** Learning how to mathematically tie multiple moving parts (debt remaining balance + account balance + transaction history) together so they never fall out of sync.
* **Referential relationships between records:** Linking JSON objects using IDs (`transaction_id`, `account_id`, `debt_id`) simulating foreign keys in a relational database architecture.
* **Maintaining balance synchronization:** Understanding that moving money involves double-entry-style logic—if a debt balance goes down, an account balance must go up, and a transaction must be recorded.
* **Transaction reversal patterns:** Learning how to cleanly "undo" a complex action by carefully reversing its exact mathematical effects, rather than attempting to restore a previously saved state file.
* **Status-based lifecycle management:** Deriving a record's state (`ACTIVE`/`CLOSED`) mathematically based on its actual data values rather than relying on manual user input toggles.
* **Soft accounting principles:** Grasping that LENT money acts as an "Expense" against your current liquid balance, and BORROWED money acts as "Income" to your current liquid balance.
* **Data normalization:** Storing entities (Debts vs Repayments) in their own discrete flat lists rather than deeply nesting them, making the logic code easier to read and scale.
* **Designing business rules before coding:** Realizing that identifying edge cases (like overpayments, date paradoxes, and debt merging logic) *before* writing code prevents massive structural refactoring later.
* **Rollback protection:** Backing up all related lists before destructive debt operations prevents partial file writes from corrupting account balances or debt state.

---

## Known Limitations (V1)

* No debt editing for amount/account/type
* No debt reminders
* No interest calculations
* No due dates
* No debt search/filter
* No partial settlements or discounts
* No debt analytics

---

## Future Improvements

* Due dates
* Debt reminders
* Interest tracking
* Debt analytics dashboard
* Person-wise debt summary
* Debt search
* Debt filtering
* Debt reports
* Debt aging analysis

---
---

# Feature 8: Dashboard

## Purpose

The dashboard was added to provide a high-level, read-only financial overview of the entire Expense Intelligence System on a single screen. Previously, users had to navigate multiple menus (View Accounts, View Transactions, View Debts) and manually calculate their total financial standing. The dashboard solves this by aggregating data from all separate modules (`accounts.json`, `transactions.json`, `debts.json`, `categories.json`) into an instant, centralized snapshot.

---

## Business Rules

* Dashboard is strictly read-only
* Dashboard never modifies, saves, or deletes data
* Dashboard uses existing JSON files dynamically instead of storing summary metrics
* Dashboard relies on existing business logic and validators
* Dashboard summarizes information instead of duplicating data entry screens
* Dashboard displays exactly 6 sections:
  * Financial Overview
  * Account Summary
  * Debt Summary
  * Top Expense Categories
  * Recent Activity
  * Net Debt Position
* Top Expense Categories only calculates transactions of type "Expense"
* Recent Activity is limited strictly to 5 transactions, sorted newest first
* Malformed records (missing keys, invalid formats) are silently excluded from all aggregations to prevent crashes

---

## Functions

`calculate_total_balance()`
Purpose: Calculate total balance across all accounts.

`calculate_income_expense_summary()`
Purpose: Calculate total income, total expenses, and net cash flow.

`calculate_account_summary()`
Purpose: Extract valid accounts and their balances.

`calculate_debt_summary()`
Purpose: Aggregate lent/borrowed amounts and active/closed counts.

`calculate_top_expense_categories()`
Purpose: Find the 3 highest expense categories.

`get_recent_transactions()`
Purpose: Retrieve the 5 most recent transactions.

`calculate_net_debt_position()`
Purpose: Compute net debt (lent minus borrowed).

`format_signed_currency()`
Purpose: Format amounts with +/- signs.

`show_dashboard()`
Purpose: Orchestrate dashboard data loading and display.

---

## Flow

Load Data
↓
Validate Data
↓
Calculate Summaries
↓
Generate Dashboard Sections
↓
Display Results

---

## Design Decisions

* Read-only architecture
* Reuse existing helper functions
* No new JSON files
* Category resolution using category_id
* Showing deleted categories as "(Deleted)"
* Top 3 expense categories only
* Recent Activity limited to 5 transactions
* Signed amount formatting (+/-)
* Total Account Count wording

---

## Key Learnings

* Data aggregation
* Read-only reporting
* Cross-feature integration
* Sorting
* Filtering
* Financial calculations
* Dashboard design
* Defensive programming

---

## Known Limitations

* No analytics
* No budgeting
* No charts
* No trend analysis
* No AI insights

---

## Review Improvements

* Added signed transaction formatting (+/-)
* Improved dashboard validation
* Fixed account count wording
* Improved malformed data handling

---

## Future Improvements

* Analytics
* Budget tracking
* Savings rate
* Monthly trends
* Charts
* AI insights
---
---

# Feature 9: Transfer Money Between Accounts

## Purpose

The transfer feature was added to allow users to move money between their own accounts while maintaining complete financial integrity.

A transfer represents the movement of money between two accounts owned by the user. It is distinctly different from:

* **Income**: New money entering the system from an external source.
* **Expense**: Money leaving the system to an external entity.

Transfers should not affect income or expense totals because the overall net worth of the user within the system remains unchanged. Treating a transfer as an expense or income would artificially inflate the financial reports, making the user appear to have earned or spent more than they actually did.

---

## Business Rules

* Transfer is a separate transaction type
* Transfer is not income
* Transfer is not expense
* Same account transfers not allowed
* Insufficient balance validation
* Credit Card exception
* Optional notes
* Custom date support
* Future dates not allowed
* Confirmation screen required
* One transfer = one transaction record
* Transfers stored in transactions.json
* Transfers use from_account_id and to_account_id
* Transfer deletion allowed
* Transfer deletion reverses balances
* Unsafe reversals blocked
* Credit Card deletion exception
* Transfers cannot be edited
* Referenced accounts cannot be deleted
* Atomic execution
* Dashboard recent activity includes transfers

---

## Functions

`transfer_money()`
Purpose: Initiates the transfer creation flow, validating sufficient balances, preventing same-account selection, checking date validity, and atomically executing the balance updates and transaction save.

`delete_transfer()`
Purpose: Presents a list of transfers and handles deletion. It safely reverses the balance changes without putting normal accounts into the negative, and removes the transfer from the transaction history atomically.

`is_account_referenced_by_transfers()`
Purpose: A helper function that scans the transaction history to check if an account is part of any transfer, fulfilling future account deletion validation requirements.

`validate_transaction()`
Purpose: Validate transaction records while supporting different schemas for Income, Expense, and Transfer transactions. Transfer validation uses `from_account_id` and `to_account_id` instead of `account_id` and `category_id`.

`display_transaction_table()`
Purpose: Display transfer transactions using dynamic `Source Account -> Destination Account` formatting while maintaining compatibility with Income and Expense transaction display logic.

`get_recent_transactions()`
Purpose: Retrieve the latest valid transactions, including Transfer records, for dashboard Recent Activity display.

`show_dashboard()`
Purpose: Integrate Transfer transactions into Recent Activity while ensuring transfers remain excluded from income and expense calculations.

---

## Flow

Select Source Account
↓
Select Destination Account
↓
Validate Different Accounts
↓
Enter Amount
↓
Validate Balance Rules
↓
Enter Date
↓
Validate Date
↓
Enter Notes
↓
Show Confirmation Screen
↓
Execute Transfer
↓
Save Transaction
↓
Update Account Balances

**Deletion Flow:**
Select Transfer to Delete
↓
Validate Safe Balance Reversal
↓
Show Confirmation Screen
↓
Reverse Balances
↓
Remove Transaction Record
↓
Save Updates Atomically

---

## Design Decisions

* **One transfer record instead of two records**
  Storing one `"Transfer"` record instead of a paired Income and Expense record ensures that financial reporting aggregates do not accidentally count transfers as cash flow.
* **Use transaction type "Transfer"**
  Explicitly separating the type allows standard validation logic and UI rendering functions to uniquely format transfer data (like `Bank -> Investment`) without breaking existing logic.
* **Store in transactions.json**
  Keeping all transaction history in a single file preserves the chronological timeline of the user's financial activity, allowing unified views without cross-file sorting overhead.
* **Use account IDs instead of account names**
  Maintains referential integrity. If an account is ever renamed, the transfer history automatically reflects the new name during dynamic UI resolution.
* **No transfer editing**
  Editing implies simultaneously modifying dates, amounts, and two separate account balances. Reversing and recreating (deleting and adding new) is significantly safer than writing complex edit-in-place financial update logic.
* **Atomic save protection**
  Provides application-level rollback protection by storing backup copies of account and transaction data before execution. If a save operation fails, the previous state can be restored to reduce the risk of data inconsistency.
* **Confirmation before execution**
  Transfers update two accounts at once. Explicitly confirming the details prevents accidental cross-account corruption from user typos.
* **Dashboard integration**
  Transfer events organically integrate into the Recent Activity feed, providing a comprehensive audit trail of money movement at a glance.
* **Transfer history integration**
  Ensures transfers appear chronologically among normal income and expenses for full transparency.
* **Credit Card special handling**
  Credit cards natively operate with negative balances (representing owed debt rather than liquid cash), so typical insufficient balance rules are suspended to accommodate paying off credit statements.

---

## Key Learnings

* **Financial integrity:** Ensuring that moving money from one bucket to another does not mistakenly alter global net worth or gross cash flow statistics.
* **Atomic transactions:** Developing a reliable fallback mechanism (`try/except` with `copy.deepcopy()`) to ensure partial updates never permanently corrupt the system if I/O operations fail.
* **Data consistency:** Guaranteeing that the `from_account` and `to_account` always maintain equilibrium by subtracting and adding the exact same values synchronously.
* **Rollback logic:** Understanding how to cache previous states in memory before executing destructive file writes, and gracefully recovering those states upon system errors.
* **Cross-account operations:** Managing complex flows where user choices on one variable (e.g., source account) strictly influence valid options on another (e.g., preventing same-account selection).
* **Validation chains:** Linking multiple business rules (balances, dates, valid types) to act as a solid gateway before executing a transaction.
* **Transaction modeling:** Learning how to adapt an existing schema (removing `category_id` and injecting `from_account_id` / `to_account_id`) to support entirely distinct concepts within a unified data store.
* **Relational references using IDs:** Preventing hardcoded strings in transaction logs to allow dynamic resolution, ensuring data remains accurate regardless of future upstream changes.
* **Defensive programming:** Building explicit blocks against edge cases, such as blocking the reversal of a transfer if it would drop a normal account balance below zero.
* **Business rule enforcement:** Strictly implementing future constraints (e.g., account deletion protection) early on via dedicated helper logic.
* **Data Modeling:** Learning how a single transaction system can support multiple business concepts (Income, Expense, and Transfer) using different record structures while still remaining inside one unified storage file and one transaction history timeline. Transfer records use a different schema because they represent internal money movement rather than external cash flow, so they do not need categories. However, maintaining all types inside `transactions.json` preserves a single, chronological timeline of financial activity. The key benefit of this unified transaction model is that cross-system features like the Dashboard's Recent Activity feed and global sorting logic can operate seamlessly across all transaction types without requiring complex, multi-file queries or data merging.

---

## Known Limitations

* No recurring transfers
* No scheduled transfers
* No transfer fees
* No transfer editing
* No multi-currency support
* No transfer analytics

---

## Review Improvements

* **Fixed date validation:** Blank input still defaults to today, while invalid or future dates are rejected in a strict loop.
* **Added future date validation:** Specifically blocked future dates so transfer history stays real and chronological.
* **Added rollback protection:** Backups of memory state are now taken immediately before execution, allowing safe aborts on I/O failure.
* **Improved atomic execution:** Linked the `save_transactions` and `save_accounts` methods in a unified `try/except` block to prevent half-writes.
* **Fixed dashboard wording:** Updated "Active Account Count" to "Total Account Count" because the system does not track inactive accounts.
* **Added transfer cancellation protection:** Implemented and proved that answering `N` during the confirmation prompt leaves the system state completely untouched.

---

## Future Improvements

* Recurring transfers
* Scheduled transfers
* Transfer analytics
* Transfer search/filtering
* Transfer categories
* Multi-currency support
* Bank integration

---

# Post-Development Refactoring & Stability Improvements

## Major Bugs Fixed

* Future dates are now rejected in transfer and debt/repayment flows.
* Repayment date checks now respect the debt creation date.
* Transfer deletion and debt/repayment deletion now reverse balances safely.
* Invalid transaction records are skipped cleanly instead of breaking summaries.

## Atomic Save Improvements

* Multi-file financial writes now use deep-copied rollback state before any save.
* Transaction/account updates, debt creation, repayment creation, and deletion flows all restore the previous state if a save fails.
* This prevents half-written JSON files and balance mismatches.

## Cleanup Work Performed

* Removed obsolete helper references and cleaned up redundant code created during earlier development iterations.
* Kept `format_signed_currency()` and `get_valid_transactions()` because the dashboard still uses them.
* Kept `is_account_referenced_by_transfers()` as a future helper for account deletion validation.
* Aligned transaction, debt, transfer, and dashboard notes with the current category-aware schema.

## Lessons Learned

* Rollback protection matters as much as validation in money-related flows.
* Shared helpers should be reused only when their behavior stays identical.
* Financial features are easier to maintain when every write path is treated as an atomic transaction.

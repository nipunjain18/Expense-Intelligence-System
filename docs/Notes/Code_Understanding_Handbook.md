# Expense Intelligence System - Code Understanding Handbook

We won't talk about theoretical software design. We are going to look strictly at what the code does, why it does it, and what happens when it breaks.

By the end of this guide, you will be able to trace a transaction from your keyboard to the hard drive without looking at `main.py`.

---

## 1. How The System Thinks

Before we read code, you need to understand how the system models reality.

### Accounts
Think of Accounts as the **current reality**.
If your HDFC Bank account says ₹10,000, that is the truth right now. Accounts are the physical buckets holding water.
**What happens in the code:** The system loads `accounts.json` into memory as a list of dictionaries. When money moves, the system finds the specific account dictionary and mutates the `"balance"` key. That's it. It’s just changing a number in memory.

### Transactions
Transactions are **not** the truth. Transactions explain **HOW** the truth changed.
If the Account is the bucket of water, the Transaction is the receipt proving someone poured water in or scooped it out.
**What happens in the code:** Every time an Account's balance changes, the code forces you to append a new dictionary to `transactions.json`. A transaction is completely immutable once written.

### Categories
Categories are just the **labels on the receipts**.
They do not affect math. They do not hold money. They just answer the question, "Why did you spend this?"
**What happens in the code:** When you make a transaction, the code asks for a Category. It saves the `category_id` into the transaction record.

### Debts
Debts are a **shadow ledger**.
Sometimes you give money to a friend. The reality (Account) says the money is gone. The cash flow history (Transaction) says it was spent. But in the real world, you expect it back. Debts exist to track that expectation.
**What happens in the code:** When you lend money, the system creates a Transaction (to deduct your Account) AND creates a separate Debt record to track the IOU. 

### Repayments
Repayments are **fulfillment receipts** for Debts.
When your friend pays you back, you don't just add money to your account. You have to tell the shadow ledger that the debt is smaller now.
**What happens in the code:** A Repayment reduces the `"remaining_amount"` on a Debt, AND creates an Income Transaction to put the money back in your Account.

### Transfers
Transfers are a **teleportation event**.
You moved ₹500 from your Wallet to your Bank. Your net worth didn't change.
**What happens in the code:** The code deducts ₹500 from Account A, adds ₹500 to Account B, and writes exactly **one** special transaction record that points to both accounts.

### Dashboard
The Dashboard is a **read-only observer**.
**What happens in the code:** It loads every single JSON file, loops through them, does some math (summing things up), and prints it to the screen. It never changes data.

---


### Module Mental Models

### Accounts Module
**Purpose:** Store current liquid balances.
**Core Responsibility:** Act as the physical containers for funds.
**What It Owns:** `accounts.json`, Account creation/validation logic.
**What It Depends On:** Storage Layer.
**What Depends On It:** Transactions, Transfers, Debts, Repayments, Dashboard.
**Critical Functions:** `add_account()`, `get_valid_balance()`.
**Critical Business Rules:** Balance cannot be negative (except Credit Cards). Names must be unique.
**Failure Impact:** Total system failure. Money cannot be spent, transferred, or lent if balances cannot be resolved.
**Mental Model:** Accounts represent the current physical reality. Transactions simply explain how reality changed.

### Transactions Module
**Purpose:** Explain how balances changed over time.
**Core Responsibility:** Log immutable events of money moving.
**What It Owns:** `transactions.json`, Income/Expense routing.
**What It Depends On:** Accounts (to fund), Categories (to classify), Storage Layer.
**What Depends On It:** Dashboard, Transfer logic, Debt logic.
**Critical Functions:** `_add_transaction()`, `validate_transaction()`.
**Critical Business Rules:** Expense $\le$ Account Balance. Amount must be finite and $> 0$.
**Failure Impact:** Cash flow history is lost. Balances lose their mathematical audit trail. Dashboard aggregates fail.
**Mental Model:** Transactions are the receipts. 

### Categories Module
**Purpose:** Provide analytical meaning to transactions.
**Core Responsibility:** Grouping and metadata management.
**What It Owns:** `categories.json`
**What It Depends On:** Storage Layer.
**What Depends On It:** Transactions, Dashboard.
**Critical Functions:** `ensure_default_categories()`, `is_duplicate_category_name()`.
**Critical Business Rules:** Global uniqueness. Soft deletes only. System defaults cannot be modified.
**Failure Impact:** Transactions cannot be created (missing mandatory metadata). Dashboard crashes during spending analysis.
**Mental Model:** Categories are the labels on the folders. They don't hold money, they just explain intent.

### Debt Tracking Module
**Purpose:** Track interpersonal IOUs independently of cash flow analytics.
**Core Responsibility:** Manage the lifecycle of Lent/Borrowed money and partial fulfillments.
**What It Owns:** `debts.json`, `repayments.json`
**What It Depends On:** Accounts, Transactions, Categories (hidden defaults), Storage Layer.
**What Depends On It:** Dashboard.
**Critical Functions:** `add_debt()`, `add_repayment()`, `delete_debt()`, `delete_repayment()`.
**Critical Business Rules:** One Debt = One Account. Repayment $\le$ Remaining Amount. Deletion blocked if repayments exist.
**Failure Impact:** Financial drift. Reversing a repayment could corrupt core account balances if the relational logic breaks.
**Mental Model:** A shadow ledger that piggybacks on Transactions to move money, while maintaining a separate balance sheet for counter-parties.

### Transfers Module
**Purpose:** Lateral movement of funds without affecting cash flow.
**Core Responsibility:** Shifting balances between two Accounts.
**What It Owns:** Transfer logic loop.
**What It Depends On:** Accounts, Transactions, Storage Layer.
**What Depends On It:** Dashboard (Recent Activity).
**Critical Functions:** `transfer_money()`, `delete_transfer()`.
**Critical Business Rules:** Source $\ne$ Destination. Reversal blocked if destination lacks funds.
**Failure Impact:** Money could duplicate or vanish if the dual-account update loses atomicity.
**Mental Model:** A teleportation event. Money disappears from Account A and instantly appears in Account B via a single record.

### Dashboard Module
**Purpose:** Aggregation and Visualization.
**Core Responsibility:** Transform raw JSON into human-readable insights.
**What It Owns:** Mathematical aggregator functions.
**What It Depends On:** Accounts, Transactions, Categories, Debts.
**What Depends On It:** Nothing (Terminal node).
**Critical Functions:** `calculate_income_expense_summary()`.
**Critical Business Rules:** Must strictly ignore "Transfer" type transactions when calculating Net Cash Flow.
**Failure Impact:** User loses high-level visibility, though no physical data corruption occurs.
**Mental Model:** A read-only observer. It mutates nothing.

### Storage Layer
**Purpose:** Handle all physical disk interactions safely.
**Core Responsibility:** Read/Write JSON safely.
**What It Owns:** File I/O.
**What It Depends On:** `json`, `os`.
**What Depends On It:** Every module.
**Critical Functions:** `load_json_file()`.
**Critical Business Rules:** Assume files are hostile. Never crash on `JSONDecodeError`.
**Failure Impact:** Application fails to boot or saves corrupted fragments.
**Mental Model:** The vault door.

---

## 2. Follow The Money

This is the most important section. To understand the code, you must understand exactly how money moves during an operation.

### Expense Example
**Before:**
Account Balance: ₹10,000
User Action: Food Expense ₹500

**What Happens in Code?**
- **Step 1:** The system deepcopies the current lists in memory (Safety net).
- **Step 2:** The system reduces the Account Balance in memory: `10000 -> 9500`.
- **Step 3:** The system creates an Expense Transaction record for ₹500.
- **Step 4:** The system delegates to `_atomic_save()` to handle writing to both files safely.

**After:**
Account Balance: ₹9500
Transaction History: +1 record

**Why?**
Because the Account must always reflect current reality, and the Transaction must always prove why the reality changed.

### Income Example
**Before:**
Account Balance: ₹10,000
User Action: Salary Income ₹5,000

**What Happens in Code?**
- **Step 1:** Deepcopy lists.
- **Step 2:** Increase Account Balance: `10000 -> 15000`.
- **Step 3:** Create Income Transaction record for ₹5,000.
- **Step 4:** Delegate to `_atomic_save()` for both files.

### Transfer Example
**Before:**
Account A (Wallet): ₹10,000
Account B (Bank): ₹0
User Action: Transfer ₹2,000 from Wallet to Bank

**What Happens in Code?**
- **Step 1:** Check if Wallet has $\ge$ ₹2,000.
- **Step 2:** Deepcopy lists.
- **Step 3:** Deduct from Wallet: `10000 -> 8000`.
- **Step 4:** Add to Bank: `0 -> 2000`.
- **Step 5:** Create ONE Transfer Transaction record pointing to both accounts.
- **Step 6:** Atomic save.

**Why ONE transaction?**
If we created an Expense and an Income, the Dashboard would think you "earned" ₹2,000 and "spent" ₹2,000. By making it a specific "Transfer" type, the Dashboard safely ignores it.

### Debt Creation (LENT)
**Before:**
Account Balance: ₹10,000
User Action: Lend friend ₹1,000

**What Happens in Code?**
- **Step 1:** Deepcopy 3 lists (Accounts, Transactions, Debts).
- **Step 2:** Deduct Account Balance: `10000 -> 9000`.
- **Step 3:** Create an Expense Transaction linked to the hidden "Debt Lent" category.
- **Step 4:** Create a Debt record for ₹1,000.
- **Step 5:** Atomic save all 3 files.

### Repayment
**Before:**
Account Balance: ₹9,000
Active Debt Remaining: ₹1,000
User Action: Friend repays ₹400

**What Happens in Code?**
- **Step 1:** Deepcopy 4 lists (Accounts, Transactions, Debts, Repayments).
- **Step 2:** Increase Account Balance: `9000 -> 9400`.
- **Step 3:** Create an Income Transaction linked to "Debt Repayment Received".
- **Step 4:** Create a Repayment record for ₹400.
- **Step 5:** Reduce Debt Remaining: `1000 -> 600`.
- **Step 6:** Atomic save all 4 files.

### Delete Repayment
**What Happens in Code?**
- **Step 1:** Locate the Repayment record. Look up its associated Account, Transaction, and Debt.
- **Step 2:** Reverse math: Subtract the ₹400 from Account Balance. Add ₹400 back to Debt Remaining.
- **Step 3:** Delete the Transaction dict. Delete the Repayment dict.
- **Step 4:** If the Debt was marked "CLOSED", flip it back to "ACTIVE".
- **Step 5:** Atomic save.

---

## 3. System Execution Map

This is the exact call hierarchy of the application. If you follow this tree, you know exactly what function calls what.

```text
main()
│
├── 1. Manage Accounts
│   ├── add_account()
│   └── view_accounts()
│
├── 2. Add Income / 3. Add Expense
│   └── _add_transaction(transaction_type)
│       ├── select_account()
│       ├── select_transaction_category()
│       ├── get_valid_amount()
│       ├── generate_transaction_id()
│       └── _atomic_save()
│
├── 4. View Transactions
│   └── view_transactions()
│       ├── load_json_files()
│       ├── validate_transaction()
│       └── display_transaction_table()
│
├── 5. Transfer Money
│   └── transfer_money()
│       ├── select_account() (Source)
│       ├── select_account() (Destination)
│       ├── get_valid_amount()
│       ├── generate_transaction_id()
│       └── _atomic_save()
│
├── 6. Manage Categories
│   ├── add_category()
│   ├── view_categories()
│   └── delete_category()
│
├── 7. Debt Tracking
│   ├── add_debt()
│   │   ├── create_debt_transaction()
│   │   └── generate_debt_id()
│   ├── add_repayment()
│   │   ├── create_repayment_transaction()
│   │   └── update_debt_status()
│   ├── view_debts()
│   ├── delete_debt()
│   └── delete_repayment()
│
├── 8. Undo Transfer
│   └── delete_transfer()
│
└── 9. Dashboard
    └── show_dashboard()
        ├── calculate_total_balance()
        ├── calculate_income_expense_summary()
        ├── calculate_account_summary()
        ├── calculate_debt_summary()
        ├── calculate_top_expense_categories()
        ├── get_recent_transactions()
        └── calculate_net_debt_position()
```

---

## 4. Runtime Execution Flow

### Accounts Feature
- **Step By Step Walkthrough:** You type "SBI", the code checks if "SBI" already exists. You type a starting balance of 5000. The code generates an ID of `1`, appends the dictionary to memory, and saves `accounts.json`.

### Transactions Feature
- **Step By Step Walkthrough:** You select your Wallet. You select "Food". You enter ₹50. The code subtracts 50 from Wallet in memory. It generates a transaction record. It saves both.

### Debt Tracking Feature
- **Step By Step Walkthrough:** You lend money. The code forces an Expense transaction on your account using a hidden "Debt Lent" category. Then it creates a separate Debt record. When they pay you back ₹400, it creates a Repayment record, creates an Income transaction, and drops the Debt balance to ₹600.

### Transfers Feature
- **Step By Step Walkthrough:** Select Bank. Select Wallet. Enter ₹500. Code subtracts ₹500 from Bank, adds ₹500 to Wallet. Code writes ONE transaction to `transactions.json`.

---

## 5. Function Walkthroughs

This is the most critical section. We are going to rip open the most important functions and look at their organs.

### `_add_transaction(transaction_type)`
- **Purpose:** Adds an Income or Expense.
- **Why This Function Exists:** Instead of writing `add_income()` and `add_expense()` (which share 95% of the same code), we pass a string argument to branch the math logic.
- **What Problem It Solves:** Prevents duplicate code when moving money.
- **Inputs:** `transaction_type` (String: "Income" or "Expense").
- **Outputs:** None (mutates disk state).
- **Files Read:** `accounts.json`, `categories.json`, `transactions.json`
- **Files Written:** `accounts.json`, `transactions.json`
- **Step-by-Step Execution:**
  - **Step 1:** Load Accounts. (Why? We need to know where the money is coming from).
  - **Step 2:** Select Account. (Why? A transaction belongs to a physical bucket).
  - **Step 3:** Select Category. (Why? The dashboard needs to know *what* you bought).
  - **Step 4:** Validate Amount. (Why? Prevent spending more than you have, or entering `nan`).
  - **Step 5:** Deepcopy Memory. (Why? If the save fails halfway, we need to restore the pristine state).
  - **Step 6:** Math Check. (If Income: `balance + amount`. If Expense: `balance - amount`).
  - **Step 7:** Create Transaction Dict.
  - **Step 8:** Call `_atomic_save()` passing the new and backup memory states.

### `add_debt()`
- **Purpose:** Creates a new IOU.
- **Why This Function Exists:** To initiate the shadow ledger.
- **What Problem It Solves:** Ensures that lending money correctly deducts from your physical account while simultaneously registering the IOU.
- **Files Read:** `accounts.json`, `debts.json`, `transactions.json`
- **Files Written:** All 3.
- **Step-by-Step Execution:**
  - **Step 1:** Get Debt Type (Lent vs Borrowed).
  - **Step 2:** Select Account to fund the loan.
  - **Step 3:** Enter person's name. Check if an active debt already exists for them (warns user).
  - **Step 4:** Get amount.
  - **Step 5:** Deepcopy all 3 lists.
  - **Step 6:** Call `create_debt_transaction()`. (Why? We need a transaction record to explain where the money went. This helper function modifies the account balance AND appends the transaction).
  - **Step 7:** Create Debt Dict. Link it to the `transaction_id`.
  - **Step 8:** Call `_atomic_save()` for all 3 files.

### `add_repayment()`
- **Purpose:** Fulfill part of a Debt.
- **Why This Function Exists:** To allow partial paybacks over time instead of requiring full lumpsums.
- **Step-by-Step Execution:**
  - **Step 1:** Select active Debt.
  - **Step 2:** Select destination Account.
  - **Step 3:** Enter Amount. (Why the truncation check? If they owe ₹400 and pay ₹500, the system forces it to ₹400 so the debt doesn't become negative).
  - **Step 4:** Deepcopy 4 lists.
  - **Step 5:** Call `create_repayment_transaction()`. (Updates Account balance, creates Income transaction).
  - **Step 6:** Create Repayment Dict.
  - **Step 7:** Deduct amount from `debt["remaining_amount"]`.
  - **Step 8:** Call `update_debt_status()`. (Why? If remaining is 0, it flips status to CLOSED).
  - **Step 9:** Call `_atomic_save()` for all 4 files.

### `delete_repayment()`
- **Purpose:** Reverse an accidental repayment entry.
- **Why This Function Exists:** Fixing mistakes manually in JSON is dangerous.
- **Step-by-Step Execution:**
  - **Step 1:** Locate the Repayment. Look up the Debt, Transaction, and Account it touches.
  - **Step 2:** Deepcopy 4 lists.
  - **Step 3:** Call `_reverse_transaction()` to handle account math and transaction removal.
  - **Step 4:** Add amount back to Debt `remaining_amount`.
  - **Step 5:** `repayments.remove(repayment_dict)`.
  - **Step 6:** Call `update_debt_status()` to flip it back to ACTIVE if necessary.
  - **Step 7:** Call `_atomic_save()`.

### `transfer_money()`
- **Purpose:** Move money between accounts.
- **Files Read/Written:** `accounts.json`, `transactions.json`.
- **Step-by-Step Execution:**
  - **Step 1:** Select Source Account.
  - **Step 2:** Select Destination Account. (Verify they are different).
  - **Step 3:** Check Source balance.
  - **Step 4:** Deepcopy lists.
  - **Step 5:** Deduct Source balance. Add to Destination balance.
  - **Step 6:** Create ONE Transaction. Instead of `category_id`, it uses `from_account_id` and `to_account_id`.
  - **Step 7:** Call `_atomic_save()`.

### `show_dashboard()`
- **Purpose:** The analytics brain.
- **Why This Function Exists:** To answer "Where did my money go?"
- **Files Read:** All of them.
- **Files Written:** NONE.
- **Step-by-Step Execution:**
  - **Step 1:** Load all JSON files.
  - **Step 2:** Pass the lists to isolated calculator functions (e.g., `calculate_account_summary(accounts)`).
  - **Step 3:** Each function iterates over the lists, summing numbers.
  - **Step 4:** `show_dashboard` prints the final calculated numbers formatted beautifully.

---

## 6. Relationship Walkthroughs

The system is a spiderweb of IDs connecting records.

```text
Account (ID: 1)
│
├── Transaction (ID: 105) ────> Category (ID: 4)
│
├── Debt (ID: 1) ─────────────> Transaction (ID: 106)
│   │
│   └── Repayment (ID: 1) ────> Transaction (ID: 107)
│
└── Transfer (ID: 108) ───────> Account (ID: 2)
```

**Why relationships exist:**
If we stored the string `"SBI"` inside a transaction, and you later renamed the account to `"State Bank"`, all old transactions would break. By storing `account_id: 1`, the transaction always points to the exact object, regardless of what its name is.

**What breaks if IDs are wrong:**
If a Repayment record says it belongs to `debt_id: 99`, but `debt_id: 99` doesn't exist, the UI will crash trying to render the repayment, because it cannot resolve the parent object.

---


### Implementation Relationships
**Example: `delete_repayment()`**
- **Uses:** `repayment_id` $\rightarrow$ `debt_id` $\rightarrow$ `transaction_id` $\rightarrow$ `account_id`

**Focus:** How the relationship is used in code to traverse dictionaries and reverse math.
## 7. Function Dependency Maps

These maps show exactly what functions must succeed for a core feature to work.

### `add_account()`
```text
add_account()
│
├── load_accounts()
├── is_duplicate_name()
├── get_valid_account_type()
├── get_valid_balance()
├── generate_account_id()
└── save_accounts()
```
- **Purpose:** Create a new storage bucket.
- **Why called:** To fund transactions.
- **What breaks if it fails:** You cannot add money or spend it.

### `_add_transaction()`
```text
_add_transaction()
│
├── ensure_default_categories()
├── load_accounts()
├── select_account()
├── select_transaction_category()
├── load_transactions()
├── get_valid_amount()
├── generate_transaction_id()
└── _atomic_save()
```
- **Purpose:** Primary mutation loop for cash flow.
- **Why called:** To record Income or Expense.
- **What breaks if it fails:** The physical balance changes, but the receipt isn't written (Atomicity failure).

### `view_transactions()`
```text
view_transactions()
│
├── load_transactions()
├── load_accounts()
├── load_categories()
├── validate_transaction()
└── display_transaction_table()
```
- **Purpose:** Render cash flow.
- **Why called:** User wants to see history.
- **What breaks if it fails:** UI crashes, data is hidden.

### `add_debt()`
```text
add_debt()
│
├── get_or_create_debt_categories()
├── load_accounts()
├── select_account()
├── load_debts()
├── find_active_debts_by_person()
├── get_valid_amount()
├── get_valid_date()
├── load_transactions()
├── create_debt_transaction()
│   ├── generate_transaction_id()
│   └── (mutates account balance)
├── generate_debt_id()
└── _atomic_save()
```
- **Purpose:** Create an IOU.
- **Why called:** Track money lent or borrowed.
- **What breaks if it fails:** Partial saves leave money deducted from Account but no Debt record created.

### `add_repayment()`
```text
add_repayment()
│
├── load_debts()
├── select_active_debt()
├── load_accounts()
├── select_account()
├── get_valid_date()
├── load_transactions()
├── load_repayments()
├── create_repayment_transaction()
│   ├── generate_transaction_id()
│   └── (mutates account balance)
├── generate_repayment_id()
├── update_debt_status()
└── _atomic_save()
```
- **Purpose:** Log a partial or full fulfillment.
- **Why called:** User received owed money.
- **What breaks if it fails:** Debt remains active despite money returning to the account.

### `delete_repayment()`
```text
delete_repayment()
│
├── load_repayments()
├── load_debts()
├── load_transactions()
├── load_accounts()
└── _atomic_save()
```
- **Purpose:** Reverse an accidental repayment.
- **Why called:** Data entry mistake.
- **What breaks if it fails:** Deleting the repayment but failing to reverse the account math creates ghost money.

### `delete_debt()`
```text
delete_debt()
│
├── load_debts()
├── load_repayments() (to check blocks)
├── load_transactions()
├── load_accounts()
└── _atomic_save()
```
- **Purpose:** Reverse debt creation.
- **Why called:** Data entry mistake.
- **What breaks if it fails:** Bypassing the repayment block destroys referential integrity.

### `transfer_money()`
```text
transfer_money()
│
├── load_accounts()
├── select_account() (Source)
├── select_account() (Destination)
├── load_transactions()
├── get_valid_amount()
├── generate_transaction_id()
└── _atomic_save()
```
- **Purpose:** Move money safely.
- **Why called:** Lateral cash movement.
- **What breaks if it fails:** Source account deducts, Destination fails to add = Money vanished.

### `delete_transfer()`
```text
delete_transfer()
│
├── load_transactions()
├── load_accounts()
└── _atomic_save()
```
- **Purpose:** Reverse lateral move.
- **Why called:** Data entry mistake.
- **What breaks if it fails:** Restoring a transfer forces the destination into negative balance.

### `show_dashboard()`
```text
show_dashboard()
│
├── load_accounts()
├── load_transactions()
├── load_categories()
├── load_debts()
├── calculate_total_balance()
├── calculate_income_expense_summary()
├── calculate_account_summary()
├── calculate_debt_summary()
├── calculate_top_expense_categories()
├── get_recent_transactions()
└── calculate_net_debt_position()
```
- **Purpose:** Analytics.
- **Why called:** Data insight.
- **What breaks if it fails:** Just the UI display; no data is harmed.

---

## 8. Runtime Object Reference

This is how data literally looks in RAM when the python script runs.

### Account
**Example Object:**
`{"account_id": 1, "name": "SBI", "account_type": "Bank", "balance": 500.0, "created_at": "2023-10-01"}`
- **account_id** | `int` | Primary Key. Used by Transactions/Debts. Cannot change.
- **name** | `str` | Display label. Used by UI. Cannot change.
- **account_type** | `str` | Constraint grouping. Used by UI/Validation. Cannot change.
- **balance** | `float` | Current reality. Used by Everything. Changes constantly.
- **created_at** | `str` | Timestamp. Used by UI. Cannot change.

### Transaction
**Example Object:**
`{"transaction_id": 105, "account_id": 1, "category_id": 4, "type": "Expense", "amount": 50.0, "description": "Coffee", "date": "2023-10-05"}`
- **transaction_id** | `int` | Primary Key. Used by Debts/Repayments. Cannot change.
- **account_id** | `int` | Foreign Key to Accounts. Cannot change.
- **category_id** | `int` | Foreign Key to Categories. Cannot change. (Transfers use `from_account_id` and `to_account_id`).
- **type** | `str` | Direction logic (Income/Expense/Transfer). Used by Dashboard. Cannot change.
- **amount** | `float` | Magnitude. Used by Dashboard. Cannot change.
- **description** | `str` | Human readable context. Used by UI. Cannot change.
- **date** | `str` | Chronology. Used by sorting/UI. Cannot change.

### Category
**Example Object:**
`{"category_id": 4, "name": "Food", "type": "Expense", "is_default": True, "is_deleted": False}`
- **category_id** | `int` | Primary Key. Used by Transactions. Cannot change.
- **name** | `str` | Display label. Cannot change.
- **type** | `str` | Filters transaction dropdowns. Cannot change.
- **is_default** | `bool` | Prevents system categories from deletion. Cannot change.
- **is_deleted** | `bool` | Soft delete flag. Used by UI filters. CAN CHANGE.

### Debt
**Example Object:**
`{"debt_id": 1, "transaction_id": 106, "account_id": 1, "person_name": "Rahul", "type": "LENT", "status": "ACTIVE", "original_amount": 1000.0, "remaining_amount": 600.0, "purpose": "Movie", "notes": "", "created_date": "2023-10-05"}`
- **debt_id** | `int` | Primary Key. Used by Repayments. Cannot change.
- **transaction_id** | `int` | Foreign Key. Links to the originating money movement. Cannot change.
- **account_id** | `int` | Foreign Key. Defines which bucket funded this. Cannot change.
- **person_name** | `str` | Identifier. Used by UI. Cannot change.
- **type** | `str` | LENT/BORROWED. Cannot change.
- **status** | `str` | ACTIVE/CLOSED. CAN CHANGE.
- **original_amount** | `float` | Starting bounds. Cannot change.
- **remaining_amount** | `float` | Current debt state. CAN CHANGE.
- **created_date** | `str` | Temporal bounds. Used by Repayment validation. Cannot change.

### Repayment
**Example Object:**
`{"repayment_id": 1, "debt_id": 1, "transaction_id": 107, "account_id": 1, "amount": 400.0, "date": "2023-10-06"}`
- **repayment_id** | `int` | Primary Key. Cannot change.
- **debt_id** | `int` | Foreign Key. Cannot change.
- **transaction_id** | `int` | Foreign Key to the incoming money receipt. Cannot change.
- **account_id** | `int` | Foreign Key. Cannot change.
- **amount** | `float` | Magnitude. Cannot change.
- **date** | `str` | Chronology. Cannot change.

---

## 9. Debugging Through Thinking

Let's teach you how to think when the app breaks.

**Problem: Balance is incorrect.**

**How To Think:**
- **Question 1: Was the account updated?** Open `accounts.json`. Look at the balance. Is it what you expect?
- **Question 2: Was the transaction created?** Open `transactions.json`. Sum all the numbers for that `account_id`. Does the math match `accounts.json`? If no, the files desynced.
- **Question 3: Did a rollback occur?** Did the app crash halfway during a save, and deepcopy failed to restore it?
- **Question 4: Was JSON manually edited?** Did you accidentally delete a transaction from the JSON file by hand but forget to update the account balance?
- **Question 5: Are IDs still linked?** Did someone change the `account_id` in the transaction?

When debugging, always follow the math from the Transaction to the Account. The discrepancy always lives there.

---

## 10. Advanced Debugging Scenarios

When things break in production, follow this playbook.

### Scenario: Account balance incorrect
- **Symptoms:** Dashboard shows ₹500, manual math shows ₹400.
- **Likely Causes:** Rollback failure during a multi-file save.
- **Files To Inspect:** `accounts.json`, `transactions.json`.
- **Functions To Inspect:** `_add_transaction()`.
- **How To Verify:** Run a `sum()` on all transactions for that `account_id` in Python. Compare to `balance` in `accounts.json`.
- **Expected Fix:** Edit `accounts.json` `balance` to perfectly match the transaction sum.

### Scenario: Missing Transaction
- **Symptoms:** You know you bought coffee, but it's not in the list.
- **Likely Causes:** JSON schema is missing a key (e.g., `amount` was deleted by hand).
- **Files To Inspect:** `transactions.json`.
- **Functions To Inspect:** `validate_transaction()`.
- **How To Verify:** The `view_transactions()` function silently skips invalid records. Add a print statement inside the `else` block of `validate_transaction`.
- **Expected Fix:** Correct the JSON syntax.

### Scenario: Broken Debt Status
- **Symptoms:** Debt says ACTIVE but remaining is 0.
- **Likely Causes:** Floating point precision error (`0.0000000001 != 0`).
- **Files To Inspect:** `debts.json`.
- **Functions To Inspect:** `update_debt_status()`.
- **How To Verify:** Print the exact float of `remaining_amount`.
- **Expected Fix:** Round to 2 decimals or manually edit `debts.json`.

### Scenario: Repayment Not Closing Debt
- **Symptoms:** User pays ₹500 on a ₹500 debt, but it stays ACTIVE.
- **Likely Causes:** `update_debt_status()` was bypassed or failed.
- **Expected Fix:** Call `update_debt_status()` dynamically or edit JSON.

### Scenario: Debt Closed Incorrectly
- **Symptoms:** Debt closed prematurely.
- **Likely Causes:** Overpayment truncation logic failed, pushing remaining amount $\le 0$.
- **Files To Inspect:** `repayments.json`.

### Scenario: Transfer Reversal Failure
- **Symptoms:** Cannot delete a transfer.
- **Likely Causes:** Destination account already spent the money. Reversing it drops it $< 0$.
- **Expected Fix:** No code fix. Explain to user they must fund the destination account.

### Scenario: Dashboard Totals Wrong
- **Symptoms:** Income seems artificially high.
- **Likely Causes:** Transfers or Debt Repayments are lacking the correct filters and being counted as raw income.
- **Functions To Inspect:** `calculate_income_expense_summary()`.
- **How To Verify:** Ensure `transaction["type"] == "Income"` ignores Transfers.

### Scenario: Category Lookup Failure
- **Symptoms:** View Transactions crashes.
- **Likely Causes:** Category was hard-deleted from `categories.json` instead of soft-deleted.
- **Files To Inspect:** `categories.json`.
- **Expected Fix:** Manually recreate the category with the exact missing ID and `is_deleted: True`.

### Scenario: Corrupted JSON
- **Symptoms:** Startup crash.
- **Likely Causes:** Missing comma in JSON.
- **Functions To Inspect:** `load_json_file()`.
- **Expected Fix:** Use a JSON linter to fix syntax.

### Scenario: ID Relationship Issues
- **Symptoms:** Repayment links to wrong debt.
- **Likely Causes:** Array indexing assumptions instead of ID matching.
- **Files To Inspect:** `debts.json`, `repayments.json`.

---


### Debugging Playbook

### Incorrect Balance
- **Symptoms:** User sees ₹400 in Dashboard, but transactions sum to ₹600.
- **Likely Causes:** A transaction was saved, but the account save failed (atomicity failure), or the JSON was edited manually.
- **Functions To Inspect:** `_add_transaction()`, `transfer_money()`.
- **Files To Inspect:** `accounts.json`, `transactions.json`.
- **Debug Procedure:** Sum all transactions for the account ID. Compare against current `accounts.json` balance. Check if manual edits were made.
- **Expected Fix:** Correct `accounts.json` balance to match the transaction ledger explicitly.

### Missing Transaction
- **Symptoms:** Transactions view skips known records.
- **Likely Causes:** A record is missing a required key or has a typo in the JSON schema.
- **Functions To Inspect:** `validate_transaction()`.
- **Files To Inspect:** `transactions.json`.
- **Debug Procedure:** Add `print(transaction)` inside the `else` block of `validate_transaction()` to see exactly which record is failing structure checks.
- **Expected Fix:** Correct the JSON syntax manually.

### Debt Not Closing
- **Symptoms:** Remaining amount is 0, but status says ACTIVE.
- **Likely Causes:** Floating point precision error (`0.00000001 != 0`), or `update_debt_status()` was bypassed.
- **Functions To Inspect:** `update_debt_status()`, `add_repayment()`.
- **Files To Inspect:** `debts.json`.
- **Debug Procedure:** Print the exact float value of `remaining_amount`. 
- **Expected Fix:** Round `remaining_amount` to 2 decimals or manually edit `debts.json`.

### Debt Not Reopening
- **Symptoms:** Repayment deleted, but debt still says CLOSED.
- **Likely Causes:** Regression in `delete_repayment()` forgetting to toggle status.
- **Functions To Inspect:** `delete_repayment()`.
- **Files To Inspect:** `debts.json`.
- **Debug Procedure:** Verify `debt["status"] = "ACTIVE"` executes during reversal.
- **Expected Fix:** Manually edit status in JSON and patch `delete_repayment()`.

### Transfer Reversal Failure
- **Symptoms:** Transfer deletion blocked due to "negative balance", but user has money.
- **Likely Causes:** The destination account spent the transferred money. Reversing it would logically drop the account below zero.
- **Functions To Inspect:** `delete_transfer()`.
- **Files To Inspect:** `accounts.json`.
- **Debug Procedure:** Print `to_account["balance"]` and `selected_transfer["amount"]` to verify the mathematical block is working as intended.
- **Expected Fix:** No code fix required. Explain to user they must fund the destination account first.

### Dashboard Totals Incorrect
- **Symptoms:** Income/Expense totals mismatch individual account states.
- **Likely Causes:** Transfers accidentally counted as Income/Expense, or invalid records ignored by `validate_transaction()`.
- **Functions To Inspect:** `calculate_income_expense_summary()`, `validate_transaction()`.
- **Files To Inspect:** `transactions.json`.
- **Debug Procedure:** Check for "Skipped invalid transaction records" warnings.
- **Expected Fix:** Correct corrupted transaction records.

### Category Display Problems
- **Symptoms:** Transactions say "Unknown Category".
- **Likely Causes:** A category was hard-deleted from JSON manually, rather than soft-deleted.
- **Functions To Inspect:** `get_category_name()`.
- **Files To Inspect:** `categories.json`.
- **Debug Procedure:** Identify the orphaned `category_id` in `transactions.json`.
- **Expected Fix:** Restore the category manually to `categories.json` with `is_deleted: True`.

### Corrupted JSON
- **Symptoms:** Application fails to boot or displays warning on startup.
- **Likely Causes:** Malformed syntax (missing comma/bracket) in JSON file.
- **Functions To Inspect:** `load_json_file()`.
- **Files To Inspect:** All `.json` files.
- **Debug Procedure:** Paste JSON contents into a linter.
- **Expected Fix:** Repair JSON syntax.

---

## 11. Code Reading Guide

If you open `main.py` today, DO NOT read it from top to bottom. Read it in this exact order:

**1. Storage Functions (`load_*`, `save_*`, `_atomic_save`)**
- **Why:** Understand how data moves from disk to RAM. Notice the `try...except` blocks protecting against corruption, and how `_atomic_save` guarantees multi-file consistency.

**2. Validation Functions (`get_valid_amount`)**
- **Why:** Understand the gates. See how `math.isfinite` protects the whole application.

**3. Accounts (`add_account`)**
- **Why:** The easiest module. Understand how IDs are generated (`max() + 1`) and how data is appended.

**4. Transactions (`_add_transaction`)**
- **Why:** This introduces the Deepcopy rollback pattern and how it ties into `_atomic_save`. Master this before moving on.

**5. Transfers (`transfer_money`)**
- **Why:** Understand how two accounts are mutated simultaneously, but only one transaction is written.

**6. Debts & Repayments (`add_debt`, `add_repayment`)**
- **Why:** The final boss. Understand how 4 files are updated simultaneously in memory before an atomic save is executed.

**7. Dashboard (`show_dashboard`)**
- **Why:** Read this last. It’s just looping over the data you already understand and summing it up.

### Final Thoughts
When reading this code, always ask yourself: "If the power goes out exactly at this line of code, what state is the JSON left in?" That single question will help you understand 90% of why the code is written the way it is.

---


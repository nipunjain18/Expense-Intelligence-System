


# Expense Intelligence System - Version 1 Learning Notes

---

## Project Overview

**What was built:** A comprehensive, terminal-based Personal Finance Management System written purely in Python. It manages accounts, tracks income and expenses via customizable categories, orchestrates money transfers, and handles complex debt lifecycles (borrowing, lending, partial repayments, and automated balance synchronization).

**Why it was built:** To apply fundamental software engineering principles to a real-world, mathematically strict domain. Building a financial ledger from scratch forces developers to handle edge cases, data persistence, atomic operations, and rigid validation, moving beyond simple CRUD apps.

**Final Version 1 Status:**

Version 1 Feature Complete

All planned Version 1 functionality has been implemented and tested.

The project successfully passed:

- Functional Testing
- Integration Testing
- Corruption Testing
- Rollback Testing
- Performance Testing

Version 1 is considered:

- Stable Release Candidate
- Ready for Personal Production Use
- Strong Portfolio Project

Future versions can improve:

- Automated Testing
- Logging
- Backup Systems
- Modular Architecture
- Database Support

---

## New Skills Acquired

### Technical Skills

* **Data Modeling:** Designed relational schemas across JSON files using integer IDs as foreign keys.
* **Referential Integrity:** Enforced cross-file consistency between accounts, transactions, debts, and repayments without a database engine.
* **Rollback Systems:** Built atomic multi-file save operations with `copy.deepcopy()` snapshots and nested exception handling.
* **Corruption Recovery:** Centralized JSON loading to gracefully handle missing, empty, and malformed files.
* **Performance Analysis:** Identified $O(n^2)$ bottlenecks through stress testing at 50,000+ records.

### Engineering Skills

* **Requirement Analysis:** Translated real-world financial rules into strict programmatic constraints.
* **Edge Case Thinking:** Discovered that `float("nan")`, future dates, and same-account transfers bypass standard validation.
* **Bug Isolation:** Traced root causes across multiple modules (e.g., `nan` appearing in 4 separate entry points).
* **Root Cause Analysis:** Learned to fix the underlying pattern (centralized validation) rather than patching individual symptoms.
* **QA Methodology:** Executed 14 structured test groups covering functional, integration, corruption, rollback, and performance testing.

---


## Version 1 Engineering Mindset Shift

The most significant growth during Version 1 was the transition from **feature-driven development** to **resilience-driven engineering**.

Initially, success was defined as *"does the code execute the happy path?"* By the end of the project, success was defined as *"can the system survive hostile inputs, partial saves, and corrupted states?"*

This shift manifested in several core areas:
* **Validation:** Moving from trusting user input to assuming all inputs (and native language quirks like `float("nan")`) are actively trying to break the math.
* **Rollbacks (Atomicity):** Realizing that saving data to three files is not three operations—it is one operation that must completely succeed or completely fail, utilizing `copy.deepcopy()` to protect state.
* **Corruption Recovery:** Transitioning from blind file reads (`json.loads()`) to defensive I/O wrappers that trap `JSONDecodeError` and OS-level permission failures.
* **Edge Cases:** Discovering that the most dangerous bugs do not live in core calculation logic, but at system boundaries (future dates, same-account transfers, zero balances).
* **Reliability over Features:** Feature development became 20% of the effort; building the hardened infrastructure to protect those features became the other 80%.

## Version 1 Engineering Milestones

* Built working features
* Added validation layers
* Added business rules
* Added relational integrity
* Added rollback protection
* Added corruption recovery
* Added integration testing
* Added performance testing

**Lesson:**
Building features was easy. Making them reliable was the real engineering challenge.
## Major Technical Concepts Learned

### Centralized Storage Architecture
**Why `load_json_file()` was created:** Initially, each module loaded its own JSON files, assuming the files existed and were perfectly formatted. This led to crashes. By centralizing storage infrastructure into one helper, I could enforce system-wide resilience.
**Handling edge cases:**
* **Missing file handling:** If `os.path.exists` is false, it safely returns an empty list `[]` instead of crashing.
* **Empty file handling:** Handles completely empty files gracefully.
* **JSON corruption handling:** Traps `json.JSONDecodeError` to prevent fatal application crashes when a file has invalid syntax.
* **OSError handling:** Catches permission or disk errors defensively.
* **Directory auto-creation:** Guarantees `data/` exists before attempting reads.
**Lessons Learned:** Centralized infrastructure acts as a single source of truth. If a bug is found in file loading, fixing it in `load_json_file()` instantly protects the entire application.

### 1. Data Modeling
**Accounts, Transactions, Categories, Debts, Repayments:** I learned to map real-world financial concepts into structured dictionaries. An Account is a state container (`balance`), while a Transaction is an immutable event that modifies that state. Debts and Repayments are relational layers sitting on top of core transactions.

**Lessons Learned:**
* **Why IDs are better than names:** Names change and duplicate. Generating and storing unique integer IDs (`account_id`, `category_id`) guarantees that references remain unbreakable even if the user renames their "Bank" to "Checking".
* **Why relationships matter:** A debt repayment isn't just money moving—it's a change to an Account's balance, a decrease in a Debt's `remaining_amount`, and a permanent Transaction record. Tying these together via IDs is what makes the ledger accurate.

### 2. Validation Evolution & Systems
**What it means:** Validation is the security checkpoint of software. It proves data is mathematically, structurally, and logically sound before the application trusts it.

**Evolution from Feature-Specific to Centralized Validation:**
Initially, each feature (like `add_income` or `transfer_money`) had its own `while True` loop validating inputs. This caused duplicated logic and inconsistent rules. By moving to centralized validation helpers (`get_valid_balance()`, `get_valid_amount()`, `get_valid_date()`, `validate_transaction()`, `validate_category_name()`), the system became strictly uniform.
**Lessons Learned:** 
* **Defensive programming mindset:** Never trust user input, external files, or even other internal functions.
* **Why validation should be reusable:** Centralized functions guarantee that "amount" means the exact same thing whether it's an expense or a debt repayment. 

**NAN / Infinity Bug Lesson:**
* **Dangerous Quirks:** Python's `float("nan")` and `float("inf")` bypass normal mathematical comparisons. `nan > 5000` evaluates to `False`, allowing a user to sneak `nan` past a maximum-value check!
* **Mandatory Fix:** Using `math.isfinite()` became absolutely mandatory across all financial inputs to block these non-real numbers.
* **Lesson Learned:** You can't just validate against what you *expect* a user to do; you must consider the deep technological limitations and quirks of the language itself during validation.

### Validation Layers

Validation exists at multiple levels:

- Input Validation
- Data Validation
- Business Rule Validation
- Relationship Validation

Lesson:
A value can be technically valid while still violating business rules.

**Examples & Lessons:**
* **ACC-001 (Negative Balances):** Allowed creating accounts with sub-zero balances. Taught me to enforce domain constraints immediately at data entry.
* **INC-001, TRN-001, REP-001 (`float("nan")` bypasses):** Addressed via the centralized `math.isfinite()` defense mechanism.

### 3. Rollback Systems
**Why it exists:** When a user creates a Debt, the application modifies `debts.json`, `transactions.json`, and `accounts.json`. If the application crashes halfway through saving these files, the database enters a permanently corrupted "partial" state.
**How it works:** Taking a snapshot via `copy.deepcopy()` before changing any data. If an `Exception` occurs during the save sequence, the system forcefully overwrites the files with the pristine snapshot.
**The ATOM-001 Lesson:** A rollback is still an I/O operation! If the first save fails due to a disk error, the rollback save will likely fail too. The rollback sequence itself must be protected by a nested `try...except` block to prevent cascading unhandled crashes.

### Deep Copy vs Assignment

`old_accounts = accounts`

does not create a backup.

Both variables point to the same object.

`copy.deepcopy(accounts)`

creates an independent snapshot.

Lesson:
Rollback systems are impossible without true copies.

### 4. Corruption Recovery
**The REC-001 Bug:** The system assumed `json.loads()` would always succeed if a file existed. If a file got corrupted (e.g. `{ invalid syntax `), the app crashed entirely on startup.
**Why it matters:** Users can accidentally edit JSON files. A system crash is unacceptable.
**The Fix & Lesson:** Centralized JSON loading into a `load_json_file()` helper that specifically traps `json.JSONDecodeError` and `OSError`, gracefully returning an empty list and warning the user, keeping the application alive. Assume all external files are hostile.

### 5. Soft Delete Architecture
**Why it's used:** If a user deletes a category called "Food", but 50 historical transactions use `category_id: 5`, deleting the category record breaks history. 
**The Lesson:** Hard deletes corrupt relational databases. By adding an `"is_deleted": True` flag, the category disappears from UI menus but remains available so old transactions render correctly. Historical immutability is paramount in financial software.

### 6. Relational Data Design
**Why references are safer than duplicated data:** If a transaction stored the literal string `"Bank"` instead of `account_id: 1`, and the user later renamed the account to `"Checking"`, I would have to search and update thousands of transaction records. By referencing an ID, I only update the name in one place, and the entire system instantly reflects the change. Single source of truth.

### Single Source of Truth

Store IDs instead of names.

Derive information instead of duplicating it.

Lesson:
Duplicated state eventually becomes inconsistent.

---


# Feature Architecture & Engineering Case Studies

## Feature 5: Category Management (Design Decisions)

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

## Design Decisions

- **`category_id` instead of category name:** Names change over time. If a user renames "Gym" to "Fitness", using a stable numeric ID ensures that all past transactions pointing to ID `11` instantly reflect the new name. Linking by name would require updating every historical transaction during a rename.
- **Soft delete instead of hard delete:** Financial data relies on historical accuracy. Permanently deleting a category would break past transactions linked to it. Soft deletion preserves referential integrity by merely hiding the category from active selection menus while keeping the data intact for reporting.
- **Global uniqueness instead of type-based uniqueness:** Allowing identical names across types creates data ambiguity where an Expense category named "Food" and an Income category named "Food" could coexist simultaneously. Enforcing global uniqueness ensures that AI insights and analytics can group data purely by name without NLP confusion.
- **Type inferred from menu instead of asking the user:** The submenu directly routes to "Add Expense Category" and "Add Income Category" rather than asking the user for the type after they start the creation flow. This reduces prompts and minimizes user error by establishing intent upfront.
- **Unified `select_category()` helper instead of separate selection functions:** Consolidated the repetitive selection flow for renaming, deleting, and restoring into a highly flexible helper function. This enforces the DRY principle and dramatically reduces code duplication.

---


---

---

---


## Feature 6: Category Integration (Data-Model Evolution)

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

---

---

## Design Decisions

- **Separate user menus (`add_income`, `add_expense`) but shared internal logic (`_add_transaction`):** Provides a clean user experience while reusing code.
- **Use `category_id` instead of `category_name`:** Names can change; IDs remain stable.
- **Resolve category names dynamically when viewing transactions:** Supports renaming, deleting, and restoring categories without having to update old transaction records.
- **Display deleted categories as `[Name] (Deleted)`:** Keeps old transactions readable without breaking the UI.

---

---

---

---
---


## Feature 7: Debt Tracking (Engineering Case Study)

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

---

---

---
---


## Feature 9: Transfer Architecture (Case Study)

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

---

---

---

---


## Bugs and Engineering Lessons

| BUG | CAUSE | FIX | LESSON |
| :--- | :--- | :--- | :--- |
| **ACC-001** | Account creation logic did not check if the initial balance was `< 0`. | Added strict `>= 0` conditional loops to the account creation prompt. | Always validate initial state, not just ongoing mutations. |
| **INC-001** | Python's `float()` accepted `"nan"` and `"inf"`, bypassing conditional checks entirely. | Centralized amount validation using `math.isfinite()`. | Never trust native type casting. Understand language-level quirks for data types. |
| **TRN-001** | `transfer_money` implemented its own fragile validation loop instead of using the hardened helper. | Rerouted `transfer_money` to use `math.isfinite()`. | Don't Repeat Yourself (DRY). Inline, duplicated logic breeds inconsistent vulnerabilities. |
| **REP-001** | `add_repayment` did manual `nan` vulnerable checks when verifying `remaining_amount` overpayments. | Enforced `math.isfinite()` and strict bounds checks in the repayment loop. | Every entry point that touches a mathematical ledger must be guarded identically. |
| **REC-001** | `json.loads()` was called without a `try-except` wrapper, causing fatal startup crashes on bad syntax. | Wrapped all loaders in a centralized helper that catches `JSONDecodeError`. | External states (files, networks) are volatile and untrustworthy. Catch I/O exceptions defensively. |
| **ATOM-001** | The `except Exception` rollback block failed to catch secondary exceptions if the rollback save itself failed. | Added a nested `try...except` inside the rollback block. | Error handling code must itself be fault-tolerant. Anticipate cascading systemic failures. |
| **DATE-001** | Future dates were accepted, which corrupted the financial timeline. | Future date validation blocked inputs greater than `date.today()`. | Valid format does not mean valid business data. |
| **DEBT-001** | Repayment date could occur before debt creation date, causing chronological inconsistency. | Minimum date validation referencing the debt's creation date. | Cross-record validation is often more important than single-field validation. |

---

## Testing Lessons

### Bug Discovery Pattern

Most bugs were not calculation bugs.

Most bugs came from:

- Missing validation
- Missing business rules
- Missing relationship checks
- Unhandled I/O failures
- Incorrect assumptions

Lesson:
The highest-risk parts of software are usually system boundaries.

**Summary of QA:** We executed 14 Test Groups progressing from Accounts to Transactions, Transfers, Debts, multi-module integrations, JSON corruption, save-failures, and finally extreme-scale performance profiling.

* **Testing Early vs Late:** Because I didn't test float validation thoroughly until Group 5 (Transfers), the `nan` bug was discovered in multiple places, requiring repetitive fixes. I should have hardened the base validation functions before building complex features.
* **Edge Cases:** QA is about breaking things. Testing `float("inf")`, zero-balance transfers, and identical source/destination accounts found more bugs than standard "happy path" testing.
* **Regression Testing:** Every time I fixed a bug, I re-ran the suite. This proved that fixing ATOM-001 didn't break standard transactions.
* **Stress Testing & Performance Findings:** Throwing large datasets at Python proved the language's memory management is excellent, but highlighted algorithmic bottlenecks.
  * **Largest Dataset Tested:** 1,000 Accounts, 50,000 Transactions, 2,000 Debts, 5,000 Repayments.
  * **Peak Memory Usage:** ~30 MB.
  * **Bottlenecks Discovered:** `view_repayments()` suffered from an $O(n^2)$ loop, causing UI lag. `get_account_name()` and `get_category_name()` executed $O(n)$ lists scans inside transaction loops. `get_recent_transactions()` had heavy sorting costs on the full list, and the dashboard suffered from repeated identical full-list scans.
  * **Lessons Learned:** Big O notation strictly dictates application performance. Shifting from list iterations to dictionary indexing ($O(1)$) is mandatory. Algorithms matter significantly more at scale than hardware or language speed.

---

## Architecture Decisions That Worked Well

* **JSON Storage:** Extremely lightweight and easy to inspect manually for debugging.
* **Soft Deletes:** Preserved the strict mathematical and visual integrity of the ledger when removing accounts or categories.
* **Relational IDs:** Kept the JSON files small and made renaming operations trivial and safe.
* **Rollback Strategy:** `copy.deepcopy()` proved to be an incredibly effective, simple way to maintain transaction atomicity without needing a formal SQL engine.

---

## Engineering Decisions I Designed Myself

Document the major design decisions created during development.

* **Debt Category Architecture**: System-generated debt categories are strictly siloed from user selection.


---

## Architecture Decisions I Would Change

* **Large `main.py`:** A monolithic 1,900-line file is difficult to navigate. Version 2 must be split into modular domains.
* **Duplicated Validation:** Inline `while True` loops caused duplicate logic. Version 2 requires a dedicated prompt manager.
* **$O(n^2)$ Lookups:** Iterating over all debts inside rendering loops lags at scale. Version 2 must load lists into dictionaries for $O(1)$ lookups.

---

---

## Biggest Mistakes

* **Inline Validation:** I allowed `transfer_money` to write its own validation checks instead of forcing it to use a central helper. **Lesson:** If logic is written twice, it will break twice.
* **Assuming I/O succeeds:** I assumed `json.loads` and `file.write` would always work if the file existed. **Lesson:** The Operating System can revoke permissions, fill up the disk, or corrupt files at any microsecond.
* **Not using dictionaries for lookups:** Relying on list comprehensions `next((x for x in list if x.id == id))` inside `for` loops scaled terribly. **Lesson:** Learn time complexity ($Big O$) and apply appropriate data structures.

---

## What This Project Taught Me About Software Engineering

**Engineering Mindset Evolution:**
* **At the start:** The focus was entirely on feature building—just getting the "happy path" code to execute and print the correct result.
* **At the end:** The focus shifted entirely to reliability, integrity, validation, rollback safety, and corruption resistance. Writing the feature became only 20% of the job; protecting it became the other 80%.

Building this project rewired my brain from "just making it work" to **"engineering it to survive."** Software engineering differs drastically from simply writing code. Code executes instructions; software engineering guarantees those instructions don't destroy the system when the environment or user behaves unpredictably.

I learned to think defensively:
* "What if the user types NaN?"
* "What if the hard drive unplugs during a save?"
* "What if they delete an account that has 400 past transactions?"

An engineering mindset requires assuming that everything that *can* fail *will* fail, and designing a system that gracefully traps those failures.

---

## Version 1 Project Metrics

Project Statistics:

* Code: ~1,900 lines (single `main.py`)
* Features: 9
* Critical Bugs Fixed: 8 (ACC-001, INC-001, TRN-001, REP-001, DATE-001, DEBT-001, REC-001, ATOM-001)
* Deferred Issues: 1 (DASH-001)
* QA Test Groups: 14
* Stress Test Peak: 50,000 transactions, ~30 MB memory

---

---

## Version 1 Final Engineering Achievements

Over the course of Version 1, the following critical infrastructure was successfully designed and implemented:
* **Corruption recovery:** Safe JSON loaders that gracefully trap syntax errors.
* **Atomic rollback:** Nested exception handling ensuring multi-file saves never partially fail.
* **Validation hardening:** Centralized protection against `nan`, `inf`, and boundary edge-cases.
* **Debt lifecycle management:** Automated status progression tracking complex interpersonal finance.
* **Transfer architecture:** Single-record design preventing double-counting inflation.
* **Category integration:** Soft-delete relational architecture preserving historical integrity.
* **Dashboard aggregation:** Multi-module analytics summarizing the entire state of the application.
* **Performance profiling:** Proven memory stability under 50,000+ record scale tests.

---

## Engineering Principles Learned

1. Validate at multiple layers (input, business rules, relationships).
2. IDs are more stable than names for relational references.
3. Never trust file input — assume all external data is hostile.
4. Financial operations must be atomic across all affected files.
5. Rollback logic is as important as save logic.
6. Single source of truth prevents data inconsistency.
7. Bugs usually hide in edge cases, not in core logic.
8. Correctness before optimization.
9. Test assumptions, not just features.
10. Reliability requires more effort than feature creation.

---

## Final Reflection

1. **What did I do well?** Successfully modeled a multi-layered relational financial system with ironclad rollback safety.
2. **What did I struggle with?** Code organization; the monolithic `main.py` grew unwieldy over time.
3. **What would I do differently?** Build the centralized input validation functions and JSON loaders first, before any features.
4. **Engineering mindset evolution:** Software engineering isn't just about features. The hardest part is protecting those features from invalid input, partial saves, and edge cases.

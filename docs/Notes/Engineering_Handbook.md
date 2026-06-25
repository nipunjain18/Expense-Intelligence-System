# Expense Intelligence System - Version 1.1.0 Engineering Handbook

---

## 1. Executive Summary

**Project Purpose**
The Expense Intelligence System is a terminal-based Personal Finance Management application. It is designed to act as a strict, immutable ledger for all personal financial activity.

**What Problem It Solves**
The system solves the problem of rigorously tracking income, expenses, complex interpersonal debts (borrowing, lending, partial repayments), and inter-account transfers. It ensures that money doesn't simply "disappear" across disparate accounts without a trace, maintaining strict referential integrity.

**Version 1.1.0 Status**
Version 1.1.0 is a Stable, Feature-complete release. The engineering refactoring is completed, establishing a solid foundation for Version 2. It successfully passed comprehensive functional, integration, rollback, and stress testing.

**Major Capabilities**
- Multi-account balance tracking
- Granular categorization of cash flow
- Strict transfer auditing
- Automated debt lifecycle management (LENT/BORROWED/ACTIVE/CLOSED)
- Atomic file operations preventing data corruption
- Centralized read-only aggregation dashboard

**Key Achievements**
- Identifier-based file architecture using purely JSON arrays.
- Implemented robust `copy.deepcopy()` rollback mechanisms ensuring atomic-like multi-file writes.
- Discovered and mitigated deep language-level flaws (e.g., `float("nan")` vulnerabilities) via hardened validation systems.

---

## 2. System Overview

The system operates as a unified financial ledger composed of seven interlinked modules.

**Accounts:** The physical containers for funds. They act as the absolute source of truth for the current state ("How much money do I have right now?").
**Categories:** Analytical metadata tags (e.g., "Food", "Salary") that group financial events for reporting.
**Transactions:** Immutable event records that explain *how* and *why* an Account's balance changed.
**Transfers:** Lateral movement logic that shifts money between two Accounts without affecting Net Cash Flow analytics.
**Debts:** A shadow ledger for interpersonal IOUs that piggybacks on Transactions to move money while maintaining its own tracking math.
**Repayments:** Fulfillment records linked to a specific Debt that mathematically reverse the original obligation.
**Dashboard:** A read-only analytical engine that aggregates data across all modules into human-readable insights.

### High-Level Architecture Explanation
The application uses a **Function-Based Architecture** operating on shared lists of dictionaries. When an event occurs (e.g., an Expense), the system loads the necessary state (Accounts, Transactions) into memory, validates the mutation, updates the data structures, and then triggers an atomic save. 

**Relationships Flow:**
- Standard: `Account` $\rightarrow$ `Transaction` $\rightarrow$ `Category`
- Debt: `Account` $\rightarrow$ `Debt` $\rightarrow$ `Repayment` $\rightarrow$ `Transaction`

---

## 3. Data Architecture

The system relies on five independent JSON schemas.

### Accounts Schema (`accounts.json`)
- **Purpose:** Tracks the current liquid state of the user.
- **Fields:** `account_id` (int), `name` (str), `account_type` (str), `balance` (float), `created_at` (str).
- **Relationships:** Referenced by Transactions, Debts, Repayments, and Transfers.
- **Constraints:** Balance $\ge 0$ (unless "Credit Card"). Names must be globally unique.

### Transactions Schema (`transactions.json`)
- **Purpose:** Chronological audit trail of money movement.
- **Fields:** `transaction_id` (int), `account_id` (int), `category_id` (int), `type` (str), `amount` (float), `description` (str), `date` (str).
- **Relationships:** Belongs to 1 Account, Belongs to 1 Category. (Transfers use `from_account_id` and `to_account_id`).
- **Constraints:** Immutable. Must be linked to valid active IDs. Amount $> 0$.

### Categories Schema (`categories.json`)
- **Purpose:** Metadata grouping for analytics.
- **Fields:** `category_id` (int), `name` (str), `type` (str), `is_default` (bool), `is_deleted` (bool).
- **Relationships:** Referenced by Transactions.
- **Constraints:** Names globally unique across all types.

### Debts Schema (`debts.json`)
- **Purpose:** Tracks interpersonal obligations.
- **Fields:** `debt_id` (int), `transaction_id` (int), `account_id` (int), `person_name` (str), `type` (str), `status` (str), `original_amount` (float), `remaining_amount` (float), `purpose`/`notes` (str), `created_date` (str).
- **Relationships:** Belongs to 1 Account. Owns 1 Transaction. Owns many Repayments.
- **Constraints:** `remaining_amount` $\ge 0$. One Debt = One Account strictly.

### Repayments Schema (`repayments.json`)
- **Purpose:** Tracks partial or full fulfillment of Debts.
- **Fields:** `repayment_id` (int), `debt_id` (int), `transaction_id` (int), `account_id` (int), `amount` (float), `date` (str).
- **Relationships:** Belongs to 1 Debt. Belongs to 1 Account. Owns 1 Transaction.
- **Constraints:** Date $\ge$ Debt `created_date`. Amount $\le$ Debt `remaining_amount`.

### Why IDs Instead of Names
The architecture strictly enforces **Identifier-Based Linkage** by using integer IDs (`account_id`, `category_id`, etc.) rather than string names. If a transaction stored the literal string `"Bank"` instead of `account_id: 1`, renaming the account to `"Checking"` would instantly break the linkage for thousands of historical records. Integer IDs decouple the data's identity from its presentation, allowing safe renaming and soft-deletion without cascading data corruption.

---


### Architectural Relationships
- **Account $\rightarrow$ Transaction**
- **Debt $\rightarrow$ Repayment**
- **Category $\rightarrow$ Transaction**

**Focus:** Why the relationship exists. Enforcing referential integrity and ensuring single source of truth.
## 4. Core Engineering Principles

These foundational principles govern the entire codebase and must not be violated during maintenance.

- **Defensive Programming:** Assume all inputs (user typing, file reading, function arguments) are actively trying to break the system. Never trust external state.
- **Validation First:** Data must be proven mathematically, structurally, and logically sound before the application trusts it to update state.
- **Single Source of Truth:** Data is never duplicated. If a transaction belongs to an account, it stores the ID, not the account's current balance or name.
- **Atomic Operations:** Multi-file modifications (like adding a Debt) are singular events. They must completely succeed or completely fail, leaving no partial state on disk.
- **Data Normalization:** Separation of concerns via distinct files (e.g., storing Repayments separately from Debts) rather than nesting massive arrays inside single objects.
- **Referential Integrity:** Enforcing unbreakable links between datasets. A debt cannot be deleted if a repayment references its ID.
- **Soft Delete Strategy:** Hard deletions corrupt historical ledgers. Records (like Categories) use `is_deleted: True` to hide them from UI menus while preserving historical transactions that reference them.
- **Read-Only Operations:** Analytical features (like the Dashboard) must strictly observe state and are forbidden from mutating lists or triggering saves.
- **DRY (Don't Repeat Yourself):** Repeated logic (like checking for sufficient funds or finite numbers) must be abstracted into centralized helper functions (`get_valid_amount`) to prevent localized bugs.
- **Single Responsibility Principle:** Functions do one thing. A function that formats currency does not also calculate the sum.
## 5. Feature Documentation

### Feature 1: Account Management
- **Purpose:** Establish the physical containers for monetary balances.
- **Business Rules:** Names must be globally unique. Initial balance $\ge 0$. Type must be from an explicit list.
- **Key Design Decisions:** ID generation isolates names from downstream transactions, future-proofing the system for account renaming.
- **Known Limitations:** Accounts cannot currently be renamed, soft-deleted, or have their type edited.
- **Future Improvements:** Add soft deletion capabilities for accounts.

### Feature 2: Account Viewing
- **Purpose:** Display active accounts and their current balances.
- **Business Rules:** Display sorted sequentially by `account_id` (creation order). Top-level summary aggregates total account count and total balance.
- **Key Design Decisions:** Separation of display logic from calculation logic ensures UI consistency.
- **Known Limitations:** No pagination or custom sorting (e.g., sort by highest balance).
- **Future Improvements:** Custom sorting parameters.

### Feature 3: Transactions
- **Purpose:** Log immutable events of external cash flow (Income/Expense).
- **Business Rules:** Expenses cannot exceed current balance. Amount must be $> 0$. Date is strictly `today()`. Debt categories are hidden from selection.
- **Key Design Decisions:** `_add_transaction` abstracts both Income and Expense logic to prevent code duplication, using a simple string argument to branch the math (`+` vs `-`).
- **Known Limitations:** Cannot backdate standard transactions (forced `date.today()`).
- **Future Improvements:** Add a historical date prompt.

### Feature 4: Transaction Viewing
- **Purpose:** Provide a unified, chronological history of all cash flow and transfers.
- **Business Rules:** Sorted by date (descending) then ID. Invalid records are skipped silently to prevent crashes. Soft-deleted categories render with a "(Deleted)" suffix.
- **Key Design Decisions:** Read-time validation (`validate_transaction()`) ensures manual JSON edits do not crash the application.
- **Known Limitations:** Resolving names requires full list iterations ($O(N)$), causing UI lag at scale.
- **Future Improvements:** Implement dictionary hash maps for $O(1)$ lookups.

### Feature 5: Category Management
- **Purpose:** Provide analytical metadata structuring for transactions.
- **Business Rules:** Globally unique names across all types. Default system categories cannot be renamed or deleted. Re-creating a deleted category automatically restores the original.
- **Key Design Decisions:** Enforcing global uniqueness (instead of type-based uniqueness) ensures AI/Analytics can group data purely by name without NLP confusion.
- **Known Limitations:** Type (Income/Expense) cannot be changed after creation.
- **Future Improvements:** Category-specific budgeting.

### Feature 6: Category Integration
- **Purpose:** Connect categories with transactions reliably.
- **Business Rules:** Transaction cannot be created without a category. Category type must match transaction type. Only active categories can be selected.
- **Key Design Decisions:** Normalizing data by storing only the `category_id` prevents cascading update issues when a user renames a category.

### Feature 7: Debt Tracking
- **Purpose:** Track interpersonal IOUs independently of cash flow totals.
- **Business Rules:** One Debt = One Account. Repayment $\le$ Remaining Amount. Deletion blocked if repayments exist. Overpayments truncate to remaining.
- **Key Design Decisions:** Explicitly isolating debt categories (`Debt Lent`, etc.) from standard user selection prevents users from polluting normal financial logging with shadow ledger events.
- **Known Limitations:** A single debt cannot span multiple funding accounts.
- **Future Improvements:** Allow debt renaming or editing.

### Feature 8: Dashboard
- **Purpose:** Financial overview and aggregation.
- **Business Rules:** Excludes "Transfer" type transactions from Income/Expense cash flow summaries.
- **Key Design Decisions:** Completely decoupled calculation logic from display logic for high testability.
- **Known Limitations:** Severely unoptimized list traversals repeat over the same lists multiple times.
- **Future Improvements:** Implement a single-pass analytics engine that computes all aggregates simultaneously.

### Feature 9: Transfers
- **Purpose:** Lateral movement of funds without affecting net worth.
- **Business Rules:** Source $\ne$ Destination. Amount $\le$ Balance (unless Credit Card). Deletion blocked if it causes destination to go negative.
- **Key Design Decisions:** Stored as a *single* transaction record rather than paired Income/Expense records, completely isolating it from cash flow analytics.
- **Known Limitations:** Only affects 2 accounts (no multi-way splits).
- **Future Improvements:** Add transfer fee capabilities (e.g., bank charges).
## 6. Validation Architecture

Validation is the security checkpoint of the software. A value can be technically valid (e.g., a number) while still violating business rules (e.g., a number greater than the balance). 

**Evolution to Centralized Validation:**
Initially, features implemented their own inline `while True` validation loops. This scattered logic led to inconsistencies (e.g., Bug TRN-001 where transfers lacked float protection). The architecture was refactored to use centralized helpers (`get_valid_amount`, `get_valid_date`, `validate_transaction`), guaranteeing absolute uniformity across the system.

- **Input Validation:** Trapping `ValueError` for empty strings or letters entered in numeric fields.
- **Amount Validation:** Ensuring amounts are strictly $> 0$.
- **NaN / Infinity Protection:** Python's `float("nan")` bypasses normal maximum value checks (`nan > 5000` is `False`). Using `math.isfinite()` became an absolute mandate for all mathematical inputs.
- **Date Validation:** Ensuring ISO-8601 formatting and enforcing maximum bounds (`date <= today`).
- **Cross-Record Validation:** Enforcing causality, such as ensuring a repayment date is $\ge$ the debt's creation date.
- **Business Rule Validation:** Enforcing domain physics, such as preventing negative balances or stopping source and destination accounts from matching during a transfer.

**Key Lesson:** You cannot validate only against what you *expect* a user to do; you must validate against the deep technological limitations of the language itself.

---


### Business Rule Walkthroughs

The code is full of rules. Let's explain why the rules exist.

### Rule: Expense cannot exceed balance.
- **Why?** Imagine your Wallet has ₹1,000. You log an expense of ₹2,000. Your Wallet balance becomes -₹1,000. You cannot physically have a negative wallet. The ledger no longer reflects reality, destroying trust in the system.
- **Function Enforcing Rule:** `get_valid_amount()` / `_add_transaction()`

### Rule: Repayment Date $\ge$ Debt Date
- **Why?** Imagine you lent money on Jan 5th. You log a repayment for Jan 1st. You just bent time. This destroys chronological sorting and creates impossible financial states.
- **Function Enforcing Rule:** `add_repayment()`

### Rule: Overpayments truncate to remaining amount.
- **Why?** A debt is ₹500. A friend hands you ₹600. If the system accepts ₹600, the debt remaining becomes -₹100. Does that mean you now owe them? To prevent complex liability loops, the system caps the repayment at ₹500 and assumes you kept the ₹100 as a gift.
- **Function Enforcing Rule:** `add_repayment()`

### Rule: Cannot delete an account.
- **Why?** If you delete an account, but leave 500 transactions pointing to `account_id: 1`, those transactions are now orphaned. When the Dashboard tries to find the name of Account 1, the program crashes.
- **Function Enforcing Rule:** Missing by design. (There is no `delete_account()` function).

### Rule: Amounts must be `math.isfinite()`.
- **Why?** Python allows the string `"nan"` to become a float `Not-A-Number`. `nan` bypasses all `<` or `>` mathematical checks. If you enter `nan` as an expense, the account balance becomes `nan`. The entire database is instantly corrupted permanently.
- **Function Enforcing Rule:** `get_valid_amount()`

---

## 7. Storage & Persistence Architecture

The system uses a completely offline, zero-database architecture relying on raw JSON arrays.

**Directory Auto-Creation:**
On boot, the system checks for the `data/` directory and creates it if it doesn't exist, ensuring `FileNotFound` errors do not occur on first run.

**The `load_json_file()` Guardian:**
Instead of blindly calling `json.loads()`, all file reads pass through `load_json_file()`. This centralized wrapper assumes files are hostile. It gracefully traps `json.JSONDecodeError` (if a file was manually corrupted) and `OSError` (disk permission issues), returning an empty `[]` instead of allowing a fatal system crash.

**Save Wrappers:**
Functions like `save_accounts()` wrap `json.dump` with `indent=4` to enforce human-readable formatting, making manual file inspection trivial.

**File Safety Strategy:**
There is no concurrent file locking. The application relies entirely on single-threaded linear execution and atomic write sequences to maintain state.

---

## 8. Atomic Rollback Architecture

### Why Rollback Exists
When a user adds a Repayment, the application modifies `repayments.json`, `debts.json`, `transactions.json`, and `accounts.json`. If the application crashes halfway through saving these four files (e.g., disk full), the database enters a permanently corrupted "partial" state.

### How Rollback Works
The system achieves atomicity without a SQL engine by using Python's `copy.deepcopy()`.
Before any data is modified, deep copies of the current JSON arrays are stored in memory. The application mutates the active lists and attempts to save all files inside a `try` block. If any `Exception` occurs during the save sequence, the `except` block immediately overwrites the active lists with the pristine deep copies and triggers a secondary "rescue" save.

### The ATOM-001 Lesson
A rollback is still an I/O operation. If the first save fails due to an `OSError`, the rollback save will likely fail for the exact same reason. The rollback sequence itself must be protected by a nested `try...except` block to prevent the rollback mechanism from causing a cascading unhandled crash.

### Rollback Limitations & Future Database Advantages
While `copy.deepcopy()` is highly effective for Version 1, it requires duplicating massive lists in RAM. At scale, this spikes memory usage. Furthermore, it cannot protect against abrupt hardware power loss occurring exactly during the file write stream. A true SQLite or PostgreSQL database utilizing Write-Ahead Logging (WAL) and native `BEGIN TRANSACTION` / `COMMIT` architecture is the superior long-term solution.

---

## 9. Bug History & Engineering Lessons

| Bug ID | Root Cause | Fix | Engineering Lesson |
| :--- | :--- | :--- | :--- |
| **ACC-001** | Account creation logic did not check if initial balance was $< 0$. | Added strict $\ge 0$ loops to the prompt. | Always validate initial state, not just ongoing mutations. |
| **INC-001** | Python's `float()` accepted `"nan"`, bypassing conditional checks. | Centralized validation using `math.isfinite()`. | Never trust native type casting. Understand language-level quirks. |
| **TRN-001** | `transfer_money` implemented its own fragile validation loop. | Rerouted to use centralized helper. | Don't Repeat Yourself (DRY). Inline logic breeds vulnerabilities. |
| **REP-001** | `add_repayment` did manual `nan` vulnerable checks on overpayments. | Enforced `math.isfinite()` and bounds checks. | Every entry point that touches the ledger must be guarded identically. |
| **REC-001** | `json.loads()` was called without a `try-except` wrapper. | Wrapped all loaders in a centralized exception handler. | External states (files, networks) are volatile and untrustworthy. |
| **ATOM-001**| The rollback block failed to catch exceptions if the rollback save failed. | Added a nested `try...except` inside the rollback. | Error handling code must itself be fault-tolerant. |
| **DATE-001**| Future dates were accepted, corrupting the financial timeline. | Future date validation blocked inputs $> today$. | Valid data format does not mean valid business data. |
| **DEBT-001**| Repayment date could occur before debt creation date. | Minimum date validation referencing debt creation. | Cross-record causal validation is critical. |

### Code Evolution Stories

Understanding *why* the code looks like this is crucial. It didn't start this way.

### The `float("nan")` Bug (INC-001)
**Initial Implementation:** `amount = float(input())`. Checked if `amount > 0`.
**Problems Found:** Python accepts the literal string `"nan"` as a valid float. 
**Bug Discovery:** A user typed "nan". `nan > 0` returns False, but loops didn't trap it properly in some places. The Account Balance became `nan`. 
**Fixes Added:** `math.isfinite(amount)` became mandatory.
**Lessons Learned:** The language itself can be hostile. You must validate against language specifications, not just user logic.

### The Deepcopy Rollback (ATOM-001)
**Initial Implementation:** Modify `accounts` list. Modify `transactions` list. Save both.
**Problems Found:** If `save_transactions()` succeeded, but `save_accounts()` crashed (e.g. disk full), the transaction was recorded but the money never left the account.
**Bug Discovery:** Deliberately crashing the app mid-save left corrupted JSON arrays.
**Fixes Added:** The system now copies the entire list into memory via `copy.deepcopy()` before touching it. If the `try` block fails, it forces the lists back to the deepcopy and does a rescue save.
**Final Design:** A nested `try...except` block because the rollback save itself could fail for the same OS reasons.

### Centralized Validation (TRN-001)
**Initial Implementation:** `_add_transaction` had a `while True` loop to check amounts. `transfer_money` had its own `while True` loop to check amounts.
**Problems Found:** When `nan` protection was added to `_add_transaction`, we forgot to add it to `transfer_money`.
**Bug Discovery:** Transfers crashed the system with `nan`.
**Fixes Added:** All math input loops were deleted and replaced with a single call to `get_valid_amount()`.
**Lessons Learned:** Code duplication is a security risk.

---

## 10. Testing & Quality Assurance

### Testing Strategy
QA was executed progressively across 14 Test Groups, isolating modules before attempting complex cross-module mutations.

- **Functional Testing:** Verifying the "happy path" (e.g., adding an expense deducts money).
- **Integration Testing:** Verifying cross-file flows (e.g., deleting a transfer correctly restores two different accounts and deletes the transaction).
- **Corruption Testing:** Manually destroying JSON file syntax and verifying the app boots safely and skips the unreadable files.
- **Rollback Testing:** Forcefully raising exceptions mid-save to verify deepcopy restoration logic.
- **Stress & Performance Testing:** Throwing extreme datasets at the architecture to find Big-O algorithmic limits.

### Performance Findings
- **Largest Dataset Tested:** 1,000 Accounts, 50,000 Transactions, 2,000 Debts, 5,000 Repayments.
- **Peak Memory Usage:** ~30 MB (Proving Python's RAM efficiency is excellent).
- **Bottlenecks:** Significant UI freezing occurred during `view_transactions()` and `show_dashboard()`. The root cause was identified as $O(N)$ list traversals inside `get_category_name()` and $O(N^2)$ loops in aggregation logic.

**Testing Lesson:** The highest-risk bugs do not live in calculation logic; they live at system boundaries (future dates, missing files, language quirks). Testing early and aggressively breaking inputs is mandatory.

---

## 11. Major Architecture Decisions

### Soft Delete Architecture
- **Decision:** Use `is_deleted: True` instead of hard file deletion.
- **Alternatives Considered:** Deleting the record entirely.
- **Reasoning:** Hard deletes break foreign key integrity, destroying historical transaction rendering.
- **Benefits:** Immutability is preserved.
- **Tradeoffs:** JSON files grow infinitely, never reducing in size.

### Relational ID Architecture
- **Decision:** Store `account_id` instead of `"Bank Name"`.
- **Reasoning:** Names change; IDs do not. Prevents cascading update failures.
- **Benefits:** Single source of truth.

### Debt Lifecycle Architecture
- **Decision:** Debt status (`ACTIVE`/`CLOSED`) is dynamically derived, not manually toggled.
- **Reasoning:** Prevents users from archiving debts with remaining balances.
- **Benefits:** Mathematical certainty overrides user error.

### Debt Category Architecture
- **Decision:** System-generated Debt categories are hidden from standard manual selection.
- **Reasoning:** Prevents users from polluting normal cash flow data with shadow-ledger events.

### Transfer Architecture
- **Decision:** Stored as one single `"Transfer"` record instead of a paired Income/Expense.
- **Reasoning:** Prevents dashboard aggregators from accidentally counting lateral movement as true cash flow.

### Rollback Architecture
- **Decision:** `copy.deepcopy()` memory snapshots.
- **Alternatives Considered:** File backups (`.bak`).
- **Reasoning:** RAM copies are instantaneous and bypass disk I/O permission complexities.

---

## 12. Refactoring Retrospective (Version 1.1.0)

### What Problems Existed Before Refactoring
- **Monolithic `main.py`:** A massive 1,900-line file caused cognitive overload.
- **Duplicate Logic:** Many features manually implemented their own validation and rollback logic.
- **Tangled Responsibilities:** Saving logic, input validation, and business rules were heavily intertwined inside feature functions.

### What Improvements Version 1.1.0 Introduced
- **Helper Extraction:** Massively reduced code duplication by extracting reusable helpers for data lookups and validation.
- **Centralized Rollback:** Introduced `_atomic_save()` to handle all multi-file rollbacks, guaranteeing absolute uniformity across the system.
- **Separation of Responsibilities:** Cleaned up the function dependencies, significantly improving code maintainability.

### What Limitations & Technical Debt Remain
- **Single File:** The application is still largely contained within a single `main.py` file, though much cleaner.
- **File Limits:** Relying on JSON arrays means loading the entire dataset into RAM, which will eventually hit performance bottlenecks at extreme scales.
- **Lookup Inefficiencies:** Resolving relationships still relies heavily on $O(N)$ list iterations.

---

## 13. Critical Functions Overview

### `add_repayment()`
**Risk Level:** Critical
**Files Touched:** accounts.json, debts.json, repayments.json, transactions.json
**Reason It Is Important:** Most complex multi-file workflow.
**Potential Refactoring Risks:** Data inconsistency if rollback fails.

### `_add_transaction()`
**Risk Level:** High
**Files Touched:** accounts.json, transactions.json
**Reason It Is Important:** Primary mutation engine for cash flow.
**Potential Refactoring Risks:** Validation bypass could corrupt core balances.

### `transfer_money()`
**Risk Level:** High
**Files Touched:** accounts.json, transactions.json
**Reason It Is Important:** Simultaneous dual-account mutation.
**Potential Refactoring Risks:** Saving the transaction but failing to update the second account.

### `add_debt()`
**Risk Level:** High
**Files Touched:** accounts.json, debts.json, transactions.json
**Reason It Is Important:** Generates transactions dynamically.
**Potential Refactoring Risks:** Transactions mapped to wrong accounts.

## 14. Change Impact Guide

If you decide to refactor this code, you need to know what will explode.

### If I change: Account Structure (e.g. rename `balance` to `funds`)
- **Affected Functions:** Every single function that moves money.
- **Affected Features:** Everything.
- **Affected JSON Files:** `accounts.json`.
- **Risk Level:** CRITICAL.
- **Required Testing:** Full system QA.
- **Potential Regressions:** Any missed `account["balance"]` reference will crash the app instantly with a `KeyError`.

### If I change: Transaction Structure (e.g. rename `type` to `category_type`)
- **Affected Functions:** `validate_transaction()`, Dashboard calculators.
- **Affected Features:** Viewing, Dashboard, Analytics.
- **Affected JSON Files:** `transactions.json`.
- **Risk Level:** HIGH.
- **Required Testing:** `view_transactions()` must survive.
- **Potential Regressions:** `validate_transaction()` might reject all historical data.

### If I change: Category Structure
- **Affected Functions:** `get_category_name()`.
- **Affected JSON Files:** `categories.json`.
- **Risk Level:** MEDIUM.
- **Required Testing:** UI rendering.

### If I change: Debt Structure
- **Affected Functions:** `add_repayment()`, Dashboard summaries.
- **Affected JSON Files:** `debts.json`.
- **Risk Level:** MEDIUM.
- **Potential Regressions:** `remaining_amount` truncation logic might fail.

### If I change: Repayment Structure
- **Affected Functions:** `delete_repayment()`.
- **Affected JSON Files:** `repayments.json`.
- **Risk Level:** MEDIUM.

### If I change: Transfer Logic
- **Affected Functions:** `validate_transaction()`.
- **Affected Features:** Transfers, Dashboard.
- **Risk Level:** HIGH.
- **Potential Regressions:** Transfers accidentally getting summed up as Income/Expense.

---

## 15. Version 2 Roadmap

**1. Modular Architecture (High Priority)**
- Split the refactored `main.py` into distinct modules (`storage.py`, `models/`, `views/`, and `utils.py`).

**2. Database-Backed Persistence (High Priority)**
- Migrate from JSON arrays to a relational database (e.g., SQLite/PostgreSQL) to natively handle constraints, WAL atomicity, and memory limits.

**3. Automated Testing (Medium Priority)**
- Implement automated test suites to replace the 14 manual QA groups, protecting against future regressions.

**4. Web Application Interface (Medium Priority)**
- Build a web-based UI to replace the CLI, improving user experience and accessibility.

**5. Logging & Analytics (Low Priority)**
- Add an `application.log` file to record critical backend events.
- Implement advanced analytics and AI-assisted financial insights.

---

## 16. Project Metrics

- **Code Size:** Significantly condensed single `main.py` script after extensive helper extraction
- **Total Features:** 9 Core Modules
- **Data Persistence:** 5 distinct JSON schemas
- **Critical Bug Fixes Executed:** 8 Core architecture flaws mitigated
- **QA Test Groups Executed:** 14 structured phases
- **Stress Testing Peak:** Handled 50,000 transactions simultaneously
- **Release:** Version 1.1.0 (Stable)


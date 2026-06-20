# Expense Intelligence System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Version](https://img.shields.io/badge/Version-1.0.0-success)
![Storage](https://img.shields.io/badge/Storage-JSON-orange)
![Testing](https://img.shields.io/badge/QA-14%20Test%20Groups-brightgreen)
![Status](https://img.shields.io/badge/Status-Stable-success)

A production-focused Python CLI personal finance system featuring relational JSON storage, rollback-protected transactions, corruption recovery, and extensive QA testing.

The Expense Intelligence System is a terminal-based personal finance management application built in Python. It goes beyond basic CRUD operations by enforcing financial business rules, maintaining relational integrity across JSON data stores, and implementing rollback-protected multi-file transactions without a traditional database.

## Current Status

**Version:** 1.0.0

**Status:** Stable Release

## Version 1 Highlights

- 9 core financial modules completed
- 14 structured QA test groups completed
- 8 critical bugs discovered and fixed
- Rollback-protected multi-file transactions
- Corruption recovery system
- Stress tested with 50,000 transactions

## Tech Stack

- Python
- JSON Storage
- Git
- GitHub

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Technical Highlights](#technical-highlights)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Testing Summary](#testing-summary)
- [Critical Bugs Fixed](#critical-bugs-fixed)
- [Performance](#performance)
- [Lessons Learned](#lessons-learned)
- [Skills Demonstrated](#skills-demonstrated)
- [Version 2 Roadmap](#version-2-roadmap)

---

## Overview
This system was built to explore software engineering resilience by constructing a strict financial ledger from scratch. It is an exploration of how to make software survive hostile edge cases, corrupted states, and persistence failures using atomic constraints and rigid validation logic.

## Why This Project Matters

While most personal finance projects stop at basic CRUD operations, this project was designed specifically to tackle core software engineering concerns. It focuses heavily on relational data modeling, rollback-protected transactions, corruption recovery, and defensive validation. The primary goal was not just to build a feature-complete application, but to construct a highly resilient system that guarantees referential integrity and survives hostile environments, validated by 14 structured QA test groups.

---

## Key Features

| Feature | Description |
| ------- | ----------- |
| **Multi-Account Management** | Manage Cash, Bank, UPI, Investment, and Credit Card accounts. |
| **Income & Expense Tracking** | Record strictly validated financial flows. |
| **Category Management** | Define, rename, and soft-delete transaction categories. |
| **Category Integration** | Maintain relational ties between transactions and historical categories. |
| **Money Transfers** | Safely move money between internal accounts without inflating income/expense totals. |
| **Debt Tracking** | Manage "Money Lent" and "Money Borrowed" with automated balance synchronization. |
| **Repayment Tracking** | Link transactional settlements directly to outstanding debts. |
| **Debt Deletion** | Safely reverse historical debts and their linked transactions. |
| **Repayment Deletion** | Restore debt balances and reverse account transactions safely. |
| **Financial Dashboard** | A unified, read-only aggregation of the user's total net worth and activity. |
| **JSON Persistence** | Lightweight, robust local data storage simulating a database. |
| **Soft Delete Architecture** | Ensures historical transactions never lose their categorical identity. |
| **Rollback Protection** | Multi-file operations are atomic and memory-safe. |
| **Corruption Recovery** | Gracefully handles missing, empty, or malformed data files. |

---

## Technical Highlights

* **Python CLI Application:** Built with zero external dependencies.
* **JSON Database Architecture:** Emulates relational database tables using discrete flat files.
* **Relational Data Modeling:** Uses integer IDs as foreign keys to maintain referential integrity.
* **Atomic Transactions:** Implements rollback-protected multi-file transactions using `copy.deepcopy()`.
* **Validation Layers:** Centralized type, boundary, and business logic validation.
* **Corruption Recovery:** Centralized I/O wrappers trap `JSONDecodeError` to prevent fatal crashes.
* **Single Source of Truth:** Eliminates duplicated state to ensure metrics never desynchronize.

---

## Architecture

The system uses a highly normalized JSON storage schema representing distinct domains, connected via auto-generated IDs (`account_id`, `category_id`, `debt_id`, `transaction_id`).

```text
Accounts
    │
    ▼
Transactions ─────► Categories
    │
    ▼
Debts
    │
    ▼
Repayments
```

The relationships are fundamentally hierarchical: Accounts own Transactions. Transactions are tagged by Categories. Debts are funded by Accounts and managed independently, and Repayments settle Debts by creating corresponding Transactions.

* `accounts.json`: Maintains current state (liquid balances).
* `transactions.json`: An immutable ledger of events.
* `categories.json`: A unified taxonomy enforcing global uniqueness.
* `debts.json`: Tracks active and closed interpersonal liabilities.
* `repayments.json`: The bridge between a debt and its corresponding transactional settlement.

---

## Project Structure

```text
Expense-Intelligence-System/
├── main.py                     # Core application entry point
├── README.md                   # Project overview
├── data/
│   ├── accounts.json           # Account balances and metadata
│   ├── categories.json         # Taxonomy mapping
│   ├── debts.json              # Active and closed liabilities
│   ├── repayments.json         # Debt settlement logs
│   └── transactions.json       # Immutable financial ledger
└── docs/
    ├── learning_notes.md          # Engineering lessons and architecture insights
    └── project_documentation.md   # System workflows and schema definitions
```

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/nipunjain18/Expense-Intelligence-System.git

# Navigate to the directory
cd Expense-Intelligence-System

# Run the application (No external dependencies required)
python main.py
```

---

## Testing Summary

The application was subjected to rigorous QA simulating extreme environments across 14 test groups.

| Category            | Status |
| ------------------- | ------ |
| Functional Testing  | ✅      |
| Integration Testing | ✅      |
| Corruption Testing  | ✅      |
| Rollback Testing    | ✅      |
| Performance Testing | ✅      |

---

## Version 1 Statistics

| Metric | Value |
|----------|----------|
| Core Features | 9 |
| QA Test Groups | 14 |
| Critical Bugs Fixed | 8 |
| Data Files | 5 |
| Stress Test Transactions | 50,000 |
| Peak Memory Usage | ~30 MB |

---

## Critical Bugs Fixed

| Bug ID | Description | Fix Implemented |
| ------ | ----------- | --------------- |
| **ACC-001** | Negative balance validation gaps. | Enforced strict domain constraints at data entry. |
| **INC-001** | Bypassing validation via `float("nan")` and `float("inf")`. | Centralized `math.isfinite()` defense mechanism. |
| **TRN-001** | Duplicated validation logic breeding inconsistencies. | Consolidated into unified helper functions. |
| **REP-001** | Unhandled overpayment boundaries. | Truncation prompts and strict math boundaries. |
| **REC-001** | Fatal crashes caused by manual JSON syntax errors. | Defensive I/O wrapping `JSONDecodeError`. |
| **ATOM-001** | Cascading failures during rollback I/O attempts. | Nested `try/except` fallback blocks. |
| **DATE-001** | Chronological corruption from future-dated inputs. | Temporal validation blocking future inputs. |
| **DEBT-001** | Repayment dates preceding debt creation dates. | Relational validation against parent debt. |

---

## Performance

The system's JSON processing capabilities were heavily stress-tested using artificially generated large-scale datasets. Python easily handled the in-memory load.

| Metric | Result |
| ------ | ------ |
| Accounts | 1,000 |
| Transactions | 50,000 |
| Debts | 2,000 |
| Repayments | 5,000 |
| Peak Memory | ~30 MB |

*Insight:* UI rendering loops highlighted critical `O(n²)` algorithmic bottlenecks when cross-referencing names by ID across 50,000 records, providing a clear optimization roadmap.

---

## Lessons Learned

* **Validation:** Input validity is not business validity. Defensive programming means actively protecting the math from hostile inputs.
* **Rollbacks:** Saving data to three files isn't three distinct actions—it's one atomic transaction. True rollback requires deep copying.
* **Data Modeling:** Using immutable IDs instead of names prevents catastrophic cascading updates during renaming operations.
* **Corruption Recovery:** Never trust file I/O. Assuming a file is syntactically sound is a recipe for startup crashes.
* **Testing:** The most critical bugs hide at system boundaries (future dates, identical source/destinations, zero boundaries), not in the core calculation logic.

---

## Skills Demonstrated

- Python Programming
- Data Modeling
- File-Based Persistence
- Defensive Programming
- Input Validation
- Error Handling
- Atomic Transactions
- Rollback Mechanisms
- Software Testing
- Performance Analysis
- Software Documentation
- Git & GitHub

---

## Version 2 Roadmap

- [ ] Web-based application
- [ ] Authentication and user accounts
- [ ] Interactive dashboard
- [ ] Charts and visual analytics
- [ ] Report export functionality
- [ ] AI-powered financial insights
- [ ] Improved architecture and modularization



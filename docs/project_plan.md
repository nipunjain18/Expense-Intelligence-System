# Expense Intelligence System — Project Plan

## Project Overview

This document serves as the central planning and scoping reference for the Expense Intelligence System. It outlines the project goals, current status, development methodology, architecture overview, testing strategy, version history, and future roadmap.

## Contents

- [Project Goal](#project-goal)
- [Current Project Status](#current-project-status)
- [Version History](#version-history)
- [Development Methodology](#development-methodology)
- [Version 1 Features](#version-1-features)
- [Testing Strategy](#testing-strategy)
- [Architecture Overview](#architecture-overview)
- [Design Principles](#design-principles)
- [Version 2 Roadmap](#version-2-roadmap)

---

## Project Goal

The Expense Intelligence System is a terminal-based personal finance application designed to enforce strict financial business rules and maintain data relationships without relying on a traditional database engine. 

Its primary purpose is to safely and accurately record financial events—such as incomes, expenses, debts, and transfers—ensuring that the underlying math is robust and protected from corruption or invalid states.

The project was created to learn and apply core software engineering concepts in a practical environment. These concepts include defensive programming, data modeling with JSON, rollback mechanisms, project architecture, and disciplined development workflows.

---

## Current Project Status

* **Version 1 is feature-complete and stable.**
* The core financial management functionality has been completed and tested.
* Future updates to the Version 1 branch are expected to be limited strictly to bug fixes and routine maintenance. 
* New functionality and architectural shifts will be introduced in Version 2.

---

## Version History

### Version 1.0.0
* Initial stable release containing all core financial modules and CLI interfaces.

### Version 1.1.0
* Internal engineering refactoring.
* Improved maintainability and reduced code duplication.
* No feature additions or business logic changes.

---

## Development Methodology

To ensure stability and logical progression, the project utilizes a strict, iterative development workflow. Every feature in Version 1 followed this exact lifecycle:

1. **Business Rules:** Defined strict constraints and financial validity limits.
2. **Design:** Planned data structures and validation boundaries.
3. **Implementation:** Wrote resilient Python code, applying rollback mechanisms where multi-file writes were required.
4. **Testing:** Validated against edge cases and system boundaries.
5. **Documentation:** Documented the feature logic and engineering decisions.
6. **Git Commit:** Saved the stable, verified milestone.

---

## Version 1 Features

Version 1 includes a comprehensive suite of financial management capabilities:

* **Accounts:** Management of Cash, Bank, Credit, and Investment accounts using integer identifiers.
* **Transactions:** Validation and tracking of income and expense records.
* **Categories:** Taxonomy management with soft-delete capabilities to preserve historical data.
* **Category Integration:** Categories linked to transactions using stable identifiers to preserve historical records even if a category is deleted.
* **Transfers:** Value movement between internal accounts that correctly updates balances without inflating total income or expense metrics.
* **Debt Tracking:** Complete lifecycle management for lent and borrowed money, ensuring debts are linked to corresponding settlement transactions (repayments).
* **Dashboard:** Unified read-only analytics displaying aggregated net worth and transaction history calculated directly from the underlying data files.

---

## Testing Strategy

Version 1 was validated through rigorous, continuous testing focused on system resilience and data integrity. The strategy included:

* Feature testing
* Regression testing
* Manual CLI testing
* Edge-case validation
* Financial integrity verification

---

## Architecture Overview

The Version 1 system prioritizes simplicity and robust data handling through a **Function-Based Architecture**:

* **Language:** Python
* **Interface:** Terminal-based CLI Application
* **Storage:** JSON storage with relationships maintained using unique identifiers.
* **State Management:** File-based persistence featuring rollback mechanisms applied to multi-file operations to preserve data consistency upon failure.

*Note: Version 2 is expected to introduce a modular architecture, further decoupling the application layers.*

---

## Design Principles

The engineering philosophy used throughout Version 1 development relies on several core principles:

* **Constraint-driven development:** Defining financial rules and boundaries before writing implementation logic.
* **Data integrity before convenience:** Enforcing strict constraints at the application boundary to protect the data layer.
* **Incremental feature development:** Building and verifying one isolated feature at a time.
* **Maintainability over premature optimization:** Prioritizing readable, easily debuggable code over complex performance optimizations.
* **Documentation alongside implementation:** Recording architectural decisions and engineering notes concurrently with code changes.
* **Behavior preservation during refactoring:** Improving the structural integrity of the code without altering established functionality.

---

## Version 2 Roadmap

Version 2 focuses primarily on architectural evolution and long-term scalability rather than extending Version 1 incrementally. The future development roadmap transitions the project from a local CLI tool to a scalable application.

### Architecture
* Modular project structure
* Better separation of concerns

### Backend
* SQLite/PostgreSQL database migration
* Repository or service layer implementation

### Interface
* Web application interface

### Analytics
* Comprehensive reporting
* Visual charts
* Interactive financial insights

### Future AI
* Natural language transaction entry
* AI-powered spending insights

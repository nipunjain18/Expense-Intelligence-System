# Expense Intelligence System — Project Plan

## Project Overview

This document serves as the central planning and scoping reference for the Expense Intelligence System. It outlines the project goals, development phases, planned features, testing strategy, and future roadmap.

## Contents

- [Project Goal](#project-goal)
- [Development Phases](#development-phases)
- [Version 1 Scope](#version-1-scope)
- [Planned Features](#planned-features)
- [Testing Strategy](#testing-strategy)
- [Data Architecture](#data-architecture)
- [Version 2 Roadmap](#version-2-roadmap)

---

## Project Goal

The project was created to learn and apply:

* Software Development
* Problem Solving
* File Handling
* JSON-Based Data Persistence
* Project Architecture
* Git & GitHub Workflows
* Software Design Principles

---

## Development Phases

The project is intentionally developed feature-by-feature to simulate a real software development lifecycle. Each module is designed, implemented, tested, documented, and committed independently before moving to the next phase.

| Phase   | Module                           |
| ------- | -------------------------------- |
| Phase 1 | Account Management               |
| Phase 2 | Category Management              |
| Phase 3 | Income & Expense Tracking        |
| Phase 4 | Transfer Management              |
| Phase 5 | Debt Tracking                    |
| Phase 6 | Dashboard                        |
| Phase 7 | Testing, Hardening & Refactoring |

The project was designed around a feature-by-feature development approach. Each phase builds upon the previous one, allowing business rules, validation, testing, and documentation to evolve alongside the application.

---

## Version 1 Scope

### System Scope

* Single-user application
* Local JSON storage
* Terminal-based interface

### Planned Modules

Version 1 was planned to include:

- Account Management
- Category Management
- Income Tracking
- Expense Tracking
- Transfer Management
- Debt Tracking
- Repayment Tracking
- Dashboard

---

## Planned Features

### Financial Management

* Multi-account management
* Income tracking
* Expense tracking
* Transfer management

### Debt Management

* Debt creation
* Debt repayment tracking
* Debt deletion
* Repayment deletion

### Data Management

* Category management
* Soft delete architecture
* Relational data modeling

### System Features

* Dashboard analytics
* Corruption recovery
* Rollback protection

---

## Testing Strategy

Testing was planned as a continuous activity throughout development rather than a final phase. Each feature was validated individually before integration into the larger system.

### Areas to Test

- Functional testing
- Integration testing
- Data validation testing
- Corruption recovery testing
- Rollback testing
- Performance testing

---

## Data Architecture

Version 1 uses JSON files as the persistence layer. Each file represents a separate domain within the system and is connected through unique identifiers.

* `accounts.json`
* `categories.json`
* `transactions.json`
* `debts.json`
* `repayments.json`

---

## Future Architecture Direction

Version 1 prioritizes simplicity and learning through a function-based architecture with JSON storage.

Future versions may introduce:

- Database-backed persistence
- Modular application structure
- Authentication and user management
- API-driven architecture
- Web-based user interface

---

## Version 2 Roadmap

### Planned Improvements

- Web Application
- Authentication & User Accounts
- Database Integration
- Interactive Dashboard
- Charts & Analytics
- Report Exporting
- AI-Powered Insights
- Improved Architecture & Modularization

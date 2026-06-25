# Expense Intelligence System - Project History

This document records the evolution of the Expense Intelligence System from its initial idea through Version 1.1.0. It serves as a personal reflection on the major engineering decisions made, the technical challenges encountered, and the software engineering lessons learned along the way.

## Project Goal
I built the Expense Intelligence System as a personal project to learn how to write a complete application from scratch in Python. I wanted to move past solving basic algorithmic problems and actually build something functional that I could use to track my own finances. The main goal was to figure out how software development actually works—handling files, structuring code, using Git, and figuring out how to store data without just dumping everything into a plain text file.

## Initial Scope
At first, the plan was just to build a simple command-line script for a single user. I wanted to use JSON files to save the data locally so I wouldn't have to learn SQL right away. The checklist of features included managing accounts, grouping things by categories, logging income and expenses, tracking money moved between accounts, and keeping a basic record of money I lent to or borrowed from friends. I also wanted a simple text dashboard to show my total balances.

## Development Timeline
I built the project one piece at a time. 

I started with Account Management because I needed somewhere to store money first. Once that was working, I added Category Management so I could tag my transactions. Then I built the actual Income and Expense tracking. This part was tricky because a single transaction had to link to both an account and a category.

After that, I added Transfer Management. It turned out to be harder than I expected because moving money between two accounts shouldn't count as an expense or income, but it still needed to update two different balances at the same time.

Next, I worked on Debt and Repayment Tracking. I had to figure out how to link a repayment back to the original debt so the balance would update correctly. Finally, I built the Dashboard to pull all this data together, and spent the last few weeks testing the app and fixing a lot of bugs I didn't see coming.

What started as a basic script to log expenses quickly evolved into something much more complex. Because I chose to use multiple JSON files to store everything, I realized I had to build my own validation layers, rollback mechanisms, and corruption recovery just to keep the data safe. Linking debts and repayments also forced me to implement identifier-based relationships manually to make sure dates and balances stayed synchronized.

This steady, iterative process eventually culminated in the stable Version 1.0.0 release. Following that, I immediately shifted focus from building features to improving the codebase structure, launching the Version 1.1.0 engineering refactoring phase to clean up the architecture.

## Major Design Decisions
As I kept adding features, I had to make a few important technical decisions:

- **JSON Storage:** I decided to use plain JSON files instead of a database engine. It forced me to learn how to handle file reading and writing manually, which was a great learning exercise.
- **Using IDs Instead of Names:** At first, I used category names to identify transactions. That broke immediately when I tried to rename a category in the app. I ended up switching to integer IDs for everything to maintain stable relationships.
- **Soft Deleting Categories:** I realized if I deleted a category, all past transactions using that category would break because they wouldn't know what they were mapped to anymore. So, I added an `is_deleted` flag instead of actually deleting the data.
- **Rollback Protection:** When making a transfer, if the script updated the first account but crashed before updating the second, the money just disappeared into thin air. I used `copy.deepcopy()` to make changes in memory first, and only saved them to the files if everything was completely successful, mimicking atomic-like behavior for multi-file operations.
- **Separate Repayment Records:** I decided to track repayments separately from regular transactions to keep a clear link to the specific debt they were paying off.
- **Single-User Architecture:** I completely ignored multi-user support and authentication. It was too complicated for Version 1 and I wanted to focus on getting the core math right.

## Problems Encountered
I ran into a lot of issues that taught me how fragile code can be:

- **Validation Problems:** I thought checking if an input was a float was enough. Then I realized Python accepts `float("nan")` and `float("inf")`, which completely broke the math logic.
- **Data Consistency Issues:** In one of my early tests, I accidentally paid back more money than I owed, and the system happily gave me a negative debt balance. I had to add strict boundary checks to stop this.
- **Rollback Challenges:** Sometimes my rollback code would fail while trying to fix a failed save, which crashed the whole app. I had to learn how to use nested try/except blocks properly.
- **Date Validation Issues:** I didn't restrict dates at first, so I could log a transaction for the year 2099. This messed up my chronological sorting.
- **Corrupted JSON Handling:** If I manually opened a JSON file and accidentally deleted a comma, the whole app would crash on startup. I had to write defensive code to catch `JSONDecodeError` and load an empty list instead of crashing.
- **Debt-Repayment Synchronization:** I found a bug where I could log a repayment for a date *before* the debt was even created. I had to add validation to compare dates across different files.

## Testing Process
I spent a lot of time breaking the app to see what would happen. 

I did functional testing to make sure the math worked, and integration testing to make sure transferring money actually updated the accounts and transactions files correctly at the same time. I specifically tested corruption by feeding the app bad JSON files to see if it would survive. I also simulated disk crashes to test my rollback logic. 

In the end, I wrote 14 different manual test groups and found 8 critical bugs. To see if the app would hold up under a lot of data, I wrote a script to dump 50,000 transactions, 2,000 debts, and 5,000 repayments into the JSON files. I really just wanted to see if Python could handle loading that much JSON into memory at once without slowing down the terminal. It turned out it handled it fine, and the core operations stayed reasonably fast even under heavy load.

## The Git Recovery Incident
While developing, I encountered a major version control issue. I attempted an interactive rebase to clean up some messy commits, but I misunderstood how Git handles history and accidentally created a tangled merge history. My working tree became a mess, and I couldn't push my changes. 

I was able to recover the repository by relying on manual backups, utilizing `git reset --hard` to go back to a known good state, and performing a force push. It was a stressful experience, but it taught me a valuable engineering lesson about understanding version control deeply and the importance of having local backups before performing complex Git operations.

## Post-Release Engineering Phase (Version 1.1.0)
After completing Version 1.0.0, I realized that while the application worked perfectly, the codebase had become monolithic and difficult to read. I initiated the Version 1.1.0 refactoring phase with a strict goal: improve maintainability without changing any functionality.

I focused on reducing massive code duplication. I reorganized the code structure, extracted complex logic into reusable helpers, and separated the UI concerns from the business logic. Because I wanted to guarantee that I hadn't broken anything, I performed manual regression testing after every single refactoring phase. This engineering cycle successfully transformed Version 1 into a clean, stable foundation for Version 2.

## Documentation Evolution
As the project grew, so did the documentation. Initially, I just kept a file of "Learning Notes" to jot down things I figured out. As the system became more complex, that single file wasn't enough.

I eventually split the documentation into an Engineering Handbook and a Code Understanding Handbook. This was a crucial step because separating architectural reasoning from implementation explanations made the project much easier to maintain and review.

## Engineering Evolution
Looking back, my software engineering mindset completely changed during this project. When I started, I just wanted to write features quickly. Over time, I learned to design business rules first before writing a single line of code. 

I discovered the absolute importance of maintainability; writing code that works isn't enough—it has to be readable and adaptable. I learned to appreciate refactoring as a core part of development rather than just a cleanup task. Most importantly, I realized that testing and documentation aren't afterthoughts; they are integral parts of the software engineering process.

## Version 1 Snapshot
To give an idea of what was actually built, here is the final state of Version 1.1.0:

- **Current Version:** 1.1.0
- **Technology Stack:** Python Standard Library, JSON Storage
- **Architecture Style:** Function-Based CLI Application
- **Major Modules:** 9
- **Testing Coverage:** 14 QA test groups
- **Stress Testing Summary:** Successfully processed 50,000 transactions while maintaining fast core operations

## Future Direction
The next phase of the project focuses primarily on architectural evolution rather than incremental feature additions. 

With Version 1 serving as a highly stable foundation, my long-term goals include migrating to a modular architecture and replacing the file-based JSON storage with database-backed persistence. Once the backend is robust and scalable, I eventually hope to build a web application interface, improve testing methodologies, introduce analytics, and explore AI-assisted financial features. These represent the future vision for the system as it continues to grow.

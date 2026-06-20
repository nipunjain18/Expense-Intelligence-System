# Expense Intelligence System - Project History

## Project Goal
I built the Expense Intelligence System as a personal project to learn how to write a complete application from scratch in Python. I wanted to move past solving basic algorithmic problems and actually build something functional that I could use to track my own finances. The main goal was to figure out how software development actually works—handling files, structuring code, using Git, and figuring out how to store data without just dumping everything into a plain text file.

## Initial Scope
At first, the plan was just to build a simple command-line script for a single user. I wanted to use JSON files to save the data locally so I wouldn't have to learn SQL right away. The checklist of features included managing accounts, grouping things by categories, logging income and expenses, tracking money moved between accounts, and keeping a basic record of money I lent to or borrowed from friends. I also wanted a simple text dashboard to show my total balances.

## Development Timeline
I built the project one piece at a time. 

I started with Account Management because I needed somewhere to store money first. Once that was working, I added Category Management so I could tag my transactions. Then I built the actual Income and Expense tracking. This part was tricky because a single transaction had to link to both an account and a category.

After that, I added Transfer Management. It turned out to be harder than I expected because moving money between two accounts shouldn't count as an expense or income, but it still needed to update two different balances at the same time.

Next, I worked on Debt and Repayment Tracking. I had to figure out how to link a repayment back to the original debt so the balance would update correctly. Finally, I built the Dashboard to pull all this data together, and spent the last few weeks testing the app and fixing a lot of bugs I didn't see coming.

What started as a basic script to log expenses quickly evolved into something much more complex. Because I chose to use multiple JSON files to store everything, I realized I had to build my own validation layers, rollback protection, and corruption recovery just to keep the data safe. Linking debts and repayments also forced me to implement relational data modeling manually to make sure dates and balances stayed synchronized.

## Major Design Decisions
As I kept adding features, I had to make a few important technical decisions:

- **JSON Storage:** I decided to use plain JSON files instead of a real database. It forced me to learn how to handle file reading and writing manually, which was a great learning exercise.
- **Using IDs Instead of Names:** At first, I used category names to identify transactions. That broke immediately when I tried to rename a category in the app. I ended up switching to integer IDs for everything, just like a real database uses primary keys.
- **Soft Deleting Categories:** I realized if I deleted a category, all past transactions using that category would break because they wouldn't know what they were mapped to anymore. So, I added an `is_deleted` flag instead of actually deleting the data.
- **Rollback Protection:** When making a transfer, if the script updated the first account but crashed before updating the second, the money just disappeared into thin air. I used `copy.deepcopy()` to make changes in memory first, and only saved them to the files if everything was completely successful.
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

In the end, I wrote 14 different manual test groups and found 8 critical bugs. To see if the app would hold up under a lot of data, I wrote a script to dump 50,000 transactions, 2,000 debts, and 5,000 repayments into the JSON files. I really just wanted to see if Python could handle loading that much JSON into memory at once without slowing down the terminal. It turned out it handled it fine, using only about 30 MB of memory, and the core operations stayed reasonably fast.

## Project Size
To give an idea of what was actually built, here are the final numbers for Version 1:
- 9 major modules implemented
- 14 QA test groups completed
- 8 critical bugs fixed
- 50,000 transactions stress tested
- 2,000 debts tested
- 5,000 repayments tested
- Built entirely using the Python standard library and JSON storage

## Version 1 Outcome
I started out trying to write a basic script to track expenses, but the project grew more complex as I ran into real development challenges and discovered what was actually required to keep the data safe. To keep the math accurate and the files from corrupting, I ended up learning about relational data modeling, atomic transactions, and referential integrity—concepts I hadn't formally studied yet. The project definitely achieved my goal of learning how real software is built.

## Lessons Learned
The biggest lesson I learned is that just because an input is a valid data type (like a number) doesn't mean it makes sense for the business logic. I also learned that file systems are completely unreliable—if an app reads or writes files, it has to assume the file might be missing or corrupted. Finally, writing to multiple files showed me why databases use atomic transactions; if one file fails to save, the others have to revert, or the whole system gets corrupted.

## Future Direction
For Version 2, I would like to explore migrating the application to a web-based architecture. Possible areas I want to look into include replacing the JSON files with a real database engine, building an interactive user interface, and adding user authentication so more than one person can use it. I'm also thinking about adding features for data export and simple analytics, but that will depend on how the database migration goes.

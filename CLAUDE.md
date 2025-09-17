## Important Guidelines to Strictly Follow When Working with Codebase

1. Always use proper naming convention, dont use terms like revised, fixed, enhanced, advanced or any adjective. If say Something is x file name, it should remain x file name. 
2. Ensure the codebase is always structured.Similar items should be grouped together. No unorganized or messy code should be committed. 
3. Dont use comments.
4. The code must never be overengineered. Think Simple. 
5. Never use subagents unless asked to do so.
6. Use descriptive variable and function names.
7. Design first then implement. 
8. Always ensure that we dont have unnecessary files in our codebase such as old code, unused files. If required for safekeeping keep them in a separate directory called old_code or archive. Make sure that we store any output content/data in the appropriate directory. They must not be lost or scattered around. 
9. Always keep .md files in docs/ directory.
10. Always keep track of the project state through plan.md file in the root directory containing checklist of tasks to be done. Use design.md for project design documentation. Update done.md after each session with checklist of completed tasks, including any deviations from the original plan to ensure project feasibility.

# VERY IMPORTANT - NEVER USE FAKE DATA OR FALSE INFORMATION TO MAKE CODE WORK. Always work with real data. Incase the inforamtion is not available, assume it will come from the api endpoint mentioned in the system design. 
# THERE IS NO NEED TO RUN THE APPLICATION OR TEST IT UNLESS ASKED TO.
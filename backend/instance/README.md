# Instance Folder

This folder contains the SQLite database file for development.

## Important Notes:

- **DO NOT DELETE** the `database.db` file unless you want to reset the database
- The database persists between Flask restarts
- To reset the database, run: `npm run init-db`
- Database files (*.db) are in .gitignore and will not be committed to git

## Database Location

The database is stored at: `backend/instance/database.db`

This location was chosen to:
1. Keep the database separate from code
2. Prevent accidental deletion during Flask debug mode restarts
3. Follow Flask best practices for instance-specific files

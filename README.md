# College Tool (Lab 08)

## Run locally on Windows

Open PowerShell in this project folder and set local development values:

```powershell
$env:DATABASE_URL = "sqlite:///local.db"
$env:PASSWORD_PEPPER = "local-dev-password-pepper"
$env:SECRET_KEY = "local-dev-secret-key-change-this"
$env:JWT_KEY = "local-dev-jwt-secret-key-at-least-32-chars"
```

Install the project dependencies and start the Flask app:

```powershell
uv sync
uv run lab08
```

Open http://127.0.0.1:5000/ in a browser. On a fresh local database, the app
seeds demo users and classes. Sign in as `Johnny Test` with password `Zebra`
to view the student dashboard, or as `Dr. Stone` with password `Hello World`
to view the teacher dashboard. Stop the server with Ctrl+C.

**New Login Credential**
Any student name in the list has the password 'student123' to view the student dashboard, as well as the admin having the password 'admin123'. Teachers will sign in with their name and password 'teacher123' to view the teacher dashboard.

The environment values above are for local development only. Do not use them
in production.

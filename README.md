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
seeds demo users and classes. For example, sign in as `Johnny Test` with
password `Zebra`. Stop the server with Ctrl+C.

The environment values above are for local development only. Do not use them
in production.

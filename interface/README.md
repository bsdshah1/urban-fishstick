# Minimal interface

Run from repository root:


Required environment variables:

- `JWT_SECRET_KEY` (required in all non-development environments): at least 32 characters and used to sign/verify auth tokens.
- `ENV` (optional): only when set to `development` will the backend allow a local fallback JWT secret.

Example:

```bash
export JWT_SECRET_KEY="replace-with-a-strong-32+-char-secret"
# Optional local dev fallback gate:
# export ENV=development
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn interface.main:app --reload
```

Open:

- `http://127.0.0.1:8000/` for a simple HTML landing page
- `http://127.0.0.1:8000/docs` for Swagger UI
- `http://127.0.0.1:8000/api/lesson-plan` for a demo JSON response

# Minimal interface

Run from repository root:

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

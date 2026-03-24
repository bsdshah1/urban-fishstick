# Minimal interface

This interface runs with Python's standard library (no pip install required).

Run from repository root:

```bash
python3 interface/main.py
```

Open:

- `http://127.0.0.1:8000/` for a simple HTML landing page
- `http://127.0.0.1:8000/api/lesson-plan` for a demo JSON response

Example with query params:

```bash
curl "http://127.0.0.1:8000/api/lesson-plan?year_group=Year%204&block=Multiplication%20and%20division&objective=Multiply%20a%202-digit%20number%20by%201-digit"
```

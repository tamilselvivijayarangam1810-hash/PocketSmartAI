# PocketSmart AI

A complete FastAPI + Jinja2 + SQLite + Gemini application for budget-aware planning across:

- Home interiors
- Party planning
- Jewelry recommendations with optional outfit image analysis

## Important implementation note

The supplied project document mixes Flask and FastAPI and references Gemini 1.5 Flash Pro. This implementation standardizes the project on **FastAPI**, matching the later milestones in the document, and uses the current Google GenAI Python SDK. The Gemini model is configurable through `.env`.

When `GEMINI_API_KEY` is not configured, the application still runs using a deterministic local recommendation fallback. This makes the project easy to demonstrate and test without an API key.

The application does not pretend to have live Amazon/Flipkart/IKEA/Swiggy/Zomato/OYO inventory. It generates platform search links and clearly marks them as search links. Live inventory integrations can be added later through official partner/merchant APIs.

## Features

- Registration / login / logout
- JWT authentication stored in an HttpOnly cookie
- SQLite persistence
- Home, Party and Jewelry planners
- Optional jewelry outfit image upload
- Gemini multimodal analysis for jewelry images
- Structured JSON AI output
- Budget validation and allocation
- Recommendation history
- Responsive frontend
- Local fallback recommendations when Gemini is unavailable
- Automated API tests
- Health endpoint

## Project structure

```text
PocketSmartAI/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── dependencies.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── catalog.py
│   │   ├── gemini_service.py
│   │   └── planner_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── pages.py
│   │   └── planners.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── home.html
│   │   ├── party.html
│   │   ├── jewelry.html
│   │   └── history.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## 1. VS Code setup

Install:

- Python 3.11+
- VS Code
- VS Code Python extension

Open the `PocketSmartAI` folder in VS Code.

### Windows

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 2. Configure Gemini

Open `.env`.

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

If you leave `GEMINI_API_KEY` blank, the app automatically uses the local fallback.

The model is configurable because model availability changes over time.

## 3. Run

```bash
python run.py
```

Then open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 4. Test

```bash
pytest -q
```

The tests exercise registration, login, home planning, party planning, jewelry planning, history and health.

## 5. Demo flow

1. Register an account.
2. Log in.
3. Open Home Planner.
4. Enter a budget and room requirements.
5. Generate recommendations.
6. Open Party Planner and generate an event plan.
7. Open Jewelry Planner and optionally upload an outfit image.
8. Open History to see saved plans.

## 6. Gemini behavior

The AI service asks Gemini to return a strict JSON recommendation object. If the call fails, returns invalid JSON, or no API key is present, the planner service falls back to local recommendations.

The fallback is intentionally deterministic and safe for demonstrations.

## 7. Extending to real product APIs

The document calls for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO data. This starter implementation uses platform search URLs instead of scraping. To add real inventory:

1. Add a service under `app/services/`.
2. Use an official API/partner program.
3. Normalize products into the `RecommendationItem` schema.
4. Pass normalized catalog data into `planner_service.py`.
5. Keep credentials in `.env`, never in source code.

## 8. Security notes

This is a student/project-ready implementation, not a production deployment. Before production:

- Use HTTPS.
- Put the app behind a reverse proxy.
- Use a strong random `JWT_SECRET`.
- Move SQLite to PostgreSQL.
- Add rate limiting.
- Add CSRF protection if cookie-based browser mutations are expanded.
- Restrict upload MIME types and image dimensions further.
- Add centralized logging and monitoring.
- Use official vendor APIs instead of scraping.

## Source alignment

The supplied documentation describes budget-aware Home, Party and Jewelry scenarios, Gemini multimodal processing, modular backend routes, authentication, session/history pages, and a Jinja2 frontend. This implementation covers those requested components while resolving the document's Flask/FastAPI inconsistency by using FastAPI throughout.

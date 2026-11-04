# Linkly

A URL shortener with click analytics, built with Flask and SQLite.

## Features
- Shorten any http(s) URL to a random 6-character code
- Optional custom aliases (`/my-link`)
- 302 redirects that record each click (timestamp + user agent)
- Stats endpoint with total clicks and clicks per day
- Input validation (blocks `javascript:` and other unsafe schemes)
- Unit tests for the API

## Setup
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/shorten` | Body: `{"url": "...", "custom_code": "optional"}` |
| GET | `/<code>` | Redirects to the original URL and logs a click |
| GET | `/api/stats/<code>` | Returns click statistics |

Example:
```bash
curl -X POST localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Tests
```bash
python -m unittest discover -v
```

## Design notes
- **App factory** (`create_app`) so tests run against an isolated database.
- **`secrets`** instead of `random` for unpredictable codes; collisions are retried.
- **Parameterized queries** everywhere to prevent SQL injection.
- Clicks live in their own table so analytics can grow (referrers, geo, etc.).

## Ideas for future work
- Rate limiting, link expiry, user accounts
- A small frontend, Docker setup, deployment

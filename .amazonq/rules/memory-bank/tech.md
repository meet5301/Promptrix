# Promptrix — Technology Stack

## Languages
- **Python 3** — backend (Flask app, site engine, utilities)
- **HTML/CSS/JS** — frontend templates (vanilla JS, no framework)
- **HTML** — all AI-generated output files

## Backend Framework
- **Flask >= 3.0.0** — web framework, routing, session management
- **Gunicorn** — WSGI production server

## AI / LLM
- **Anthropic Claude API** — site generation via `anthropic` Python SDK
- API key set via `ANTHROPIC_API_KEY` environment variable

## Database
- **MongoDB** via **pymongo >= 4.6.0** — user accounts, site history

## Key Dependencies (requirements.txt)
```
flask>=3.0.0
pymongo>=4.6.0
flask
gunicorn
pymongo
```

## Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (Windows)
set ANTHROPIC_API_KEY=sk-ant-...

# Set API key (Mac/Linux)
export ANTHROPIC_API_KEY=sk-ant-...

# Run development server
python app.py

# Fix syntax in generated sites (utility)
python fix_syntax.py
```

## Runtime
- Default port: **5000**
- URL: http://localhost:5000
- Generated sites stored in: `.generated_sites/<uuid>/`

## Frontend
- Vanilla JavaScript (no React/Vue/Angular)
- Inline CSS + external stylesheet in templates
- iframe used for live site preview
- Fetch API for AJAX calls to Flask endpoints

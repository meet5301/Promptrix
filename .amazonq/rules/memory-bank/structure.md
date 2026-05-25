# Promptrix — Project Structure

## Directory Layout
```
Promptrix/
├── app.py                  # Flask app: routes, auth, API endpoints
├── site_engine.py          # AI generation logic, prompt building, ZIP creation
├── fix_syntax.py           # Utility: post-process/repair generated HTML syntax
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html          # Main UI (prompt input, preview, refine, download)
│   ├── templates.html      # Template selection & deep customization form
│   ├── template_preview.html # Preview page for individual templates
│   └── __tmp_check.js      # Temporary JS utility/check script
└── .generated_sites/       # UUID-named folders, each holding generated HTML pages
    └── <uuid>/
        ├── index.html
        ├── about.html
        └── ...             # Additional pages per generation
```

## Core Components

### app.py
- Flask application factory and route definitions
- Handles `/generate`, `/refine`, `/download`, `/login`, `/register`, `/history`
- Calls `site_engine.py` functions and returns JSON or file responses
- MongoDB connection for user accounts and site history

### site_engine.py
- Builds prompts sent to Anthropic Claude API
- Parses Claude's response into individual HTML page files
- Writes pages to `.generated_sites/<uuid>/`
- Packages site into a ZIP for download
- Template customization logic: maps form fields → prompt instructions

### fix_syntax.py
- Standalone utility to scan and repair malformed HTML in generated files
- Run independently to clean up syntax issues in `.generated_sites/`

### templates/index.html
- Single-page app UI: prompt textarea, generate button, iframe preview
- Refine panel for follow-up modifications
- Viewport toggle (desktop/tablet/mobile)
- Download and history sidebar

### templates/templates.html
- Template gallery with 4 cards (Modern, Creative, Minimal, Professional)
- Expandable customization form per template covering all site sections
- Submits customization config back to main generation flow

## Architectural Patterns
- **Flask + Jinja2** for server-rendered HTML templates
- **REST-style JSON API** — frontend JS calls `/generate`, `/refine`, `/download` endpoints
- **UUID-based site storage** — each generation gets a unique folder under `.generated_sites/`
- **Stateless generation** — site UUID passed back to client, used for refine/download
- **MongoDB** for user persistence; site history stored as list of UUID references

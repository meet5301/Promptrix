# Promptrix — Development Guidelines

## Code Quality Standards

### Python Style
- Compact, dense code preferred — multiple assignments on one line when related (`a = x; b = y`)
- Short helper functions prefixed with `_` for private/internal use (e.g., `_norm`, `_slug`, `_hash`, `_load_site`)
- Type hints used consistently: `Dict`, `List`, `Optional`, `Tuple`, `Any` from `typing`
- `from __future__ import annotations` used in engine module
- Dataclass-style spec dicts (`Dict[str, Any]`) passed between functions instead of class instances
- Guard clauses at function entry: `if not x: return default`

### Naming Conventions
- Snake_case for all Python identifiers
- Short, descriptive names: `sid` (site id), `pk` (page key), `fc` (font choice), `st` (safe title)
- Constants in UPPER_SNAKE_CASE: `NAMED_COLORS`, `SITE_KEYWORDS`, `CONTENT_BANK`, `ICONS`
- MongoDB collections as short uppercase globals: `USERS`, `HIST`
- In-memory cache as uppercase: `SITES: Dict[str, Dict[str, str]]`

### Error Handling
- Flask routes use `try/except` with specific exception types first, then broad `Exception`
- Return `jsonify({"error": str(e)}), 500` pattern for all error responses
- Silent JSON parsing: `request.get_json(silent=True) or {}`
- Fallback chaining: `SITES.get(sid) or _load_site(sid)` — memory first, then disk

## Architectural Patterns

### Flask Route Pattern
Every mutating route follows this exact pattern:
```python
@app.route("/endpoint", methods=["POST"])
def endpoint():
    d = request.get_json(silent=True) or {}
    field = (d.get("field") or "").strip()
    if not field: return jsonify({"error": "..."}), 400
    try:
        result = do_work(field)
        sid = uuid4().hex
        # build page_map
        SITES[sid] = page_map
        _save_site(sid, page_map)
        email = _session_user(request)
        if email:
            HIST.insert_one({...})
        resp = make_response(jsonify({"result": result, "site_id": sid}))
        resp.set_cookie("last_site_id", sid, max_age=60*60*6, samesite="Lax")
        return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Dual Storage Pattern
Sites are stored in both memory and disk simultaneously:
- `SITES[sid] = page_map` — fast in-memory access
- `_save_site(sid, page_map)` — persistent disk storage under `.generated_sites/<sid>/`
- On read: `SITES.get(sid) or _load_site(sid)` — memory-first with disk fallback

### Cookie-Based Session Auth
- Auth token stored in `px_tok` HttpOnly cookie (30-day expiry)
- `_session_user(request)` helper extracts email from token via MongoDB lookup
- Token rotated on every login
- Logout invalidates token in DB and deletes cookie

### Spec Dict Pattern (site_engine.py)
All generation parameters are collected into a single `spec: Dict[str, Any]` before calling `build_pages(spec)`. This avoids long function signatures and makes it easy to add new parameters.

```python
spec = {
    "site_type": ..., "site_title": ..., "sections": ...,
    "colors": ..., "seed": ..., "overrides": ..., ...
}
pages = build_pages(spec)
```

### Stable Deterministic Seeding
`_stable_seed(text)` uses SHA-256 of normalized prompt → deterministic integer seed. Same prompt always produces same design. Variation is added via `seed = (base_seed + variation) % 10_000_000`.

## Semantic Patterns

### NLP Extraction Pipeline
`generate_site(prompt)` runs a pipeline of extraction functions before building:
1. `detect_site_type(prompt)` — keyword scoring across 14 site types
2. `extract_colors(prompt)` — hex codes + named colors (English + Hinglish)
3. `extract_numbers(prompt)` — regex patterns for cards, columns, nav items, etc.
4. `extract_section_overrides(prompt)` — key=value pairs in prompt
5. `extract_pages_with_labels(prompt)` — page list from `pages:` or `menu:` directives
6. `infer_sections(prompt, site_type)` — section aliases + site-type defaults
7. `reorder_sections(...)` — deterministic shuffle with explicit intent overrides

### Content Bank Pattern
`CONTENT_BANK` is a nested dict keyed by site type, then content key. Access via `_get_content(site_type, key, default)` which falls back to `"landing"` type if site type not found.

### Section Builder Map
`SECTION_BUILDERS` dict maps section name → callable. Home page is assembled by iterating `home_sections` and calling each builder:
```python
"home": lambda: "".join(SECTION_BUILDERS.get(s, lambda: "")() for s in home_sections)
```

### HTML Escaping
All user-derived strings are escaped with `_he.escape()` (Python's `html` module) before insertion into HTML templates. Never insert raw user input into HTML.

### Inline SVG Icons
`ICONS` dict provides inline SVG strings — no external icon library dependency. Referenced as `ICONS["star"]`, `ICONS["check"]`, etc.

### CSS Custom Properties
All generated CSS uses `--primary`, `--secondary`, `--accent`, `--bg`, `--text`, `--muted`, `--border`, `--card`, `--radius` CSS variables. Colors are set once in `:root` and referenced everywhere via `var(--primary)`.

### `color-mix()` for Tints
Tints and transparent variants use CSS `color-mix(in srgb, var(--primary) 12%, transparent)` — no pre-computed hex values needed.

## Frontend Patterns (JS)

### Vanilla JS Only
No framework. All interactivity via `document.querySelector`, `addEventListener`, `classList.toggle`.

### Toast Notification
`showToast(msg)` creates/reuses a `#toast` div, adds `.show` class, removes after 2800ms.

### Scroll Reveal
`IntersectionObserver` applied to all card elements — `opacity:0; transform:translateY(20px)` initially, animated to visible on intersection.

### Cart Count
`addToCart(name, price)` increments `#cart-count` badge and shows toast. Simple in-memory counter.

### Hamburger Nav
`.hamburger` button toggles `.nav.open` class; CSS shows `.nav-links` and `.nav-cta` as column layout when open.

## File Utility Pattern (fix_syntax.py)
One-off scripts that modify source files use:
1. Read file → string
2. `re.sub()` with `re.DOTALL` to remove/replace function bodies
3. Find insertion point with `str.find()`
4. Splice new content at index
5. Write back

## MongoDB Patterns
- `USERS.create_index("email", unique=True)` — enforced at startup
- `HIST.create_index([("email", 1), ("ts", -1)])` — compound index for user history queries
- History queries: `.sort("ts", DESCENDING).limit(30)`
- `datetime` objects converted to display strings before JSON serialization: `i["ts"].strftime("%d %b")`

## Security Practices
- Passwords hashed with SHA-256 via `hashlib` (no salt — consider upgrading to bcrypt)
- Auth tokens: `secrets.token_hex(32)` — cryptographically secure
- Cookies: `httponly=True`, `samesite="Lax"`
- Filename sanitization: `Path(filename).name` + `.html` extension enforcement
- All HTML output escaped with `html.escape()`

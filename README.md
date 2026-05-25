# Promptrix — AI Website Builder

## Project Structure
```
Promptrix/
├── app.py                  # Flask backend + Anthropic API
├── site_engine.py          # AI site generation logic
├── requirements.txt
├── templates/
│   ├── index.html          # Main app UI
│   └── templates.html      # Template selection & customization
└── README.md
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run
```bash
python app.py
```

Open: http://localhost:5000

---

## Features

- **LLM-powered generation** — Claude generates complete websites
- **Template system** — 4 pre-designed templates (Modern, Creative, Minimal, Professional)
- **Advanced customization** — Customize every aspect:
  - Header (brand name, menu count, style)
  - Hero section (title, subtitle, background)
  - Home page (sections, features, testimonials)
  - Footer (company info, social, newsletter)
  - Colors (primary & secondary)
  - Advanced settings (page count, description)
- **Real-time preview** — Live iframe preview with responsive viewport
- **Refine mode** — Follow-up instructions to modify generated site
- **Download** — Get website as HTML ZIP
- **User authentication** — Save history and preferences
- **MongoDB storage** — Persistent user data and site history

## Usage

### Quick Generation
1. Describe your website in the prompt
2. Click "Generate Website"
3. Preview and download

### Template Customization
1. Click "🎨 Use Templates" button
2. Select a template
3. Click "Customize" on desired template
4. Configure all settings:
   - Brand and header options
   - Hero section design
   - Home page layout
   - Footer content
   - Color scheme
   - Advanced settings
5. Click "Save & Generate Site"
6. Preview your customized website

## Tips

- Be specific: "4 product cards", "blue accent", "sticky navbar"
- Use templates for structured, professional designs
- Customize templates to match your brand exactly
- Download and host your generated sites locally or online
- Use Ctrl+Enter to generate quickly
- After generating, use the Refine box for changes like:
  - "make the hero taller"
  - "change primary color to red"
  - "add a testimonials section"
  - "make it dark theme"

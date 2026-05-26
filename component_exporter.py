"""
Component Exporter - Convert HTML to React/Vue/TypeScript components
Pure Python - NO external APIs
"""

import re
from typing import Dict, List, Optional, Tuple

class ComponentExporter:
    """Export generated sites as React/Vue components"""
    
    def __init__(self):
        self.jsx_template = self._jsx_template()
        self.vue_template = self._vue_template()
        self.tailwind_template = self._tailwind_template()
    
    def export_as_react(self, html: str, component_name: str = "Website", with_tailwind: bool = True) -> str:
        """Convert HTML to React JSX component"""
        jsx = self._html_to_jsx(html)
        if with_tailwind:
            component = f"""import React from 'react';

export default function {component_name}() {{
  return (
    <div className="min-h-screen">
{jsx}
    </div>
  );
}}
"""
        else:
            component = f"""import React from 'react';
import styles from './{component_name}.module.css';

export default function {component_name}() {{
  return (
    <div>
{jsx}
    </div>
  );
}}
"""
        return component

    def export_modular_react(self, config: Dict, html: str, component_name: str = "GeneratedSite") -> Dict[str, str]:
        """Export reusable section components + page composer."""
        sections = config.get("sections") or []
        files: Dict[str, str] = {
            "src/types/site.ts": self.export_as_typescript(config),
            "src/pages/WebsitePage.tsx": self.export_as_react(html, component_name, with_tailwind=True),
            "src/components/index.ts": "",
        }
        section_map = {
            "hero": "HeroSection",
            "features": "FeaturesSection",
            "pricing": "PricingSection",
            "testimonials": "TestimonialsSection",
            "faq": "FaqSection",
            "products": "ProductsSection",
            "menu": "MenuSection",
            "gallery": "GallerySection",
            "team": "TeamSection",
            "contact": "ContactSection",
            "cta": "CtaSection",
            "packages": "PackagesSection",
            "courses": "CoursesSection",
            "containers": "ContainersSection",
        }
        imports = []
        body = []
        custom = config.get("custom_content") or {}
        colors = config.get("colors") or {}
        for sid in sections:
            comp = section_map.get(sid)
            if not comp:
                continue
            files[f"src/components/{comp}.tsx"] = self._section_component_tsx(sid, comp, custom, colors)
            imports.append(f"import {comp} from '../components/{comp}';")
            body.append(f"      <{comp} />")
        files["src/pages/WebsitePage.tsx"] = f"""import React from 'react';
{chr(10).join(imports)}

export default function {component_name}() {{
  return (
    <main>
{chr(10).join(body)}
    </main>
  );
}}
"""
        files["src/components/index.ts"] = "\n".join(
            f"export {{ default as {section_map[s]} }} from './{section_map[s]}';"
            for s in sections if s in section_map
        )
        return files

    def _section_component_tsx(self, section_id: str, comp_name: str, custom: Dict, colors: Dict) -> str:
        """Minimal typed React section stubs driven by parsed config."""
        if section_id == "hero":
            return f"""import React from 'react';

export default function {comp_name}() {{
  return (
    <section id="hero" style={{{{ minHeight: '82vh', padding: '5rem 5%', background: '{colors.get("primary", "#2563eb")}' }}}}>
      <h1>{custom.get('hero_title', 'Welcome')}</h1>
      <p>{custom.get('hero_subtitle', '')}</p>
    </section>
  );
}}
"""
        if section_id == "pricing":
            plans = custom.get("pricing_plans") or []
            items = ",\n    ".join(
                f"{{ name: '{p.get('name','Plan')}', price: '{p.get('price','₹0')}' }}" for p in plans
            ) or "{ name: 'Starter', price: 'Free' }"
            return f"""import React from 'react';

const plans = [{items}];

export default function {comp_name}() {{
  return (
    <section id="pricing" style={{{{ padding: '4rem 5%' }}}}>
      <h2>Pricing</h2>
      <div style={{{{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))' }}}}>
        {{plans.map((p) => (
          <article key={{p.name}} style={{{{ border: '1px solid #ddd', borderRadius: 12, padding: 20 }}}}>
            <h3>{{p.name}}</h3>
            <p>{{p.price}}</p>
          </article>
        ))}}
      </div>
    </section>
  );
}}
"""
        if section_id == "contact":
            info = custom.get("contact_info") or {}
            return f"""import React from 'react';

export default function {comp_name}() {{
  return (
    <section id="contact" style={{{{ padding: '4rem 5%' }}}}>
      <h2>Contact</h2>
      <p>Email: {info.get('email', 'hello@example.com')}</p>
      <p>Phone: {info.get('phone', '+91 00000 00000')}</p>
    </section>
  );
}}
"""
        cards = (custom.get("section_cards") or {}).get(section_id, [])
        card_lines = "\\n".join(
            f"        <li key='{c.get('title','Item')}'>{c.get('title','Item')}</li>" for c in cards[:8]
        ) or "        <li>Item</li>"
        return f"""import React from 'react';

export default function {comp_name}() {{
  return (
    <section id="{section_id}" style={{{{ padding: '4rem 5%' }}}}>
      <h2>{section_id.title()}</h2>
      <ul>
{card_lines}
      </ul>
    </section>
  );
}}
"""
    
    def export_as_vue(self, html: str, component_name: str = "Website") -> str:
        """Convert HTML to Vue 3 component"""
        vue_html = self._html_to_vue(html)
        
        component = f"""<template>
  <div class="min-h-screen">
{vue_html}
  </div>
</template>

<script setup lang="ts">
import {{ ref }} from 'vue';

// Component logic here
</script>

<style scoped>
{self._extract_scoped_styles(html)}
</style>
"""
        
        return component
    
    def export_as_typescript(self, config: Dict) -> str:
        """Export configuration as TypeScript types"""
        ts_types = f"""export interface SiteConfig {{
  brand: string;
  tagline: string;
  siteType: 'ecommerce' | 'restaurant' | 'portfolio' | 'saas' | 'blog' | 'gym' | 'agency' | 'landing';
  colors: {{
    primary: string;
    secondary: string;
    accent: string;
  }};
  pages: string[];
  sections: string[];
  customContent?: {{
    [key: string]: string;
  }};
}}

export interface PageConfig {{
  name: string;
  filename: string;
  title: string;
  description?: string;
}}

export interface GeneratedSite {{
  pages: PageConfig[];
  siteName: string;
  siteType: string;
  pageCount: number;
  success: boolean;
  metadata?: {{
    brand: string;
    tagline: string;
    colors: SiteConfig['colors'];
    pages: string[];
  }};
}}

export const DEFAULT_COLORS = {{
  primary: '#2563eb',
  secondary: '#1e40af',
  accent: '#f59e0b',
}};

export const SITE_TYPES = [
  'ecommerce',
  'restaurant',
  'portfolio',
  'saas',
  'blog',
  'gym',
  'agency',
  'landing',
] as const;
"""
        
        return ts_types
    
    def export_as_nextjs(self, pages: List[Dict], config: Dict) -> Dict[str, str]:
        """Export as Next.js app router structure"""
        files = {}
        
        files['app/layout.tsx'] = """import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Website',
  description: 'Welcome to our site',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
"""
        
        for page in pages:
            page_name = page.get('name', 'home')
            slug = page_name.lower().replace(' ', '-')
            
            files[f'app/{slug}/page.tsx'] = f"""import {{ Suspense }} from 'react';

export default async function {page_name.title()}Page() {{
  return (
    <Suspense fallback={{'<div>Loading...</div>'}}>
      <main>
        {{{self._html_to_jsx(page.get('html', ''))}}}
      </main>
    </Suspense>
  );
}}
"""
        
        files['app/api/generate/route.ts'] = """import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const config = await request.json();
  
  try {
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to generate site' },
      { status: 500 }
    );
  }
}
"""
        
        files['tailwind.config.js'] = """module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
"""
        
        return files
    
    def _html_to_jsx(self, html: str, indent: int = 2) -> str:
        """Convert HTML to JSX syntax"""
        jsx = html
        jsx = re.sub(r'<!DOCTYPE[^>]*>', '', jsx)
        jsx = re.sub(r'<html[^>]*>', '', jsx)
        jsx = re.sub(r'</html>', '', jsx)
        jsx = re.sub(r'<head>.*?</head>', '', jsx, flags=re.DOTALL)
        jsx = re.sub(r'<body[^>]*>', '', jsx)
        jsx = re.sub(r'</body>', '', jsx)
        jsx = jsx.replace('class=', 'className=')
        jsx = re.sub(
            r'style="([^"]*)"',
            lambda m: self._convert_style_to_object(m.group(1)),
            jsx
        )
        lines = jsx.split('\n')
        indented_lines = [' ' * indent + line if line.strip() else '' for line in lines]
        return '\n'.join(indented_lines)
    
    def _html_to_vue(self, html: str) -> str:
        """Convert HTML to Vue template syntax"""
        vue = html
        vue = re.sub(r'<!DOCTYPE[^>]*>', '', vue)
        vue = re.sub(r'<html[^>]*>', '', vue)
        vue = re.sub(r'</html>', '', vue)
        vue = re.sub(r'<head>.*?</head>', '', vue, flags=re.DOTALL)
        vue = re.sub(r'<body[^>]*>', '', vue)
        vue = re.sub(r'</body>', '', vue)
        vue = re.sub(r'style="([^"]*)"', r':style="{\n\1\n}"', vue)
        return vue
    
    def _convert_style_to_object(self, style_str: str) -> str:
        """Convert CSS style string to JavaScript object"""
        styles = {}
        for declaration in style_str.split(';'):
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                prop = prop.strip()
                value = value.strip()
                prop_camel = self._css_to_camel_case(prop)
                styles[prop_camel] = f"'{value}'"
        return "style={{" + ', '.join(f"{k}: {v}" for k, v in styles.items()) + "}}"
    
    def _css_to_camel_case(self, css_prop: str) -> str:
        """Convert CSS property to camelCase"""
        parts = css_prop.split('-')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])
    
    def _extract_inline_styles(self, html: str) -> Dict[str, str]:
        """Extract all inline styles from HTML"""
        styles = {}
        style_matches = re.findall(r'style="([^"]*)"', html)
        for i, style_str in enumerate(style_matches):
            styles[f"style{i}"] = style_str
        return styles
    
    def _extract_scoped_styles(self, html: str) -> str:
        """Extract styles for Vue scoped style tag"""
        style_tags = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
        if style_tags:
            return style_tags[0]
        css = ""
        inline_styles = re.findall(r'style="([^"]*)"', html)
        for style in inline_styles:
            css += f"\n/* Generated from inline style: {style} */\n"
        return css
    
    def _jsx_template(self) -> str:
        return ""
    
    def _vue_template(self) -> str:
        return ""
    
    def _tailwind_template(self) -> str:
        return ""


def export_to_react(html: str, component_name: str = "Website") -> str:
    exporter = ComponentExporter()
    return exporter.export_as_react(html, component_name, with_tailwind=True)


def export_to_vue(html: str, component_name: str = "Website") -> str:
    exporter = ComponentExporter()
    return exporter.export_as_vue(html, component_name)


def export_to_typescript(config: Dict) -> str:
    exporter = ComponentExporter()
    return exporter.export_as_typescript(config)


def export_to_nextjs(pages: List[Dict], config: Dict) -> Dict[str, str]:
    exporter = ComponentExporter()
    return exporter.export_as_nextjs(pages, config)


def export_modular_react(config: Dict, html: str, component_name: str = "GeneratedSite") -> Dict[str, str]:
    exporter = ComponentExporter()
    return exporter.export_modular_react(config, html, component_name)

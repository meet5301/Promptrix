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
        # Extract inline styles
        styles = self._extract_inline_styles(html)
        
        # Convert HTML to JSX
        jsx = self._html_to_jsx(html)
        
        # Generate component
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
        
        # Create layout
        files['app/layout.tsx'] = """import type {{ Metadata }} from 'next';
import './globals.css';

export const metadata: Metadata = {{
  title: 'Website',
  description: 'Welcome to our site',
}};

export default function RootLayout({{
  children,
}: {{
  children: React.ReactNode;
}}) {{
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}}
"""
        
        # Create pages
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
        
        # Create API routes for generation
        files['app/api/generate/route.ts'] = """import {{ NextRequest, NextResponse }} from 'next/server';

export async function POST(request: NextRequest) {{
  const config = await request.json();
  
  // Generate site
  try {{
    // Call your local engine here
    return NextResponse.json({{ success: true }});
  }} catch (error) {{
    return NextResponse.json(
      {{ error: 'Failed to generate site' }},
      {{ status: 500 }}
    );
  }}
}}
"""
        
        # Create tailwind config
        files['tailwind.config.js'] = """module.exports = {{
  content: [
    './app/**/*.{{js,ts,jsx,tsx}}',
    './components/**/*.{{js,ts,jsx,tsx}}',
  ],
  theme: {{
    extend: {{}},
  }},
  plugins: [],
}};
"""
        
        return files
    
    def _html_to_jsx(self, html: str, indent: int = 2) -> str:
        """Convert HTML to JSX syntax"""
        jsx = html
        
        # Remove DOCTYPE and html tags
        jsx = re.sub(r'<!DOCTYPE[^>]*>', '', jsx)
        jsx = re.sub(r'<html[^>]*>', '', jsx)
        jsx = re.sub(r'</html>', '', jsx)
        jsx = re.sub(r'<head>.*?</head>', '', jsx, flags=re.DOTALL)
        jsx = re.sub(r'<body[^>]*>', '', jsx)
        jsx = re.sub(r'</body>', '', jsx)
        
        # Convert class to className
        jsx = jsx.replace('class=', 'className=')
        
        # Convert style to object notation
        jsx = re.sub(
            r'style="([^"]*)"',
            lambda m: self._convert_style_to_object(m.group(1)),
            jsx
        )
        
        # Convert for loops to map
        # (simplified - would need more complex parsing in production)
        
        # Add indentation
        lines = jsx.split('\n')
        indented_lines = [' ' * indent + line if line.strip() else '' for line in lines]
        
        return '\n'.join(indented_lines)
    
    def _html_to_vue(self, html: str) -> str:
        """Convert HTML to Vue template syntax"""
        vue = html
        
        # Remove DOCTYPE and wrap tags
        vue = re.sub(r'<!DOCTYPE[^>]*>', '', vue)
        vue = re.sub(r'<html[^>]*>', '', vue)
        vue = re.sub(r'</html>', '', vue)
        vue = re.sub(r'<head>.*?</head>', '', vue, flags=re.DOTALL)
        vue = re.sub(r'<body[^>]*>', '', vue)
        vue = re.sub(r'</body>', '', vue)
        
        # Convert style attribute
        vue = re.sub(r'style="([^"]*)"', r':style="{\n\1\n}"', vue)
        
        # Vue-specific syntax conversions
        # (could add v-if, v-for, etc. here)
        
        return vue
    
    def _convert_style_to_object(self, style_str: str) -> str:
        """Convert CSS style string to JavaScript object"""
        styles = {}
        for declaration in style_str.split(';'):
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                prop = prop.strip()
                value = value.strip()
                
                # Convert CSS property to camelCase
                prop_camel = self._css_to_camel_case(prop)
                styles[prop_camel] = f"'{value}'"
        
        # Return as inline style object
        return "style={{" + ', '.join(f"{k}: {v}" for k, v in styles.items()) + "}}"
    
    def _css_to_camel_case(self, css_prop: str) -> str:
        """Convert CSS property to camelCase"""
        parts = css_prop.split('-')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])
    
    def _extract_inline_styles(self, html: str) -> Dict[str, str]:
        """Extract all inline styles from HTML"""
        styles = {}
        
        # Find all style attributes
        style_matches = re.findall(r'style="([^"]*)"', html)
        
        for i, style_str in enumerate(style_matches):
            class_name = f"style{i}"
            styles[class_name] = style_str
        
        return styles
    
    def _extract_scoped_styles(self, html: str) -> str:
        """Extract styles for Vue scoped style tag"""
        # Find style tags
        style_tags = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
        
        if style_tags:
            return style_tags[0]
        
        # Generate from inline styles
        css = ""
        inline_styles = re.findall(r'style="([^"]*)"', html)
        
        for style in inline_styles:
            css += f"\n/* Generated from inline style: {style} */\n"
        
        return css
    
    def _jsx_template(self) -> str:
        """JSX component template"""
        return """
export default function Component() {
  return (
    <div className="w-full">
      {/* Component content */}
    </div>
  );
}
"""
    
    def _vue_template(self) -> str:
        """Vue component template"""
        return """
<template>
  <div class="w-full">
    <!-- Component content -->
  </div>
</template>

<script setup lang="ts">
// Component logic
</script>

<style scoped>
/* Component styles */
</style>
"""
    
    def _tailwind_template(self) -> str:
        """Tailwind CSS configuration"""
        return """module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
"""


def export_to_react(html: str, component_name: str = "Website") -> str:
    """Public API: Export to React"""
    exporter = ComponentExporter()
    return exporter.export_as_react(html, component_name, with_tailwind=True)


def export_to_vue(html: str, component_name: str = "Website") -> str:
    """Public API: Export to Vue"""
    exporter = ComponentExporter()
    return exporter.export_as_vue(html, component_name)


def export_to_typescript(config: Dict) -> str:
    """Public API: Export TypeScript types"""
    exporter = ComponentExporter()
    return exporter.export_as_typescript(config)


def export_to_nextjs(pages: List[Dict], config: Dict) -> Dict[str, str]:
    """Public API: Export Next.js project"""
    exporter = ComponentExporter()
    return exporter.export_as_nextjs(pages, config)

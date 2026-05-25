#!/usr/bin/env python
"""
Phase 1 Validation Script - Test all engines locally
NO EXTERNAL APIs - Pure Python validation
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_local_engine():
    """Test template generation"""
    print("\n🧪 Testing local_engine.py...")
    from local_engine import generate_site_local
    
    config = {
        "brand": "Test Store",
        "tagline": "Testing the generator",
        "site_type": "ecommerce",
        "pages": ["home", "products"],
        "sections": ["hero", "features", "cta"],
        "colors": {"primary": "#2563eb", "secondary": "#1a202c", "accent": "#f59e0b"}
    }
    
    result = generate_site_local(config)
    
    assert result["success"] == True, "Generation failed"
    assert result["page_count"] >= 2, "Should have 2+ pages"
    assert len(result["pages"]) > 0, "Should have pages"
    
    for page in result["pages"]:
        assert "html" in page, "Page should have HTML"
        assert len(page["html"]) > 100, "HTML should be substantial"
        assert "<html" in page["html"].lower(), "Should have HTML structure"
    
    print(f"   ✅ Generated {result['page_count']} pages successfully")
    print(f"   ✅ Site type: {result['site_type']}")
    print(f"   ✅ Total HTML size: {sum(len(p['html']) for p in result['pages'])} bytes")
    return True

def test_design_engine():
    """Test design analysis"""
    print("\n🧪 Testing design_engine.py...")
    from design_engine import get_design_suggestions, check_accessibility
    
    config = {
        "colors": {"primary": "#2563eb", "secondary": "#1a202c", "accent": "#f59e0b"},
        "vibe": "modern"
    }
    
    # Test design suggestions
    suggestions = get_design_suggestions(config)
    assert "suggestions" in suggestions or "dark_mode" in suggestions, "Should have design suggestions"
    print(f"   ✅ Design suggestions generated ({len(suggestions)} properties)")
    
    # Test accessibility checker
    html_sample = """
    <html>
      <head><title>Test Page</title></head>
      <body>
        <h1>Main Heading</h1>
        <p>Content here</p>
        <img src="test.jpg" alt="Test image">
      </body>
    </html>
    """
    
    accessibility = check_accessibility(html_sample)
    assert "score" in accessibility, "Should have accessibility score"
    assert 0 <= accessibility["score"] <= 100, "Score should be 0-100"
    print(f"   ✅ Accessibility score: {accessibility['score']}/100")
    
    return True

def test_seo_engine():
    """Test SEO optimization"""
    print("\n🧪 Testing seo_engine.py...")
    from seo_engine import optimize_html_seo, analyze_seo, generate_sitemap, generate_robots_txt_content
    
    html = "<html><head></head><body><h1>Test</h1><p>Content</p></body></html>"
    config = {"brand": "Test", "site_type": "blog"}
    
    # Test SEO optimization
    optimized = optimize_html_seo(html, config)
    assert "<meta" in optimized, "Should have meta tags"
    assert "og:" in optimized, "Should have Open Graph"
    print(f"   ✅ SEO optimization applied")
    
    # Test SEO analysis
    analysis = analyze_seo(html, config)
    assert "score" in analysis, "Should have SEO score"
    assert 0 <= analysis["score"] <= 100, "Score should be 0-100"
    print(f"   ✅ SEO score: {analysis['score']}/100")
    
    # Test sitemap generation
    pages = [{"filename": "index.html"}, {"filename": "about.html"}]
    sitemap = generate_sitemap(pages)
    assert "<?xml" in sitemap, "Should be valid XML"
    assert "sitemap" in sitemap.lower(), "Should have sitemap tags"
    print(f"   ✅ Sitemap generated (XML)")
    
    # Test robots.txt
    robots = generate_robots_txt_content()
    assert "User-agent" in robots, "Should have User-agent"
    assert "Disallow" in robots or "Allow" in robots, "Should have directives"
    print(f"   ✅ robots.txt generated")
    
    return True

def test_component_exporter():
    """Test component exports"""
    print("\n🧪 Testing component_exporter.py...")
    from component_exporter import export_to_react, export_to_vue, export_to_typescript, export_to_nextjs
    
    html = "<div class='container'><h1>Test</h1><p>Content</p></div>"
    config = {"brand": "Test", "site_type": "blog"}
    
    # Test React export
    react_code = export_to_react(html, "TestComponent")
    assert "import React" in react_code, "Should have React import"
    assert "className" in react_code, "Should convert class to className"
    assert "export default" in react_code, "Should have export"
    print(f"   ✅ React export ({len(react_code)} bytes)")
    
    # Test Vue export
    vue_code = export_to_vue(html, "TestComponent")
    assert "<template>" in vue_code, "Should have Vue template"
    assert "<script" in vue_code, "Should have script"
    assert "<style scoped>" in vue_code, "Should have scoped styles"
    print(f"   ✅ Vue export ({len(vue_code)} bytes)")
    
    # Test TypeScript export
    ts_code = export_to_typescript(config)
    assert "interface SiteConfig" in ts_code, "Should have interfaces"
    assert "export const" in ts_code, "Should export constants"
    print(f"   ✅ TypeScript export ({len(ts_code)} bytes)")
    
    # Test Next.js export
    pages = [{"name": "Home", "html": html}]
    nextjs_files = export_to_nextjs(pages, config)
    assert "app/layout.tsx" in nextjs_files, "Should have layout"
    assert "app/api/generate/route.ts" in nextjs_files, "Should have API route"
    print(f"   ✅ Next.js export ({len(nextjs_files)} files)")
    
    return True

def test_integration():
    """Test full integration"""
    print("\n🧪 Testing Full Integration...")
    from local_engine import generate_site_local
    from design_engine import get_design_suggestions, check_accessibility
    from seo_engine import optimize_html_seo, analyze_seo
    from component_exporter import export_to_react
    
    config = {
        "brand": "Full Test",
        "tagline": "Integration test",
        "site_type": "saas",
        "pages": ["home", "pricing"],
        "sections": ["hero", "features", "pricing", "cta"],
        "colors": {"primary": "#3b82f6", "secondary": "#1e293b", "accent": "#fbbf24"}
    }
    
    # Generate site
    result = generate_site_local(config)
    assert result["success"], "Should generate successfully"
    
    # Get first page
    first_page = result["pages"][0]["html"]
    
    # Optimize for SEO
    optimized = optimize_html_seo(first_page, config)
    
    # Check accessibility
    a11y = check_accessibility(optimized)
    
    # Export to React
    react_component = export_to_react(optimized, "SaaSWebsite")
    
    # Get design suggestions
    design = get_design_suggestions(config)
    
    print(f"   ✅ Generated: {result['page_count']} pages")
    print(f"   ✅ SEO optimized: {len(optimized)} bytes")
    print(f"   ✅ Accessibility score: {a11y.get('score', 'N/A')}/100")
    print(f"   ✅ Exported to React: {len(react_component)} bytes")
    print(f"   ✅ Design suggestions: {len(design)} properties")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Promptrix v2.0 - Phase 1 Validation")
    print("=" * 60)
    
    tests = [
        ("Local Engine", test_local_engine),
        ("Design Engine", test_design_engine),
        ("SEO Engine", test_seo_engine),
        ("Component Exporter", test_component_exporter),
        ("Full Integration", test_integration),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED! Phase 1 is ready.")
        print("\n🎯 Next: Run 'python app_v2.py' to start the server")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

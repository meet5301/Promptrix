
const templates = [
  {name:"Modern Business",icon:"💼"},{name:"Creative Agency",icon:"🎨"},{name:"E-Commerce",icon:"🛍️"},{name:"SaaS Landing",icon:"⚡"},
  {name:"Portfolio",icon:"👨‍💼"},{name:"Blog Hub",icon:"📝"},{name:"Minimal",icon:"⚪"},{name:"Dark Elegant",icon:"🌙"},
  {name:"Restaurant",icon:"🍽️"},{name:"Gym",icon:"💪"},{name:"Real Estate",icon:"🏠"},{name:"Travel",icon:"✈️"},
  {name:"Education",icon:"🎓"},{name:"Health",icon:"🏥"},{name:"Hotel",icon:"🏨"},{name:"Fashion",icon:"👗"},
  {name:"Photography",icon:"📸"},{name:"Music",icon:"🎵"},{name:"Sports",icon:"⚽"},{name:"Wedding",icon:"💒"},
  {name:"Tech Startup",icon:"💻"},{name:"Legal",icon:"⚖️"},{name:"Dental",icon:"🦷"},{name:"Auto",icon:"🚗"},
  {name:"Coffee Shop",icon:"☕"},{name:"Salon",icon:"💆"},{name:"Freelance",icon:"👩‍💻"},{name:"Charity",icon:"❤️"},
  {name:"App Landing",icon:"📱"},{name:"Conference",icon:"🎤"},{name:"Books",icon:"📚"},{name:"Pet Care",icon:"🐕"},
  {name:"Gaming",icon:"🎮"},{name:"Construction",icon:"🏗️"},{name:"Consulting",icon:"💡"},{name:"Church",icon:"⛪"},
  {name:"Cybersecurity",icon:"🔒"},{name:"Marketing",icon:"📊"},{name:"Logistics",icon:"📦"},{name:"Insurance",icon:"🛡️"},
  {name:"Video",icon:"🎬"},{name:"Design",icon:"✏️"},{name:"Crypto",icon:"₿"},{name:"AI",icon:"🤖"},
  {name:"Energy",icon:"⚡"},{name:"Furniture",icon:"🪑"},{name:"Accounting",icon:"📈"},{name:"HR",icon:"👥"},
  {name:"Eco",icon:"🌿"},{name:"Luxury",icon:"👑"},{name:"Social",icon:"🔗"},{name:"NGO",icon:"🎗️"}
];

let selectedTemplate = null, customizationData = {};
let currentHTML = '';

function init() {
  const grid = document.getElementById('templates-grid');
  grid.innerHTML = templates.map((t,i) => `
    <div class="template-card">
      <div class="template-preview-img">${t.icon}</div>
      <div class="template-info">
        <div class="template-name">${t.name}</div>
        <div class="template-desc">Professional template</div>
        <div class="template-btns">
          <button class="btn-custom" onclick="startCustomize(${i})">Customize</button>
          <button class="btn-prev" onclick="previewTemplate(${i})">Preview</button>
        </div>
      </div>
    </div>
  `).join('');
}

function previewTemplate(idx) {
  const template = templates[idx];
  const html = `<!DOCTYPE html><html><head><title>${template.name}</title><style>body{margin:0;font-family:sans-serif;background:linear-gradient(135deg,#d4540a,#0a7070);padding:40px;text-align:center;color:#fff}h1{font-size:48px;margin:0}p{font-size:20px;margin:20px 0}.icon{font-size:80px}</style></head><body><div class="icon">${template.icon}</div><h1>${template.name}</h1><p>Professional Template Preview</p><p>Click Customize to personalize this template</p></body></html>`;
  document.getElementById('preview-iframe').srcdoc = html;
  document.getElementById('preview-modal').classList.add('show');
}

function closePreview() {
  document.getElementById('preview-modal').classList.remove('show');
}

function startCustomize(idx) {
  selectedTemplate = idx;
  document.getElementById('customize-panel').classList.add('active');
  closePreview();
}

function closeCustomize() {
  document.getElementById('customize-panel').classList.remove('active');
  document.getElementById('code-preview').classList.remove('show');
}

function switchTab(idx) {
  document.querySelectorAll('.tab-btn').forEach((t,i) => t.classList.toggle('active', i===idx));
  document.querySelectorAll('.tab-content').forEach((c,i) => c.classList.toggle('active', i===idx));
}

function toggle(btn, key, val) {
  btn.parentElement.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  customizationData[key] = val;
}

function changeValue(id,delta) {
  const inp = document.getElementById(id);
  const min = parseInt(inp.getAttribute('min')||1);
  const max = parseInt(inp.getAttribute('max')||99);
  const v = Math.max(min, Math.min(max, parseInt(inp.value)+delta));
  inp.value = v;
}

function generateSite() {
  const config = {
    template: templates[selectedTemplate]?.name || 'Custom',
    brandName: document.getElementById('brand-name').value,
    tagline: document.getElementById('brand-tagline').value,
    company: document.getElementById('company-name').value,
    menuCount: parseInt(document.getElementById('menu-count').value)||5,
    heroTitle: document.getElementById('hero-title').value,
    heroSubtitle: document.getElementById('hero-subtitle').value,
    ctaText: document.getElementById('cta-text').value,
    sectionsCount: parseInt(document.getElementById('sections-count').value)||3,
    totalPages: parseInt(document.getElementById('total-pages').value)||5,
    colors: {primary:document.getElementById('color-primary').value,secondary:document.getElementById('color-secondary').value,accent:document.getElementById('color-accent').value},
    seo: {title:document.getElementById('seo-title').value,description:document.getElementById('seo-description').value}
  };

  const p = config.colors.primary, s = config.colors.secondary, a = config.colors.accent;
  
  currentHTML = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${config.seo.title}</title>
  <meta name="description" content="${config.seo.description}">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    :root { --primary: ${p}; --secondary: ${s}; --accent: ${a}; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: #fff; color: #1a1512; line-height: 1.6; }
    header { background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; padding: 20px 0; position: sticky; top: 0; z-index: 100; }
    .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
    h1 { font-size: 2.5rem; color: var(--primary); }
    h2 { font-size: 2rem; margin: 20px 0; }
    .hero { background: linear-gradient(135deg, var(--primary)20, var(--accent)20); padding: 80px 0; text-align: center; }
    .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 40px 0; }
    .feature-card { background: #f5f5f5; padding: 30px; border-radius: 10px; text-align: center; }
    .feature-card:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    .btn { background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; padding: 12px 28px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
    footer { background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; padding: 40px 0; margin-top: 60px; text-align: center; }
    @media (max-width: 768px) { h1 { font-size: 2rem; } .features { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <div class="container">
      <h3 style="margin:0">${config.brandName}</h3>
      <small>${config.tagline}</small>
      <nav style="display:flex;gap:20px;margin-top:15px">
        ${Array.from({length:config.menuCount},(_,i)=>`<a href="#" style="color:white">${i+1}</a>`).join('')}
      </nav>
    </div>
  </header>

  <section class="hero">
    <div class="container">
      <h1>${config.heroTitle}</h1>
      <p style="font-size:1.2rem">${config.heroSubtitle}</p>
      <button class="btn">${config.ctaText}</button>
    </div>
  </section>

  <section style="padding:60px 0">
    <div class="container">
      <h2>Features</h2>
      <div class="features">
        ${Array.from({length:config.sectionsCount},(_,i)=>`<div class="feature-card"><h3>Feature ${i+1}</h3><p>Your amazing feature description</p></div>`).join('')}
      </div>
    </div>
  </section>

  <footer>
    <div class="container">
      <p>&copy; 2026 ${config.company}. All rights reserved.</p>
      <p style="font-size:12px;opacity:0.8;margin-top:10px">Made with ❤️ by Promptrix</p>
    </div>
  </footer>
</body>
</html>`;

  document.getElementById('code-content').textContent = currentHTML;
  document.getElementById('code-preview').classList.add('show');
  setTimeout(() => document.getElementById('code-preview').scrollIntoView({behavior:'smooth'}), 300);
}

function copyCode() {
  navigator.clipboard.writeText(currentHTML);
  alert('✓ Code copied!');
}

function downloadCode() {
  const el = document.createElement('a');
  el.href = 'data:text/html;charset=utf-8,' + encodeURIComponent(currentHTML);
  el.download = 'website.html';
  el.click();
}

window.addEventListener('load', init);


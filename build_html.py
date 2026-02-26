import markdown
import os

BASE = "/home/user/ubermensch"
OUT = os.path.join(BASE, "output")

STYLE = """
  * { box-sizing: border-box; }
  body { max-width: 960px; margin: 40px auto; padding: 0 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; color: #24292e; background: #fff; }
  h1 { border-bottom: 2px solid #0366d6; padding-bottom: 10px; }
  h2 { border-bottom: 1px solid #eaecef; padding-bottom: 8px; margin-top: 40px; }
  h3 { margin-top: 30px; }
  a { color: #0366d6; text-decoration: none; }
  a:hover { text-decoration: underline; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  th, td { border: 1px solid #dfe2e5; padding: 8px 13px; text-align: left; }
  th { background: #f6f8fa; font-weight: 600; }
  tr:nth-child(even) { background: #f6f8fa; }
  code { background: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-size: 85%; }
  pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }
  pre code { background: none; padding: 0; }
  blockquote { border-left: 4px solid #dfe2e5; margin: 0; padding: 0 16px; color: #6a737d; }
  ul { padding-left: 2em; }
  li { margin: 4px 0; }
  img { max-width: 100%; }

  /* Tab navigation */
  .tabs { display: flex; gap: 0; border-bottom: 2px solid #0366d6; margin-bottom: 30px; position: sticky; top: 0; background: #fff; z-index: 10; padding-top: 10px; }
  .tab-btn { padding: 10px 24px; border: none; background: #f6f8fa; cursor: pointer; font-size: 15px; font-weight: 600; color: #586069; border-radius: 6px 6px 0 0; margin-right: 2px; transition: all 0.2s; }
  .tab-btn:hover { background: #e1e4e8; color: #24292e; }
  .tab-btn.active { background: #0366d6; color: #fff; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* Back to top */
  .top-btn { position: fixed; bottom: 30px; right: 30px; background: #0366d6; color: #fff; border: none; border-radius: 50%; width: 48px; height: 48px; font-size: 22px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.2); display: none; z-index: 99; }
  .top-btn:hover { background: #0256b9; }

  @media print { .tabs, .top-btn { display: none !important; } .tab-content { display: block !important; page-break-before: always; } }
"""

SINGLE_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ubermensch - 금융공기업 NCS &amp; Web Agents</title>
<style>{style}</style>
</head>
<body>

<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('home')">HOME</button>
  <button class="tab-btn" onclick="switchTab('ncs')">NCS 기출문제</button>
  <button class="tab-btn" onclick="switchTab('agents')">Web Agents</button>
</div>

<div id="tab-home" class="tab-content active">{home}</div>
<div id="tab-ncs" class="tab-content">{ncs}</div>
<div id="tab-agents" class="tab-content">{agents}</div>

<button class="top-btn" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&#8593;</button>

<script>
function switchTab(id) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  event.target.classList.add('active');
  window.scrollTo({{top: 0}});
}}
window.addEventListener('scroll', function() {{
  document.querySelector('.top-btn').style.display = window.scrollY > 400 ? 'block' : 'none';
}});
</script>
</body>
</html>"""

# Also keep individual page template
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{style}</style>
</head>
<body>
<div class="tabs">
  <a class="tab-btn" href="index.html">HOME</a>
  <a class="tab-btn" href="ncs-financial-exams.html">NCS 기출문제</a>
  <a class="tab-btn" href="web-agents.html">Web Agents</a>
</div>
{content}
<button class="top-btn" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&#8593;</button>
<script>
window.addEventListener('scroll', function() {{
  document.querySelector('.top-btn').style.display = window.scrollY > 400 ? 'block' : 'none';
}});
</script>
</body>
</html>"""

files = [
    ("README.md", "index.html", "Ubermensch - 리소스 허브"),
    ("ncs/financial-exams.md", "ncs-financial-exams.html", "금융공기업 NCS 기출문제 모음"),
    ("web-agents/README.md", "web-agents.html", "Awesome Web Agents"),
]

md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
converted = {}

# Build individual pages + collect content
for src, dst, title in files:
    with open(os.path.join(BASE, src), "r") as f:
        content = f.read()
    html_content = md.convert(content)
    md.reset()
    converted[dst] = html_content

    dst_path = os.path.join(OUT, dst)
    with open(dst_path, "w") as f:
        f.write(PAGE_TEMPLATE.format(title=title, content=html_content, style=STYLE))
    print(f"  {dst_path}")

# Build single all-in-one file
single_path = os.path.join(OUT, "ubermensch-all.html")
with open(single_path, "w") as f:
    f.write(SINGLE_PAGE_TEMPLATE.format(
        style=STYLE,
        home=converted["index.html"],
        ncs=converted["ncs-financial-exams.html"],
        agents=converted["web-agents.html"],
    ))
print(f"  {single_path}")

print(f"\nDone! Open ubermensch-all.html in your browser.")

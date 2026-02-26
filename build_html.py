import markdown
import os

TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{ max-width: 900px; margin: 40px auto; padding: 0 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; color: #24292e; background: #fff; }}
  h1 {{ border-bottom: 1px solid #eaecef; padding-bottom: 10px; }}
  h2 {{ border-bottom: 1px solid #eaecef; padding-bottom: 8px; margin-top: 40px; }}
  h3 {{ margin-top: 30px; }}
  a {{ color: #0366d6; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th, td {{ border: 1px solid #dfe2e5; padding: 8px 13px; text-align: left; }}
  th {{ background: #f6f8fa; font-weight: 600; }}
  tr:nth-child(even) {{ background: #f6f8fa; }}
  code {{ background: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-size: 85%; }}
  pre {{ background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{ border-left: 4px solid #dfe2e5; margin: 0; padding: 0 16px; color: #6a737d; }}
  ul {{ padding-left: 2em; }}
  li {{ margin: 4px 0; }}
  img {{ max-width: 100%; }}
  .nav {{ background: #f6f8fa; padding: 12px 20px; border-radius: 6px; margin-bottom: 30px; }}
  .nav a {{ margin-right: 20px; font-weight: 600; }}
</style>
</head>
<body>
<div class="nav">
  <a href="index.html">HOME</a>
  <a href="ncs-financial-exams.html">NCS 기출문제</a>
  <a href="web-agents.html">Web Agents</a>
</div>
{content}
</body>
</html>"""

files = [
    ("README.md", "index.html", "Ubermensch - 리소스 허브"),
    ("ncs/financial-exams.md", "ncs-financial-exams.html", "금융공기업 NCS 기출문제 모음"),
    ("web-agents/README.md", "web-agents.html", "Awesome Web Agents"),
]

md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])

for src, dst, title in files:
    src_path = os.path.join("/home/user/ubermensch", src)
    dst_path = os.path.join("/home/user/ubermensch/output", dst)
    with open(src_path, "r") as f:
        content = f.read()
    html_content = md.convert(content)
    md.reset()
    with open(dst_path, "w") as f:
        f.write(TEMPLATE.format(title=title, content=html_content))
    print(f"  {dst_path}")

print("\nDone!")

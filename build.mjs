#!/usr/bin/env node
// build.mjs — inline every linked CSS and JS file into a single shareable HTML.
// Usage: node build.mjs [outPath]
//   default outPath: dist/artifact.html

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const srcPath = path.join(root, 'index.html');
const outPath = path.resolve(root, process.argv[2] || 'dist/artifact.html');

const html = fs.readFileSync(srcPath, 'utf8');

// Match any <link> element. We then check attributes inside the captured tag
// instead of fixing their order in the regex itself.
const linkTagRe = /<link\b([^>]*)\/?>/gi;
// Match any <script ... src="..."></script> element. defer / type / etc may appear in any order.
const scriptTagRe = /<script\b([^>]*)>\s*<\/script>/gi;

const attrRe = (name) => new RegExp(`\\b${name}\\s*=\\s*["']([^"']+)["']`, 'i');

function isStylesheetLink(attrs) {
  const m = attrs.match(attrRe('rel'));
  return !!m && m[1].toLowerCase().includes('stylesheet');
}

function getAttr(attrs, name) {
  const m = attrs.match(attrRe(name));
  return m ? m[1] : null;
}

// Prevent inlined CSS/JS from prematurely terminating its wrapping tag.
// </style> and </script> are the only sequences that can do this. Use a
// safe textual replacement that browsers parse identically.
function safeForStyle(css) {
  return css.replace(/<\/(style)/gi, '<\\/$1');
}
function safeForScript(js) {
  return js.replace(/<\/(script)/gi, '<\\/$1');
}

let inlinedCss = 0, inlinedJs = 0;
const errors = [];

const withCss = html.replace(linkTagRe, (full, attrs) => {
  if (!isStylesheetLink(attrs)) return full;
  const href = getAttr(attrs, 'href');
  if (!href) return full;
  const absPath = path.join(root, href);
  let css;
  try {
    css = fs.readFileSync(absPath, 'utf8');
  } catch (e) {
    errors.push(`missing CSS: ${href}`);
    return full;
  }
  inlinedCss++;
  return `<style data-from="${href}">\n${safeForStyle(css)}\n</style>`;
});

const withAll = withCss.replace(scriptTagRe, (full, attrs) => {
  const src = getAttr(attrs, 'src');
  if (!src) return full; // inline scripts pass through untouched
  const absPath = path.join(root, src);
  let js;
  try {
    js = fs.readFileSync(absPath, 'utf8');
  } catch (e) {
    errors.push(`missing JS: ${src}`);
    return full;
  }
  inlinedJs++;
  return `<script data-from="${src}">\n${safeForScript(js)}\n</script>`;
});

if (errors.length) {
  console.error('✗ build failed:\n  ' + errors.join('\n  '));
  process.exit(1);
}

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, withAll);

const bytes = Buffer.byteLength(withAll);
const kb = (bytes / 1024).toFixed(1);
console.log(`✓ ${path.relative(root, outPath)}  (${inlinedCss} css, ${inlinedJs} js, ${kb} KB)`);

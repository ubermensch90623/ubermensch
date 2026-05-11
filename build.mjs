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

const cssRe = /<link\s+rel=["']stylesheet["']\s+href=["']([^"']+)["']\s*\/?>\s*/g;
const jsRe  = /<script\s+defer\s+src=["']([^"']+)["']><\/script>\s*/g;

let inlinedCss = 0, inlinedJs = 0;

const withCss = html.replace(cssRe, (_match, href) => {
  const css = fs.readFileSync(path.join(root, href), 'utf8');
  inlinedCss++;
  return `<style data-from="${href}">\n${css}\n</style>\n`;
});

const withAll = withCss.replace(jsRe, (_match, src) => {
  const js = fs.readFileSync(path.join(root, src), 'utf8');
  inlinedJs++;
  return `<script data-from="${src}">\n${js}\n</script>\n`;
});

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, withAll);

const bytes = Buffer.byteLength(withAll);
const kb = (bytes / 1024).toFixed(1);
console.log(`✓ ${path.relative(root, outPath)}  (${inlinedCss} css, ${inlinedJs} js, ${kb} KB)`);

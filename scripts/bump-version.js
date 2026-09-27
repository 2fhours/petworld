#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const indexPath = process.argv[2]
  ? path.resolve(process.cwd(), process.argv[2])
  : path.resolve(__dirname, '..', 'index.html');
const source = fs.readFileSync(indexPath, 'utf8');
const pattern = /(const APP_VERSION\s*=\s*)(\d+)(\s*;)/g;
const matches = [...source.matchAll(pattern)];
if (matches.length !== 1) {
  throw new Error(`Expected exactly one numeric APP_VERSION in ${indexPath}; found ${matches.length}`);
}
const current = Number(matches[0][2]);
const next = current + 1;
const updated = source.replace(pattern, (_, prefix, value, suffix) => `${prefix}${Number(value) + 1}${suffix}`);
fs.writeFileSync(indexPath, updated);
console.log(`APP_VERSION ${current} -> ${next}`);

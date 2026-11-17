#!/usr/bin/env node
/**
 * check-locales.mjs — locale parity and link checks for the VitePress course.
 *
 * Verifies:
 *   1. Every course page under docs/ has a Portuguese counterpart under docs/pt-BR/.
 *   2. Internal links on every page (markdown + frontmatter) resolve to an
 *      existing page within the SAME locale.
 *   3. Portuguese pages link to course pages with the `/pt-BR/` prefix.
 *
 * Run: npm run check:i18n
 */

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const DOCS = path.join(ROOT, 'docs')
const PT = path.join(DOCS, 'pt-BR')

const EXCLUDE_DIRS = new Set(['.vitepress', 'pt-BR', 'public'])
const COURSE_ROOTS = ['/lectures', '/projects', '/resources', '/skills', '/harness-designs', '/reference']

let failures = 0
let checks = 0

function fail(message) {
  failures++
  console.error(`  FAIL ${message}`)
}

function walk(dir) {
  const out = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.') || EXCLUDE_DIRS.has(entry.name)) continue
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) out.push(...walk(full))
    else if (entry.name.endsWith('.md')) out.push(full)
  }
  return out
}

function rel(p) {
  return path.relative(ROOT, p)
}

function resolveTarget(file, target, localeDir) {
  const clean = target.split(/[?#]/)[0]
  if (!clean || clean.startsWith('http://') || clean.startsWith('https://') || clean.startsWith('mailto:') || clean.startsWith('#')) return null
  if (clean.startsWith('/')) {
    if (clean === '/') return path.join(localeDir, 'index.md')
    let rest = clean.replace(/^\/pt-BR/, '')
    rest = rest.replace(/^\/+/, '')
    return path.join(localeDir, rest.endsWith('/') ? `${rest}index.md` : `${rest}.md`)
  }
  return path.join(path.dirname(file), clean.endsWith('/') ? `${clean}index.md` : `${clean}.md`)
}

function checkLinks(file, localeDir) {
  const src = fs.readFileSync(file, 'utf8')
  const links = new Set()
  for (const m of src.matchAll(/\]\(([^)\s]+)\)/g)) links.add(m[1])
  for (const m of src.matchAll(/^\s*link:\s*([^\s]+)/gm)) links.add(m[1])
  for (const target of links) {
    if (/\.(png|jpe?g|gif|svg|webp|css|js|pdf|zip|woff2?)$/i.test(target)) continue
    if (target.startsWith('/wm-')) continue
    // A static page served from docs/public, such as a demo.
    if (target.startsWith('/') && fs.existsSync(path.join(DOCS, 'public', target))) {
      checks++
      continue
    }
    if (target.startsWith('https://') || target.startsWith('http://')) continue
    if (target.startsWith('/pt-BR') && localeDir === DOCS) {
      fail(`${rel(file)}: PT link on an English page: ${target}`)
      continue
    }
    if (localeDir === PT) {
      const isCourse = COURSE_ROOTS.some((root) => target === root || target.startsWith(`${root}/`)) || target === '/'
      if (isCourse && !target.startsWith('/pt-BR/')) {
        fail(`${rel(file)}: internal link not prefixed for the pt-BR locale: ${target}`)
        continue
      }
    }
    const resolved = resolveTarget(file, target, localeDir)
    if (!resolved) continue
    checks++
    if (!fs.existsSync(resolved)) {
      fail(`${rel(file)}: broken link → ${target} (missing ${rel(resolved)})`)
    }
  }
}

console.log('== 1. Page parity (docs/ ↔ docs/pt-BR/) ==')
const enPages = walk(DOCS)
let parityOk = 0
for (const file of enPages) {
  const ptFile = path.join(PT, path.relative(DOCS, file))
  checks++
  if (!fs.existsSync(ptFile)) {
    fail(`${rel(file)}: no pt-BR counterpart at ${rel(ptFile)}`)
  } else {
    parityOk++
  }
}
console.log(`  ${parityOk}/${enPages.length} pages have a pt-BR counterpart`)

console.log('== 2. Internal links per locale ==')
for (const file of [...enPages, ...walk(PT)]) {
  const localeDir = file.startsWith(`${PT}/`) ? PT : DOCS
  checkLinks(file, localeDir)
}

console.log(`\n${checks} link checks, ${failures} failure(s)`)
if (failures > 0) {
  process.exit(1)
}
console.log('OK — locale parity and links are consistent')

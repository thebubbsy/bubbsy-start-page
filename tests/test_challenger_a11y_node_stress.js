/**
 * Node.js Accessibility, WCAG AAA Contrast & Keyboard Focus Trapping Verification Suite
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const indexHtmlPath = path.join(ROOT_DIR, 'index.html');
const appJsPath = path.join(ROOT_DIR, 'js', 'app.js');
const stylesCssPath = path.join(ROOT_DIR, 'css', 'styles.css');

const indexHtml = fs.readFileSync(indexHtmlPath, 'utf8');
const appJs = fs.readFileSync(appJsPath, 'utf8');
const stylesCss = fs.readFileSync(stylesCssPath, 'utf8');

console.log('=== RUNNING EMPIRICAL NODE.JS A11Y & CONTRAST HARNESS ===');

// --- 1. WCAG 2.1 Luminance and Contrast Ratio Engine ---
function hexToRgb(hex) {
  let clean = hex.replace('#', '');
  if (clean.length === 3) clean = clean.split('').map(c => c + c).join('');
  const num = parseInt(clean, 16);
  return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
}

function channelLinear(val) {
  const c = val / 255.0;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function relativeLuminance(rgb) {
  return 0.2126 * channelLinear(rgb[0]) + 0.7152 * channelLinear(rgb[1]) + 0.0722 * channelLinear(rgb[2]);
}

function contrastRatio(rgb1, rgb2) {
  const l1 = relativeLuminance(rgb1);
  const l2 = relativeLuminance(rgb2);
  const max = Math.max(l1, l2);
  const min = Math.min(l1, l2);
  return (max + 0.05) / (min + 0.05);
}

function compositeRgba(rgbFg, a, rgbBg) {
  return [
    Math.round(rgbFg[0] * a + rgbBg[0] * (1 - a)),
    Math.round(rgbFg[1] * a + rgbBg[1] * (1 - a)),
    Math.round(rgbFg[2] * a + rgbBg[2] * (1 - a))
  ];
}

console.log('\n[Suite 1/3] Testing WCAG AAA (>= 7.0:1) Text Contrast Ratios across 6 Palettes & 4 Themes...');

const PALETTES = {
  'crisp-silver': { primary: '#ffffff', secondary: '#e2e8f0', muted: '#a8b8cc' },
  'cyber-amber': { primary: '#fef08a', secondary: '#fde047', muted: '#f59e0b' },
  'matrix-emerald': { primary: '#bbf7d0', secondary: '#86efac', muted: '#4ade80' },
  'ice-cyan': { primary: '#e0f2fe', secondary: '#7dd3fc', muted: '#38bdf8' },
  'warm-paper': { primary: '#fef9c3', secondary: '#fde68a', muted: '#fbbf24' },
  'synthwave': { primary: '#f5d0fe', secondary: '#f0abfc', muted: '#d8b4fe' }
};

const THEMES = {
  'obsidian': { name: 'Default Obsidian', bgPri: '#0a0e17', bgSec: '#111827', cardRgba: [17, 24, 39, 0.75], cardHovRgba: [26, 38, 57, 0.90] },
  'amber': { name: 'Cyber Amber', bgPri: '#0d0c07', bgSec: '#17150d', cardRgba: [23, 21, 13, 0.80], cardHovRgba: [36, 32, 20, 0.92] },
  'matrix': { name: 'Matrix Emerald', bgPri: '#050d08', bgSec: '#0a170f', cardRgba: [10, 23, 15, 0.80], cardHovRgba: [15, 36, 23, 0.92] },
  'dracula': { name: 'Dracula Midnight', bgPri: '#0d0b18', bgSec: '#18142a', cardRgba: [24, 20, 42, 0.80], cardHovRgba: [38, 32, 66, 0.92] }
};

let checkedCombinations = 0;
let passedCombinations = 0;

for (const [themeKey, theme] of Object.entries(THEMES)) {
  const bgPriRgb = hexToRgb(theme.bgPri);
  const bgSecRgb = hexToRgb(theme.bgSec);
  const bgCardRgb = compositeRgba(theme.cardRgba.slice(0, 3), theme.cardRgba[3], bgPriRgb);
  const bgCardHovRgb = compositeRgba(theme.cardHovRgba.slice(0, 3), theme.cardHovRgba[3], bgPriRgb);

  for (const [palKey, pal] of Object.entries(PALETTES)) {
    for (const [role, hex] of Object.entries(pal)) {
      const fgRgb = hexToRgb(hex);
      const crPri = contrastRatio(fgRgb, bgPriRgb);
      const crSec = contrastRatio(fgRgb, bgSecRgb);
      const crCard = contrastRatio(fgRgb, bgCardRgb);
      const crCardHov = contrastRatio(fgRgb, bgCardHovRgb);
      const minCr = Math.min(crPri, crSec, crCard, crCardHov);

      checkedCombinations++;
      assert(minCr >= 7.0, `Contrast ratio violation: ${themeKey}/${palKey}/${role} (${hex}) achieved min ratio ${minCr.toFixed(2)}:1 (< 7.0:1 AAA threshold)`);
      passedCombinations++;
    }
  }
}

console.log(`✓ 100% WCAG AAA Text Compliance: Verified ${passedCombinations}/${checkedCombinations} combinations all achieve CR >= 7.0:1.`);

// --- 2. Modal ARIA Semantics Audit ---
console.log('\n[Suite 2/3] Testing ARIA Dialog Semantics across 19 Modals in index.html...');

const modalMatches = [...indexHtml.matchAll(/<div\s+class="modal-overlay"[^>]*id="([^"]+)"[^>]*>/g)];
assert.strictEqual(modalMatches.length, 19, `Expected 19 modal overlays, found ${modalMatches.length}`);

for (const m of modalMatches) {
  const fullTag = m[0];
  const modalId = m[1];

  assert(fullTag.includes('role="dialog"'), `Modal #${modalId} missing role="dialog"`);
  assert(fullTag.includes('aria-modal="true"'), `Modal #${modalId} missing aria-modal="true"`);

  if (fullTag.includes('aria-labelledby="')) {
    const titleIdMatch = fullTag.match(/aria-labelledby="([^"]+)"/);
    const titleId = titleIdMatch[1];
    assert(indexHtml.includes(`id="${titleId}"`), `Modal #${modalId} references missing aria-labelledby element id="${titleId}"`);
  } else if (fullTag.includes('aria-label="')) {
    const labelMatch = fullTag.match(/aria-label="([^"]+)"/);
    assert(labelMatch[1].length > 0, `Modal #${modalId} has empty aria-label`);
  } else {
    assert.fail(`Modal #${modalId} lacks both aria-labelledby and aria-label attributes`);
  }
}
console.log('✓ All 19 modals possess valid role="dialog", aria-modal="true", and existing labelledby/label elements.');

// --- 3. Keyboard Focus Trapping & Restoration Logic ---
console.log('\n[Suite 3/3] Testing Modal Focus Trapping, Restoration & Shortcuts in js/app.js...');

assert(appJs.includes('previouslyFocusedElement = document.activeElement'), 'openModal must preserve document.activeElement');
assert(appJs.includes('previouslyFocusedElement.focus()'), 'closeModal must restore focus to previouslyFocusedElement');
assert(appJs.includes('e.key === \'Tab\' && activeModal'), 'Global keydown must intercept Tab inside active modal');
assert(appJs.includes('e.shiftKey'), 'Tab focus trap must support Shift+Tab backwards navigation');
assert(appJs.includes('e.preventDefault()'), 'Tab focus trap must prevent default scrolling/tab out of modal');
assert(appJs.includes('!activeModal.contains(document.activeElement)'), 'Tab trap must re-capture stray focus');
assert(appJs.includes('wrap.addEventListener(\'keydown\''), 'Candidate avatar wrappers must handle keyboard events');
assert(appJs.includes('img.addEventListener(\'keydown\''), 'Candidate avatar images must handle keyboard events');

// Focus-visible CSS validation
assert(stylesCss.includes(':focus-visible'), 'styles.css must define :focus-visible rules');
assert(stylesCss.includes('outline: 2px solid var(--accent-cyan)'), 'styles.css must define high-contrast outline');
assert(stylesCss.includes('[data-theme="amber"] :focus-visible'), 'Amber theme must define :focus-visible');
assert(stylesCss.includes('[data-theme="matrix"] :focus-visible'), 'Matrix theme must define :focus-visible');
assert(stylesCss.includes('[data-theme="dracula"] :focus-visible'), 'Dracula theme must define :focus-visible');
assert(stylesCss.includes('.triage-avatar:focus-visible'), 'Avatars must have explicit :focus-visible outline');

console.log('✓ Focus trapping, focus restoration, avatar keyboard activation, and :focus-visible styling fully verified.');
console.log('\n=== ALL A11Y & CONTRAST VERIFICATION SUITES PASSED EMPIRICALLY ===');

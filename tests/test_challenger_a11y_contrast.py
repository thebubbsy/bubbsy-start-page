#!/usr/bin/env python3
"""
Empirical WCAG 2.1 Contrast Ratio Verification Harness
Evaluates relative luminance and contrast ratios for all 6 typography palettes
across all 4 HUD themes (Default Obsidian, Cyber Amber, Matrix Emerald, Dracula Midnight).
Verifies primary, secondary, and muted text colors against body, card, and secondary backgrounds.
"""

import sys
import math

# WCAG 2.1 relative luminance calculation
def hex_to_rgb(hex_str):
    hex_str = hex_str.strip().lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c * 2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgba_to_rgb(r, g, b, a, bg_r, bg_g, bg_b):
    """Composite RGBA over solid RGB background"""
    out_r = round(r * a + bg_r * (1 - a))
    out_g = round(g * a + bg_g * (1 - a))
    out_b = round(b * a + bg_b * (1 - a))
    return (out_r, out_g, out_b)

def channel_linear(c_srgb_255):
    c = c_srgb_255 / 255.0
    if c <= 0.04045:
        return c / 12.92
    else:
        return math.pow((c + 0.055) / 1.055, 2.4)

def relative_luminance(rgb):
    r_lin = channel_linear(rgb[0])
    g_lin = channel_linear(rgb[1])
    b_lin = channel_linear(rgb[2])
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

def contrast_ratio(rgb1, rgb2):
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

# Palettes defined in js/app.js & css/styles.css
PALETTES = {
    'crisp-silver': {
        'name': 'Crisp Silver / White',
        'primary': '#ffffff',
        'secondary': '#e2e8f0',
        'muted': '#a8b8cc'
    },
    'cyber-amber': {
        'name': 'Cyber Amber',
        'primary': '#fef08a',
        'secondary': '#fde047',
        'muted': '#f59e0b'
    },
    'matrix-emerald': {
        'name': 'Matrix Emerald',
        'primary': '#bbf7d0',
        'secondary': '#86efac',
        'muted': '#4ade80'
    },
    'ice-cyan': {
        'name': 'Ice Cyber Cyan',
        'primary': '#e0f2fe',
        'secondary': '#7dd3fc',
        'muted': '#38bdf8'
    },
    'warm-paper': {
        'name': 'Solarized Cream',
        'primary': '#fef9c3',
        'secondary': '#fde68a',
        'muted': '#fbbf24'
    },
    'synthwave': {
        'name': 'Synthwave Pink',
        'primary': '#f5d0fe',
        'secondary': '#f0abfc',
        'muted': '#d8b4fe'
    }
}

# 4 Themes
THEMES = {
    'obsidian': {
        'name': 'Default Obsidian',
        'bg_primary': '#0a0e17',
        'bg_secondary': '#111827',
        'bg_card_rgba': (17, 24, 39, 0.75),
        'bg_card_hover_rgba': (26, 38, 57, 0.90)
    },
    'amber': {
        'name': 'Cyberpunk Amber',
        'bg_primary': '#0d0c07',
        'bg_secondary': '#17150d',
        'bg_card_rgba': (23, 21, 13, 0.80),
        'bg_card_hover_rgba': (36, 32, 20, 0.92)
    },
    'matrix': {
        'name': 'Matrix Emerald',
        'bg_primary': '#050d08',
        'bg_secondary': '#0a170f',
        'bg_card_rgba': (10, 23, 15, 0.80),
        'bg_card_hover_rgba': (15, 36, 23, 0.92)
    },
    'dracula': {
        'name': 'Dracula Midnight',
        'bg_primary': '#0d0b18',
        'bg_secondary': '#18142a',
        'bg_card_rgba': (24, 20, 42, 0.80),
        'bg_card_hover_rgba': (38, 32, 66, 0.92)
    }
}

def run_empirical_contrast_suite():
    print("=" * 80)
    print("EMPIRICAL WCAG 2.1 CONTRAST RATIO AUDIT (AAA Standard: >= 7.0:1)")
    print("=" * 80)

    results = []
    failures = []
    
    for theme_key, theme_data in THEMES.items():
        bg_pri_rgb = hex_to_rgb(theme_data['bg_primary'])
        bg_sec_rgb = hex_to_rgb(theme_data['bg_secondary'])
        
        # Composite card colors over bg_primary
        c_r, c_g, c_b, c_a = theme_data['bg_card_rgba']
        bg_card_rgb = rgba_to_rgb(c_r, c_g, c_b, c_a, *bg_pri_rgb)
        
        ch_r, ch_g, ch_b, ch_a = theme_data['bg_card_hover_rgba']
        bg_card_hover_rgb = rgba_to_rgb(ch_r, ch_g, ch_b, ch_a, *bg_pri_rgb)

        backgrounds = {
            'Body (Primary)': bg_pri_rgb,
            'Card (Normal)': bg_card_rgb,
            'Card (Hover)': bg_card_hover_rgb,
            'Secondary': bg_sec_rgb
        }

        print(f"\n### HUD Theme: {theme_data['name']} (Primary: {theme_data['bg_primary']}, Secondary: {theme_data['bg_secondary']})")
        print("-" * 80)
        print(f"{'Palette':<16} | {'Text Type':<10} | {'Hex':<8} | {'Body CR':<8} | {'Card CR':<8} | {'CardHov':<8} | {'Sec CR':<8} | {'AAA Status'}")
        print("-" * 80)

        for pal_key, pal_data in PALETTES.items():
            for text_role in ['primary', 'secondary', 'muted']:
                fg_hex = pal_data[text_role]
                fg_rgb = hex_to_rgb(fg_hex)
                
                cr_body = contrast_ratio(fg_rgb, bg_pri_rgb)
                cr_card = contrast_ratio(fg_rgb, bg_card_rgb)
                cr_card_hov = contrast_ratio(fg_rgb, bg_card_hover_rgb)
                cr_sec = contrast_ratio(fg_rgb, bg_sec_rgb)
                
                min_cr = min(cr_body, cr_card, cr_card_hov, cr_sec)
                passes_aaa = min_cr >= 7.0
                passes_aa = min_cr >= 4.5
                
                status = "PASS AAA" if passes_aaa else ("PASS AA" if passes_aa else "FAIL")
                
                entry = {
                    'theme': theme_key,
                    'palette': pal_key,
                    'role': text_role,
                    'hex': fg_hex,
                    'cr_body': cr_body,
                    'cr_card': cr_card,
                    'cr_card_hov': cr_card_hov,
                    'cr_sec': cr_sec,
                    'min_cr': min_cr,
                    'status': status
                }
                results.append(entry)
                
                if not passes_aaa:
                    failures.append(entry)
                
                print(f"{pal_key:<16} | {text_role:<10} | {fg_hex:<8} | {cr_body:>7.2f}:1 | {cr_card:>7.2f}:1 | {cr_card_hov:>7.2f}:1 | {cr_sec:>6.2f}:1 | {status}")

    print("\n" + "=" * 80)
    print("FOCUS-VISIBLE INDICATOR CONTRAST RATIO AUDIT (Target >= 3.0:1)")
    print("=" * 80)
    focus_indicators = {
        'obsidian': ('#00f0ff', 'Cyan Outline'),
        'amber': ('#fbbf24', 'Amber Outline'),
        'matrix': ('#00ff9d', 'Emerald Outline'),
        'dracula': ('#c084fc', 'Purple Outline')
    }
    for theme_key, (f_hex, f_name) in focus_indicators.items():
        theme_data = THEMES[theme_key]
        bg_pri_rgb = hex_to_rgb(theme_data['bg_primary'])
        f_rgb = hex_to_rgb(f_hex)
        cr = contrast_ratio(f_rgb, bg_pri_rgb)
        print(f"Theme {theme_data['name']:<18} | Focus: {f_name:<16} ({f_hex}) | Against Body: {cr:>6.2f}:1 | {'PASS (UI Component)' if cr >= 3.0 else 'FAIL'}")

    print("\n" + "=" * 80)
    print(f"TOTAL COMBINATIONS TESTED: {len(results)}")
    print(f"AAA PASS COUNT: {len(results) - len(failures)} / {len(results)} ({((len(results) - len(failures)) / len(results) * 100):.1f}%)")
    if failures:
        print(f"AAA FAILURES ({len(failures)}):")
        for f in failures:
            print(f"  - Theme: {f['theme']}, Palette: {f['palette']}, Role: {f['role']} ({f['hex']}) -> Min CR: {f['min_cr']:.2f}:1 (Status: {f['status']})")
    else:
        print("ALL PALETTE COMBINATIONS ACHIEVE 100% WCAG AAA COMPLIANCE (>= 7.0:1)!")
    print("=" * 80)
    return results, failures

if __name__ == '__main__':
    results, failures = run_empirical_contrast_suite()
    if failures:
        sys.exit(1)
    else:
        sys.exit(0)

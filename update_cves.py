#!/usr/bin/env python3
"""
Bubbsy Threat Intel - Automated CVE & Threat Radar Catalog Updater
Fetches the latest CVEs directly from CISA KEV catalog (and fallbacks),
sorts strictly newest first, and synchronizes:
  - data/radar_cache.json
  - data/radar_cache.js
  - data/radar_metadata.json
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

CISA_KEV_URL = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
RADAR_CACHE_JSON = os.path.join(DATA_DIR, 'radar_cache.json')
RADAR_CACHE_JS = os.path.join(DATA_DIR, 'radar_cache.js')
RADAR_METADATA_JSON = os.path.join(DATA_DIR, 'radar_metadata.json')


def fetch_latest_cves():
    print(f"[*] Fetching live CISA KEV catalog from {CISA_KEV_URL}...")
    headers = {
        'User-Agent': 'Bubbsy-Threat-Radar/3.0 (Cloud Intelligence Pipeline; +https://onyachamp.com)'
    }
    req = urllib.request.Request(CISA_KEV_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=15.0) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP error {resp.status} fetching CISA KEV")
        data = json.loads(resp.read().decode('utf-8', errors='ignore'))
    
    vulns = data.get('vulnerabilities', [])
    print(f"[+] Successfully retrieved {len(vulns)} total vulnerabilities from CISA KEV.")
    
    # Sort strictly newest first by dateAdded
    vulns.sort(key=lambda v: v.get('dateAdded', ''), reverse=True)
    return vulns


def transform_for_js_bundle(raw_vulns, limit=250):
    transformed = []
    for v in raw_vulns[:limit]:
        cve_id = v.get('cveID', '')
        vendor = v.get('vendorProject', '')
        product = v.get('product', '')
        desc = v.get('shortDescription', '')
        date_added = v.get('dateAdded', '')
        ransomware = v.get('knownRansomwareCampaignUse', 'Unknown')
        is_ransomware = ransomware == 'Known'
        vuln_name = v.get('vulnerabilityName', '')
        
        # Build clean descriptive title
        if vuln_name:
            title = f"{cve_id} — {vuln_name}"
        else:
            title = f"{cve_id} — {vendor} {product}"

        transformed.append({
            'id': cve_id,
            'title': title,
            'severity': 'CRITICAL' if is_ransomware else 'HIGH',
            'vendor': vendor,
            'product': product,
            'date': date_added,
            'ransomware': is_ransomware,
            'description': desc,
            'source': 'CISA KEV (Live)',
            'url': f"https://nvd.nist.gov/vuln/detail/{cve_id}"
        })
    return transformed


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        raw_vulns = fetch_latest_cves()
    except Exception as e:
        print(f"[!] Error fetching live CISA KEV: {e}")
        if os.path.exists(RADAR_CACHE_JSON):
            print("[*] Reusing existing local radar_cache.json as fallback...")
            with open(RADAR_CACHE_JSON, 'r', encoding='utf-8') as f:
                raw_vulns = json.load(f)
        else:
            sys.exit(1)

    top_250_raw = raw_vulns[:250]
    top_250_transformed = transform_for_js_bundle(raw_vulns, limit=250)

    # 1. Write data/radar_cache.json
    print(f"[*] Writing {len(top_250_raw)} entries to {RADAR_CACHE_JSON}...")
    with open(RADAR_CACHE_JSON, 'w', encoding='utf-8') as f:
        json.dump(top_250_raw, f, indent=2, ensure_ascii=False)

    # 2. Write data/radar_cache.js
    print(f"[*] Writing {len(top_250_transformed)} bundled entries to {RADAR_CACHE_JS}...")
    js_content = (
        "/**\n"
        " * Bubbsy Threat Radar - Live CVE & Threat Intelligence Cache\n"
        f" * Auto-synchronized: {datetime.now(timezone.utc).isoformat()}\n"
        f" * Latest CVE: {top_250_transformed[0]['id']} ({top_250_transformed[0]['date']})\n"
        " */\n"
        f"window.BUBBSY_RADAR_DATA = {json.dumps(top_250_transformed, indent=2, ensure_ascii=False)};\n"
    )
    with open(RADAR_CACHE_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)

    # 3. Write data/radar_metadata.json
    meta = {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'total_catalog_count': len(raw_vulns),
        'cached_count': len(top_250_raw),
        'latest_cve': top_250_transformed[0]['id'] if top_250_transformed else '',
        'latest_cve_title': top_250_transformed[0]['title'] if top_250_transformed else '',
        'latest_date': top_250_transformed[0]['date'] if top_250_transformed else '',
        'status': 'up_to_date'
    }
    print(f"[*] Writing metadata to {RADAR_METADATA_JSON}...")
    with open(RADAR_METADATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    print("\n[+] Threat Radar CVE update completed successfully!")
    print(f"    - Newest CVE: {meta['latest_cve']} ({meta['latest_date']})")
    print(f"    - Title: {meta['latest_cve_title']}")
    print(f"    - Total Catalog Count: {meta['total_catalog_count']}")


if __name__ == '__main__':
    main()

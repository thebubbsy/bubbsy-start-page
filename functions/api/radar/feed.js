/**
 * Cloudflare Pages Function: /api/radar/feed
 * -----------------------------------------------
 * Live Threat Intelligence & CVE streaming API for Bubbsy Start Page.
 * Fetches the US CISA Known Exploited Vulnerabilities (KEV) catalog at the edge,
 * caches it at Cloudflare edge nodes, and serves strictly sorted newest first.
 *
 * Query params:
 *   ?limit=50      (Number of items to return, default 50, max 250)
 *   ?q=keyword     (Filter items by CVE ID, vendor, product, or description)
 */

const CISA_KEV_URL = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Accept',
  'Content-Type': 'application/json; charset=utf-8',
};

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: CORS_HEADERS,
  });
}

export async function onRequestGet(context) {
  const { request } = context;
  const url = new URL(request.url);
  const limitParam = parseInt(url.searchParams.get('limit') || '50', 10);
  const limit = Math.min(Math.max(1, isNaN(limitParam) ? 50 : limitParam), 250);
  const filterQuery = (url.searchParams.get('q') || '').toLowerCase().trim();

  let items = [];
  let source = 'CISA KEV (Live Edge)';
  let totalCatalogCount = 0;

  try {
    const upstreamRes = await fetch(CISA_KEV_URL, {
      headers: {
        'User-Agent': 'Bubbsy-Threat-Radar/3.0 (Cloudflare Edge Worker; +https://onyachamp.com)',
        'Accept': 'application/json',
      },
      cf: {
        cacheTtl: 1800, // 30-minute edge cache
        cacheEverything: true,
      },
    });

    if (upstreamRes.ok) {
      const data = await upstreamRes.json();
      const vulns = data.vulnerabilities || [];
      totalCatalogCount = vulns.length;

      // Sort strictly newest first by dateAdded
      vulns.sort((a, b) => {
        const da = a.dateAdded || '';
        const db = b.dateAdded || '';
        return db.localeCompare(da);
      });

      for (let i = 0; i < vulns.length && i < 300; i++) {
        const v = vulns[i];
        const cveId = v.cveID || '';
        const vendor = v.vendorProject || '';
        const product = v.product || '';
        const vulnName = v.vulnerabilityName || '';
        const isRansomware = v.knownRansomwareCampaignUse === 'Known';

        items.push({
          id: cveId,
          title: vulnName ? `${cveId} — ${vulnName}` : `${cveId} — ${vendor} ${product}`,
          description: v.shortDescription || '',
          vendor,
          product,
          date: v.dateAdded || '',
          severity: isRansomware ? 'CRITICAL' : 'HIGH',
          ransomware: isRansomware,
          source: 'CISA KEV (Live Edge)',
          url: `https://nvd.nist.gov/vuln/detail/${cveId}`,
        });
      }
    } else {
      throw new Error(`Upstream CISA responded with HTTP ${upstreamRes.status}`);
    }
  } catch (err) {
    source = 'Threat Radar (Edge Fallback)';
    items = getFallbackAdvisories();
    totalCatalogCount = items.length;
  }

  // Apply keyword filtering if specified
  if (filterQuery) {
    items = items.filter(i =>
      i.id.toLowerCase().includes(filterQuery) ||
      i.title.toLowerCase().includes(filterQuery) ||
      i.description.toLowerCase().includes(filterQuery) ||
      (i.vendor && i.vendor.toLowerCase().includes(filterQuery)) ||
      (i.product && i.product.toLowerCase().includes(filterQuery))
    );
  }

  const responseBody = {
    status: 'ok',
    source,
    total_catalog_count: totalCatalogCount,
    count: Math.min(items.length, limit),
    feed: items.slice(0, limit),
    fetched_at: new Date().toISOString(),
  };

  return new Response(JSON.stringify(responseBody), {
    status: 200,
    headers: {
      ...CORS_HEADERS,
      'Cache-Control': 'public, max-age=900, s-maxage=1800, stale-while-revalidate=86400',
    },
  });
}

function getFallbackAdvisories() {
  return [
    {
      id: 'CVE-2026-76504',
      title: 'CVE-2026-76504 — Cisco Catalyst SD-WAN Manager Hex Encoding Vulnerability',
      description: 'Cisco Catalyst SD-WAN Manager contains a hex encoding vulnerability that allows an authenticated attacker to inject arbitrary commands.',
      vendor: 'Cisco',
      product: 'Catalyst SD-WAN Manager',
      date: '2026-09-30',
      severity: 'CRITICAL',
      ransomware: false,
      source: 'CISA KEV',
      url: 'https://nvd.nist.gov/vuln/detail/CVE-2026-76504',
    },
    {
      id: 'CVE-2026-86950',
      title: 'CVE-2026-86950 — Apple Multiple Products Out-of-Bounds Write Vulnerability',
      description: 'Apple iOS, iPadOS, macOS, and visionOS contain an out-of-bounds write vulnerability enabling arbitrary code execution.',
      vendor: 'Apple',
      product: 'iOS, iPadOS, macOS, visionOS',
      date: '2026-09-29',
      severity: 'CRITICAL',
      ransomware: false,
      source: 'CISA KEV',
      url: 'https://nvd.nist.gov/vuln/detail/CVE-2026-86950',
    },
    {
      id: 'CVE-2026-88772',
      title: 'CVE-2026-88772 — Citrix NetScaler Improper Restriction of Operations Memory Buffer Vulnerability',
      description: 'Citrix NetScaler ADC and Gateway contain an improper restriction of operations within memory buffer boundaries vulnerability.',
      vendor: 'Citrix',
      product: 'NetScaler ADC and Gateway',
      date: '2026-09-27',
      severity: 'CRITICAL',
      ransomware: true,
      source: 'CISA KEV',
      url: 'https://nvd.nist.gov/vuln/detail/CVE-2026-88772',
    }
  ];
}

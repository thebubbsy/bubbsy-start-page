import urllib.request
import urllib.parse
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

base_url = 'http://127.0.0.1:7777'

def test_live_platforms():
    platforms = ['github', 'bluesky', 'keybase', 'reddit', 'gitlab', 'devto', 'dockerhub', 'whirlpool', 'ocau', 'ozbargain', 'gravatar', 'all']
    print('=== 1. Testing Live Platform Scrapers ===')
    for p in platforms:
        url = f'{base_url}/api/social/candidates?platform={p}&query=torvalds&limit=3'
        try:
            with urllib.request.urlopen(url, timeout=10.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                cands = data.get('candidates', [])
                cached_flag = data.get('cached')
                print(f'[{resp.status}] Platform {p:10} -> returned {len(cands)} candidates, cached={cached_flag}')
                if cands:
                    first = cands[0]
                    disp = first.get('display_name', '')
                    avatar = first.get('avatar_url', '')
                    print(f"     Sample: {first.get('platform')} | {disp} | {avatar[:50]}...")
        except Exception as e:
            print(f'[FAIL] Platform {p:10} -> {e}')

def test_edge_queries():
    print('\n=== 2. Testing Malicious / Edge Queries ===')
    edge_queries = [
        ('', 'empty query'),
        ('   ', 'whitespace query'),
        ('!@#$%^&*()', 'special symbols'),
        ("<script>alert(1)</script>", 'XSS payload'),
        ("' OR '1'='1", 'SQL injection'),
        ('李小龙', 'CJK Unicode'),
        ('🧑‍💻_ninja', 'Emoji query'),
        ('a' * 2000, 'Long string (2000 chars)')
    ]
    for q, desc in edge_queries:
        url = f'{base_url}/api/social/candidates?platform=github&query={urllib.parse.quote(q)}&limit=3'
        try:
            with urllib.request.urlopen(url, timeout=5.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                print(f"[{resp.status}] {desc:25} -> returned {len(data.get('candidates', []))} candidates, status=OK")
        except Exception as e:
            print(f'[FAIL] {desc:25} -> {e}')

def test_social_scan():
    print('\n=== 3. Testing /api/social/scan ===')
    scan_tests = ['torvalds', '!@#$%', '', '李小龙']
    for u in scan_tests:
        url = f'{base_url}/api/social/scan?username={urllib.parse.quote(u)}'
        try:
            with urllib.request.urlopen(url, timeout=10.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                total = data.get('total_profiles', 0)
                verified = data.get('verified_found_count', 0)
                print(f"[{resp.status}] Scan username={u!r:15} -> {total} profiles, {verified} verified")
        except urllib.error.HTTPError as he:
            print(f"[{he.code}] Scan username={u!r:15} -> HTTP {he.code}: {he.reason}")
        except Exception as e:
            print(f"[FAIL] Scan username={u!r:15} -> {e}")

if __name__ == '__main__':
    test_live_platforms()
    test_edge_queries()
    test_social_scan()

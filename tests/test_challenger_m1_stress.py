#!/usr/bin/env python3
"""
================================================================================
EMPIRICAL CHALLENGER 1 STRESS HARNESS: Milestone 1
Target: server.py, /api/social/candidates, BubbsyThreadingServer, Multi-Platform Scrapers, TTL Cache
================================================================================
"""

import sys
import os
import time
import json
import threading
import concurrent.futures
import urllib.request
import urllib.parse
import urllib.error
import socketserver
import http.server
from typing import Dict, List, Any, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import server

RESULTS = {
    "test_run_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "summary": {},
    "sections": {}
}

class TestServerHarness:
    __test__ = False

    def __init__(self):
        self.server = None
        self.thread = None
        self.port = 0
        self.base_url = ""

    def start(self):
        # Use BubbsyThreadingServer with BubbsyHandler on random free port
        server.BubbsyThreadingServer.allow_reuse_address = True
        self.server = server.BubbsyThreadingServer(('127.0.0.1', 0), server.BubbsyHandler)
        self.port = self.server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.1)
        print(f"[*] Live Test BubbsyThreadingServer started on {self.base_url}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("[*] Test BubbsyThreadingServer shut down successfully.")

def fetch_url(url: str, timeout: float = 10.0) -> Tuple[int, Dict[str, Any], float]:
    start = time.perf_counter()
    req = urllib.request.Request(url, headers={'User-Agent': 'Challenger1-StressHarness/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = (time.perf_counter() - start) * 1000.0  # ms
            status = resp.status
            body = resp.read().decode('utf-8')
            try:
                data = json.loads(body)
            except Exception:
                data = {"raw": body}
            return status, data, elapsed
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - start) * 1000.0
        try:
            body = e.read().decode('utf-8')
            data = json.loads(body)
        except Exception:
            data = {"error": str(e)}
        return e.code, data, elapsed
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000.0
        return 0, {"error": str(e)}, elapsed

def run_concurrency_stress(base_url: str, num_threads: int = 50, total_requests: int = 100) -> Dict[str, Any]:
    print(f"\n--- [1] Concurrency & Threading Stress Test ({num_threads} workers, {total_requests} requests) ---")
    platforms = ['github', 'bluesky', 'keybase', 'reddit', 'gitlab', 'devto', 'dockerhub', 'whirlpool', 'ocau', 'ozbargain', 'gravatar']
    queries = ['torvalds', 'alice', 'bob', 'charlie', 'dave', 'eva', 'frank', 'grace', 'heidi', 'ivan']
    
    tasks = []
    for i in range(total_requests):
        plat = platforms[i % len(platforms)]
        q = queries[i % len(queries)]
        url = f"{base_url}/api/social/candidates?platform={plat}&query={q}&limit=5"
        tasks.append(url)

    latencies = []
    status_codes = {}
    errors = []

    start_total = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_url = {executor.submit(fetch_url, url, 12.0): url for url in tasks}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                status, data, elapsed = future.result()
                status_codes[status] = status_codes.get(status, 0) + 1
                latencies.append(elapsed)
                if status != 200:
                    errors.append({"url": url, "status": status, "data": data})
            except Exception as e:
                errors.append({"url": url, "status": 0, "error": str(e)})

    total_time_s = time.perf_counter() - start_total
    success_count = status_codes.get(200, 0)
    pass_rate = (success_count / total_requests) * 100.0 if total_requests else 0.0

    latencies.sort()
    min_lat = latencies[0] if latencies else 0
    max_lat = latencies[-1] if latencies else 0
    avg_lat = sum(latencies) / len(latencies) if latencies else 0
    p50_lat = latencies[len(latencies)//2] if latencies else 0
    p95_lat = latencies[int(len(latencies)*0.95)] if latencies else 0

    rps = total_requests / total_time_s if total_time_s else 0

    print(f"Completed {total_requests} requests in {total_time_s:.2f}s ({rps:.1f} req/s)")
    print(f"Status codes: {status_codes}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"Latency: Min={min_lat:.1f}ms, Avg={avg_lat:.1f}ms, P50={p50_lat:.1f}ms, P95={p95_lat:.1f}ms, Max={max_lat:.1f}ms")
    if errors:
        print(f"Encountered {len(errors)} errors: {errors[:3]}")

    return {
        "num_threads": num_threads,
        "total_requests": total_requests,
        "total_time_s": round(total_time_s, 2),
        "rps": round(rps, 1),
        "status_codes": status_codes,
        "pass_rate_pct": round(pass_rate, 2),
        "latency_ms": {
            "min": round(min_lat, 1),
            "avg": round(avg_lat, 1),
            "p50": round(p50_lat, 1),
            "p95": round(p95_lat, 1),
            "max": round(max_lat, 1)
        },
        "errors": errors
    }

def run_cache_benchmark(base_url: str) -> Dict[str, Any]:
    print(f"\n--- [2] In-Memory TTL Cache Benchmark & Validation ---")
    # Clear server cache for test repeatability
    with server.CACHE_LOCK:
        server.SOCIAL_CACHE.clear()

    test_queries = [
        ('github', 'torvalds'),
        ('bluesky', 'jay.bsky.team'),
        ('keybase', 'max'),
        ('reddit', 'spez'),
        ('gitlab', 'ayufan'),
        ('devto', 'ben'),
        ('dockerhub', 'library'),
        ('whirlpool', 'mod'),
        ('ocau', 'admin'),
        ('ozbargain', 'scott')
    ]

    cache_metrics = []
    for plat, q in test_queries:
        url = f"{base_url}/api/social/candidates?platform={plat}&query={q}&limit=5"
        
        # Cold miss
        status1, data1, elapsed_cold = fetch_url(url)
        cached1 = data1.get('cached', False)
        
        # Warm hit
        status2, data2, elapsed_warm = fetch_url(url)
        cached2 = data2.get('cached', False)

        speedup = elapsed_cold / elapsed_warm if elapsed_warm > 0 else 1.0
        
        # Content equivalence test
        data1_candidates = json.dumps(data1.get('candidates', []), sort_keys=True)
        data2_candidates = json.dumps(data2.get('candidates', []), sort_keys=True)
        identical = (data1_candidates == data2_candidates)

        cache_metrics.append({
            "platform": plat,
            "query": q,
            "cold_latency_ms": round(elapsed_cold, 2),
            "warm_latency_ms": round(elapsed_warm, 2),
            "speedup_ratio": round(speedup, 1),
            "cold_cached_flag": cached1,
            "warm_cached_flag": cached2,
            "data_integrity_identical": identical
        })
        print(f"[{plat.upper()}] Cold: {elapsed_cold:.1f}ms (cached={cached1}) -> Warm: {elapsed_warm:.1f}ms (cached={cached2}) => Speedup: {speedup:.1f}x (Match={identical})")

    # Cache Expiration Test (Simulating TTL expiration)
    print("\nVerifying TTL Expiration behavior...")
    cache_key = "github_test_ttl______5"
    with server.CACHE_LOCK:
        # Inject old cache item (11 minutes ago)
        server.SOCIAL_CACHE[cache_key] = (time.time() - 660, {"platform": "github", "candidates": []})
    
    expired_check = server.get_cached_candidates(cache_key)
    ttl_pass = (expired_check is None)
    with server.CACHE_LOCK:
        key_still_in_dict = cache_key in server.SOCIAL_CACHE
    print(f"TTL Expiration (expired item evicted on access): Pass={ttl_pass and not key_still_in_dict}")

    # Cache Max Size & Eviction Test (> 500 entries)
    print("\nVerifying Cache Eviction at Capacity (> 500 entries)...")
    with server.CACHE_LOCK:
        server.SOCIAL_CACHE.clear()
    
    for i in range(550):
        server.set_cached_candidates(f"key_{i}", {"item": i})
        
    with server.CACHE_LOCK:
        cache_size = len(server.SOCIAL_CACHE)
    capacity_pass = (cache_size <= 501)
    print(f"Cache Size after 550 inserts: {cache_size} (Max <= 501): Pass={capacity_pass}")

    # Concurrent Cache Hammering Test (50 threads accessing same key)
    print("\nVerifying Concurrent Cache Race Condition Resilience (50 threads hammering same key)...")
    shared_key = "concurrency_test_key"
    server.set_cached_candidates(shared_key, {"candidates": [{"id": 1, "name": "test"}]})
    
    def hammer_cache(idx):
        res = server.get_cached_candidates(shared_key)
        server.set_cached_candidates(f"temp_key_{idx}", {"temp": idx})
        return res is not None and res.get('cached') == True

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        futs = [ex.submit(hammer_cache, i) for i in range(100)]
        results = [f.result() for f in futs]
    hammer_pass = all(results)
    print(f"Concurrent Cache Hammer: {sum(results)}/100 succeeded. Pass={hammer_pass}")

    avg_cold = sum(m['cold_latency_ms'] for m in cache_metrics) / len(cache_metrics)
    avg_warm = sum(m['warm_latency_ms'] for m in cache_metrics) / len(cache_metrics)
    overall_speedup = avg_cold / avg_warm if avg_warm > 0 else 1.0

    return {
        "cache_metrics": cache_metrics,
        "avg_cold_ms": round(avg_cold, 2),
        "avg_warm_ms": round(avg_warm, 2),
        "overall_speedup_multiplier": round(overall_speedup, 1),
        "ttl_expiration_pass": ttl_pass and not key_still_in_dict,
        "capacity_eviction_pass": capacity_pass,
        "concurrent_hammer_pass": hammer_pass
    }

def run_multi_platform_coverage(base_url: str) -> Dict[str, Any]:
    print(f"\n--- [3] Deep Multi-Platform Scraping & OSINT Schema Validation ---")
    platforms = [
        'github', 'bluesky', 'keybase', 'reddit', 'gitlab', 'devto', 
        'dockerhub', 'whirlpool', 'ocau', 'ozbargain', 'gravatar', 'all'
    ]

    platform_results = {}
    mandatory_fields = [
        'key', 'platform', 'platform_id', 'category', 'handle', 'display_name',
        'url', 'avatar_url', 'bio', 'location', 'company', 'stats', 'verified',
        'reverse_image_search', 'email_permutations', 'inferred_timezone'
    ]

    for plat in platforms:
        url = f"{base_url}/api/social/candidates?platform={plat}&query=torvalds&names=Linus+Torvalds&locations=Portland%2C+OR&org=Linux+Foundation&limit=5"
        status, data, elapsed = fetch_url(url, timeout=10.0)
        
        candidates = data.get('candidates', []) if status == 200 else []
        total = data.get('total', 0)
        
        field_checks = {}
        for field in mandatory_fields:
            field_checks[field] = True

        reverse_image_checks = True
        email_perms_checks = True
        avatar_validity_checks = True

        for c in candidates:
            for field in mandatory_fields:
                if field not in c:
                    field_checks[field] = False
            
            # Verify Reverse Image Search structure
            ris = c.get('reverse_image_search', {})
            if not isinstance(ris, dict) or not {'google_lens', 'yandex', 'tineye', 'bing', 'pimeyes'}.issubset(ris.keys()):
                reverse_image_checks = False

            # Verify Email Permutations
            emails = c.get('email_permutations', [])
            if not isinstance(emails, list) or len(emails) == 0 or not any('@' in e for e in emails):
                email_perms_checks = False

            # Verify Avatar URL format
            avatar = c.get('avatar_url', '')
            if not avatar or not avatar.startswith('http'):
                avatar_validity_checks = False

        passed = (status == 200 and len(candidates) > 0 and all(field_checks.values()) and reverse_image_checks and email_perms_checks and avatar_validity_checks)
        
        platform_results[plat] = {
            "status_code": status,
            "candidate_count": len(candidates),
            "total_reported": total,
            "latency_ms": round(elapsed, 1),
            "mandatory_fields_valid": all(field_checks.values()),
            "reverse_image_valid": reverse_image_checks,
            "email_permutations_valid": email_perms_checks,
            "avatar_valid": avatar_validity_checks,
            "passed": passed,
            "sample_avatar": candidates[0].get('avatar_url') if candidates else None,
            "sample_handle": candidates[0].get('handle') if candidates else None,
            "sample_display_name": candidates[0].get('display_name') if candidates else None
        }

        status_str = "PASS" if passed else "FAIL"
        print(f"[{plat.upper():10}] {status_str} | Status={status} | Cands={len(candidates)} | Latency={elapsed:.1f}ms | Avatar={candidates[0].get('avatar_url', '')[:45] if candidates else 'None'}...")

    all_passed = all(p['passed'] for p in platform_results.values())
    return {
        "platforms": platform_results,
        "all_platforms_passed": all_passed
    }

def run_burst_load_stress(base_url: str, burst_count: int = 200) -> Dict[str, Any]:
    print(f"\n--- [4] High-Load Fast Query Burst Stress ({burst_count} requests in tight parallel burst) ---")
    urls = [
        f"{base_url}/api/social/candidates?platform=github&query=target_{i%20}&limit=5"
        for i in range(burst_count)
    ]

    start = time.perf_counter()
    status_counts = {}
    latencies = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(fetch_url, u, 10.0) for u in urls]
        for f in concurrent.futures.as_completed(futures):
            status, data, elapsed = f.result()
            status_counts[status] = status_counts.get(status, 0) + 1
            latencies.append(elapsed)

    total_time = time.perf_counter() - start
    latencies.sort()
    rps = burst_count / total_time if total_time else 0
    success = status_counts.get(200, 0)
    pass_rate = (success / burst_count) * 100.0

    print(f"Burst Results: {burst_count} requests in {total_time:.2f}s ({rps:.1f} req/s)")
    print(f"Status Counts: {status_counts}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"Latency: Min={latencies[0]:.1f}ms, P50={latencies[len(latencies)//2]:.1f}ms, P95={latencies[int(len(latencies)*0.95)]:.1f}ms, Max={latencies[-1]:.1f}ms")

    return {
        "burst_count": burst_count,
        "total_time_s": round(total_time, 2),
        "rps": round(rps, 1),
        "status_counts": status_counts,
        "pass_rate_pct": round(pass_rate, 2),
        "latency_ms": {
            "min": round(latencies[0], 1),
            "p50": round(latencies[len(latencies)//2], 1),
            "p95": round(latencies[int(len(latencies)*0.95)], 1),
            "max": round(latencies[-1], 1)
        }
    }

def run_adversarial_boundary_fuzz(base_url: str) -> Dict[str, Any]:
    print(f"\n--- [5] Adversarial & Boundary Fuzzing Tests ---")
    
    sqli_q = urllib.parse.quote("' OR '1'='1; DROP TABLE users; --")
    xss_q = urllib.parse.quote("<script>alert('xss')</script>")
    spec_q = urllib.parse.quote("!@#$%^&*()_+")
    emoji_q = urllib.parse.quote("👨‍💻🚀🔒")
    long_q = "a" * 2000

    test_cases = [
        {
            "name": "Empty Query & Names",
            "url": f"{base_url}/api/social/candidates?platform=github&query=&names=",
            "expected_status": 200,
            "validate": lambda d: d.get('total') == 0 and len(d.get('candidates', [])) == 0
        },
        {
            "name": "Special Characters in Query",
            "url": f"{base_url}/api/social/candidates?platform=github&query={spec_q}",
            "expected_status": 200,
            "validate": lambda d: 'candidates' in d
        },
        {
            "name": "Unicode & Emojis",
            "url": f"{base_url}/api/social/candidates?platform=github&query={emoji_q}",
            "expected_status": 200,
            "validate": lambda d: 'candidates' in d
        },
        {
            "name": "SQL Injection String",
            "url": f"{base_url}/api/social/candidates?platform=github&query={sqli_q}",
            "expected_status": 200,
            "validate": lambda d: 'candidates' in d and not d.get('error')
        },
        {
            "name": "XSS Script Payload",
            "url": f"{base_url}/api/social/candidates?platform=github&query={xss_q}",
            "expected_status": 200,
            "validate": lambda d: 'candidates' in d and '<script>' not in d.get('query', '')
        },
        {
            "name": "Negative Limit (limit=-10 -> clamped to 1)",
            "url": f"{base_url}/api/social/candidates?platform=github&query=torvalds&limit=-10",
            "expected_status": 200,
            "validate": lambda d: len(d.get('candidates', [])) >= 1 and len(d.get('candidates', [])) <= 10
        },
        {
            "name": "Zero Limit (limit=0 -> clamped to 1)",
            "url": f"{base_url}/api/social/candidates?platform=github&query=torvalds&limit=0",
            "expected_status": 200,
            "validate": lambda d: len(d.get('candidates', [])) >= 1 and len(d.get('candidates', [])) <= 10
        },
        {
            "name": "Excessive Limit (limit=9999 -> clamped to 10)",
            "url": f"{base_url}/api/social/candidates?platform=github&query=torvalds&limit=9999",
            "expected_status": 200,
            "validate": lambda d: len(d.get('candidates', [])) <= 10
        },
        {
            "name": "Non-Integer Limit (limit=abc -> fallback to 5)",
            "url": f"{base_url}/api/social/candidates?platform=github&query=torvalds&limit=abc",
            "expected_status": 200,
            "validate": lambda d: len(d.get('candidates', [])) <= 5
        },
        {
            "name": "Unknown Platform (platform=matrix_cyber)",
            "url": f"{base_url}/api/social/candidates?platform=matrix_cyber&query=torvalds",
            "expected_status": 200,
            "validate": lambda d: 'candidates' in d
        },
        {
            "name": "Ultra Long String (2000 chars)",
            "url": f"{base_url}/api/social/candidates?platform=github&query={long_q}",
            "expected_status": 200,
            "validate": lambda d: 'candidates' in d
        },
        {
            "name": "Cross-Pivot Enriched Query Forwarding",
            "url": f"{base_url}/api/social/candidates?platform=reddit&query=torvalds&names=Linus+Torvalds&locations=Portland%2C+OR&org=Linux+Foundation&limit=5",
            "expected_status": 200,
            "validate": lambda d: d.get('harvested_context', {}).get('names') == ['Linus Torvalds'] and d.get('harvested_context', {}).get('locations') == ['Portland, OR']
        }
    ]

    fuzz_results = []
    for tc in test_cases:
        status, data, elapsed = fetch_url(tc['url'])
        status_ok = (status == tc['expected_status'])
        validation_ok = False
        try:
            validation_ok = tc['validate'](data)
        except Exception as e:
            validation_ok = False

        passed = status_ok and validation_ok
        fuzz_results.append({
            "name": tc['name'],
            "status_code": status,
            "passed": passed,
            "latency_ms": round(elapsed, 1)
        })
        print(f"[{'PASS' if passed else 'FAIL'}] {tc['name']} -> HTTP {status} ({elapsed:.1f}ms)")

    all_fuzz_passed = all(r['passed'] for r in fuzz_results)
    return {
        "test_cases": fuzz_results,
        "all_passed": all_fuzz_passed
    }

def main():
    harness = TestServerHarness()
    try:
        harness.start()
        base_url = harness.base_url

        sec1 = run_concurrency_stress(base_url, num_threads=50, total_requests=100)
        sec2 = run_cache_benchmark(base_url)
        sec3 = run_multi_platform_coverage(base_url)
        sec4 = run_burst_load_stress(base_url, burst_count=200)
        sec5 = run_adversarial_boundary_fuzz(base_url)

        RESULTS["sections"]["concurrency_stress"] = sec1
        RESULTS["sections"]["ttl_cache_benchmark"] = sec2
        RESULTS["sections"]["multi_platform_coverage"] = sec3
        RESULTS["sections"]["burst_load_stress"] = sec4
        RESULTS["sections"]["adversarial_fuzzing"] = sec5

        # Calculate Overall Verdict
        verdict = "APPROVE" if (
            sec1["pass_rate_pct"] >= 99.0 and
            sec2["ttl_expiration_pass"] and
            sec2["capacity_eviction_pass"] and
            sec2["overall_speedup_multiplier"] >= 2.0 and
            sec3["all_platforms_passed"] and
            sec4["pass_rate_pct"] >= 99.0 and
            sec5["all_passed"]
        ) else "REQUEST_CHANGES"

        RESULTS["summary"] = {
            "verdict": verdict,
            "concurrency_pass_rate": sec1["pass_rate_pct"],
            "cache_overall_speedup": f"{sec2['overall_speedup_multiplier']}x",
            "platforms_tested_count": len(sec3["platforms"]),
            "burst_pass_rate": sec4["pass_rate_pct"],
            "fuzz_tests_pass_rate": f"{sum(1 for t in sec5['test_cases'] if t['passed'])}/{len(sec5['test_cases'])}"
        }

        print("\n" + "="*70)
        print(f"  CHALLENGER 1 FINAL VERDICT: {verdict}")
        print(f"  - Concurrency Pass Rate: {sec1['pass_rate_pct']}%")
        print(f"  - Cache Speedup: {sec2['overall_speedup_multiplier']}x")
        print(f"  - Multi-Platform Coverage: {len(sec3['platforms'])}/12 platforms verified")
        print(f"  - Burst Load Pass Rate: {sec4['pass_rate_pct']}%")
        print(f"  - Adversarial Fuzzing: {sum(1 for t in sec5['test_cases'] if t['passed'])}/{len(sec5['test_cases'])} passed")
        print("="*70)

        # Output JSON results file
        out_path = os.path.join(ROOT_DIR, "tests", "challenger_m1_results.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(RESULTS, f, indent=2)
        print(f"[*] Full metrics saved to {out_path}")

    finally:
        harness.stop()

if __name__ == '__main__':
    main()

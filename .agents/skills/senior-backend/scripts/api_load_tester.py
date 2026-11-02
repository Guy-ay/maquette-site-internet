#!/usr/bin/env python3
"""
Testeur de charge d'API HTTP léger et sans dépendance externe.
Mesure la latence moyenne, médiane, p95, p99, le débit RPS et les codes d'erreur.
Usage:
    python api_load_tester.py <url> [--concurrency 10] [--requests 50]
"""

import sys
import time
import argparse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

def fetch_url(url):
    start = time.perf_counter()
    status_code = None
    success = False
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SeniorBackend-LoadTester/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            success = 200 <= status_code < 400
    except urllib.error.HTTPError as e:
        status_code = e.code
    except Exception as e:
        status_code = str(e)
    duration_ms = (time.perf_counter() - start) * 1000
    return duration_ms, status_code, success

def run_load_test(url, concurrency, total_requests):
    print(f"🚀 Démarrage du test de charge sur : {url}")
    print(f"⚙️  Concurrence : {concurrency} workers | Total requêtes : {total_requests}\n")

    latencies = []
    status_codes = {}
    success_count = 0

    t_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(fetch_url, url) for _ in range(total_requests)]
        for f in futures:
            dur, status, ok = f.result()
            latencies.append(dur)
            status_codes[status] = status_codes.get(status, 0) + 1
            if ok:
                success_count += 1

    total_time = time.perf_counter() - t_start
    rps = total_requests / total_time if total_time > 0 else 0

    latencies.sort()
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    median_latency = latencies[len(latencies) // 2] if latencies else 0
    p95_index = int(len(latencies) * 0.95)
    p95_latency = latencies[p95_index] if latencies else 0
    p99_index = int(len(latencies) * 0.99)
    p99_latency = latencies[p99_index] if latencies else 0

    print("📊 RÉSULTATS DU TEST DE CHARGE :")
    print(f"  • Temps total : {total_time:.2f} secondes")
    print(f"  • Requêtes par seconde (RPS) : {rps:.1f} req/s")
    print(f"  • Taux de succès : {success_count}/{total_requests} ({(success_count/total_requests)*100:.1f}%)")
    print(f"  • Latence moyenne : {avg_latency:.1f} ms")
    print(f"  • Latence médiane (p50) : {median_latency:.1f} ms")
    print(f"  • Latence 95ᵉ percentile (p95) : {p95_latency:.1f} ms")
    print(f"  • Latence 99ᵉ percentile (p99) : {p99_latency:.1f} ms")
    print("\n📈 Répartition des codes HTTP reçus :")
    for code, cnt in status_codes.items():
        print(f"    - Code {code} : {cnt} requêtes")

def main():
    parser = argparse.ArgumentParser(description="Testeur de charge HTTP léger")
    parser.add_argument("url", help="URL cible de l'API (ex: http://localhost:4000/api/v1/articles)")
    parser.add_argument("--concurrency", type=int, default=10, help="Nombre de requêtes concurrentes")
    parser.add_argument("--requests", type=int, default=50, help="Nombre total de requêtes")
    args = parser.parse_args()

    run_load_test(args.url, args.concurrency, args.requests)

if __name__ == "__main__":
    main()


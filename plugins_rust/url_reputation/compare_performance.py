import asyncio
import argparse
import json
from pathlib import Path
from unittest.mock import patch
import statistics
import sys
import time
from typing import Any, Literal
from mcpgateway.plugins.framework import (
    PluginConfig,
    ResourceHookType,
)

# Try to import Rust implementation
try:
    from url_reputation_rust import URLReputationPlugin as RustPlugin
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    print("⚠️  Rust implementation not available. Build it with:")
    print("   cd plugins_rust/url_reputation && maturin develop --release")


# Add plugins directory to path to import Python implementation
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "plugins" / "url_reputation"))


class Payload:
    def __init__(self, url):
        self.uri = url


def load_bench_config(config_path: str = "bench_config.json"):
    """Load benchmark configuration from JSON file."""
    config_file = Path(__file__).parent / config_path
    if not config_file.exists():
        raise FileNotFoundError(f"Benchmark config file not found: {config_file}")

    with open(config_file, 'r') as f:
        return json.load(f)


def generate_payloads(size: int, urls: list[str]):
    """Return a list of urls to be used in the benchmark"""
    url_count = len(urls)
    repeated = urls * (size // url_count)
    remaining = urls[:(size % url_count)]

    return [Payload(url) for url in repeated + remaining]


async def run_benchmark(language: Literal["python", "rust"], config: PluginConfig, iterations: int, urls: list[str], warmup: int = 5):
    """Run benchmark for specified language implementation."""
    if language == "rust" and not RUST_AVAILABLE:
        return [], 0

    if language == "python":
        import url_reputation
        with patch.object(url_reputation, '_RUST_AVAILABLE', False):
            from url_reputation import URLReputationPlugin
            plugin = URLReputationPlugin(config)
            # Warmup phase
            for payload in generate_payloads(warmup, urls):
                await plugin.resource_pre_fetch(payload, None)

            # Actual benchmark
            times = []
            for payload in generate_payloads(iterations, urls):
                start = time.perf_counter()
                await plugin.resource_pre_fetch(payload, None)
                times.append(time.perf_counter() - start)

            return times, len(times)
    else:
        import url_reputation
        with patch.object(url_reputation, '_RUST_AVAILABLE', True):
            from url_reputation import URLReputationPlugin
            plugin = URLReputationPlugin(config)
            # Warmup phase
            for payload in generate_payloads(warmup, urls):
                await plugin.resource_pre_fetch(payload, None)

            # Actual benchmark
            times = []
            for payload in generate_payloads(iterations, urls):
                start = time.perf_counter()
                await plugin.resource_pre_fetch(payload, None)
                times.append(time.perf_counter() - start)

            return times, len(times)


async def run_scenario(name: str, config: PluginConfig, iterations: int, urls: list[str], warmup: int = 5):
    """Run benchmark scenario."""
    print(f"\n{'=' * 70}")
    print(f"Scenario: {name}")
    print(f"{'=' * 70}")

    results = {}
    for language in ["python", "rust"]:
        print(f"Running {language}...", end=" ", flush=True)
        times, count = await run_benchmark(language, config, iterations, urls, warmup)

        if not times:
            print(f"✗ {language} => Skipped (not available)")
            if language == "rust":
                return
            continue

        mean = statistics.mean(times) * 1000
        median = statistics.median(times) * 1000
        stdev = statistics.stdev(times) * 1000 if len(times) > 1 else 0
        results[language] = {"mean": mean, "median": median, "stdev": stdev, "count": count}
        print(f"✓ {language} => ({mean:.3f} ms/iter, {count} payloads)")

    if len(results) < 2:
        return

    speedup = results["python"]["mean"] / results["rust"]["mean"] if results["rust"]["mean"] > 0 else 0
    print(f"\nResults:")
    print(f"\tPython:    {results['python']['mean']:.3f} ms ±{results['python']['stdev']:.3f} (median: {results['python']['median']:.3f})")
    print(f"\tRust:      {results['rust']['mean']:.3f} ms ±{results['rust']['stdev']:.3f} (median: {results['rust']['median']:.3f}) - {speedup:.2f}x faster 🚀")
    if results["python"]["count"] != results["rust"]["count"]:
        print(f"\n  ⚠️  WARNING: Different counts! Python={results['python']['count']}, Rust={results['rust']['count']}")


async def main():
    parser = argparse.ArgumentParser(description="Rust vs Python benchmark for URL reputation plugin")
    parser.add_argument("--iterations", type=int, default=1000, help="Iterations per scenario")
    parser.add_argument("--warmup", type=int, default=100, help="Warmup iterations")
    parser.add_argument("--config", type=str, default="bench_config.json", help="Path to benchmark config file")
    parser.add_argument("--scenario", type=str, help="Run specific scenario (default: run all)")
    args = parser.parse_args()

    print("🔍 URL Reputation benchmark (Native Python Objects)")
    print(f"Iterations: {args.iterations} (+ {args.warmup} warmup)")
    print(f"Rust available: {'✓' if RUST_AVAILABLE else '✗'}")

    # Load benchmark configuration
    try:
        scenarios = load_bench_config(args.config)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file: {e}")
        sys.exit(1)

    if not scenarios:
        print("❌ Error: No scenarios found in config file")
        sys.exit(1)

    print(f"Loaded {len(scenarios)} scenario(s)")

    # Filter scenarios if specific one requested
    if args.scenario:
        scenarios = [s for s in scenarios if s.get("scenario") == args.scenario]
        if not scenarios:
            available = [s.get("scenario") for s in load_bench_config(args.config)]
            print(f"❌ Error: Scenario '{args.scenario}' not found in config")
            print(f"Available scenarios: {', '.join(available)}")
            sys.exit(1)

    # Run each scenario
    for scenario_data in scenarios:
        scenario_name = scenario_data.get("name", scenario_data.get("scenario", "Unknown"))
        scenario_config = scenario_data.get("config", {}).copy()
        urls = scenario_data.get("urls", [])

        if not urls:
            print(f"⚠️  Warning: No URLs found for scenario '{scenario_name}', skipping")
            continue

        # Handle domain_multiplier if present
        domain_multiplier = scenario_config.pop("domain_multiplier", 1)
        if "blocked_domains" in scenario_config and domain_multiplier > 1:
            scenario_config["blocked_domains"] = scenario_config["blocked_domains"] * domain_multiplier

        plugin_config = PluginConfig(
            name="urlrep",
            kind="plugins.url_reputation.url_reputation.URLReputationPlugin",
            hooks=[ResourceHookType.RESOURCE_PRE_FETCH],
            config=scenario_config,
        )

        await run_scenario(scenario_name, plugin_config, args.iterations, urls, args.warmup)

    print(f"\n{'=' * 70}")
    print("✅ Benchmark complete!")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    asyncio.run(main())

"""Shared helpers for examples: .env loading and trace printing."""

from __future__ import annotations

from dotenv import load_dotenv

from ubermensch.agent import Agent


def load_env() -> None:
    load_dotenv()


def print_trace(label: str, *agents: Agent) -> None:
    print(f"\n--- {label} trace ---")
    total_in = total_out = total_cr = total_cc = 0
    for a in agents:
        for t in a.trace:
            print(
                f"[{t.agent:>14}] in={t.input_tokens:>4} "
                f"out={t.output_tokens:>4} "
                f"cache_read={t.cache_read:>4} "
                f"cache_create={t.cache_creation:>4}"
            )
            total_in += t.input_tokens
            total_out += t.output_tokens
            total_cr += t.cache_read
            total_cc += t.cache_creation
    cached_ratio = total_cr / max(1, total_in + total_cr) * 100
    print(
        f"totals: in={total_in} out={total_out} cache_read={total_cr} "
        f"cache_create={total_cc} cache_hit≈{cached_ratio:.1f}%"
    )

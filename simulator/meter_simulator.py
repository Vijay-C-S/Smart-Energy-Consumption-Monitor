"""Virtual smart meter simulator.

Sends energy readings to the backend API at configurable intervals.

Examples:
    python simulator/meter_simulator.py --url http://localhost:8000/readings --meters 3 --interval 10 --duration 60
    python simulator/meter_simulator.py --url http://localhost:8000/readings --meter-ids 1,2,5 --profile mixed --seed 42
"""

from __future__ import annotations

import argparse
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Optional

import requests


LOGGER = logging.getLogger("smart_energy.simulator")


@dataclass(frozen=True)
class SimulatorConfig:
    url: str
    meter_ids: List[int]
    interval: float
    duration: Optional[float]
    timeout: float
    profile: str
    seed: Optional[int]


def build_meter_ids(meters: int, meter_ids: Optional[str]) -> List[int]:
    if meter_ids:
        parsed = [int(item.strip()) for item in meter_ids.split(",") if item.strip()]
        if not parsed:
            raise ValueError("--meter-ids must contain at least one numeric meter id")
        return parsed
    if meters < 1:
        raise ValueError("--meters must be at least 1")
    return list(range(1, meters + 1))


def generate_reading(meter_id: int, profile: str) -> dict:
    energy = _pick_energy(profile)
    voltage = round(random.uniform(220.0, 240.0), 2)
    current = round(random.uniform(0.5, 18.0), 2)
    power_factor = round(random.uniform(0.80, 0.99), 2)

    return {
        "meter_id": meter_id,
        "energy_consumed_kwh": energy,
        "voltage": voltage,
        "current": current,
        "power_factor": power_factor,
        "simulated_at": datetime.now(timezone.utc).isoformat(),
    }


def _pick_energy(profile: str) -> float:
    profile = profile.lower()
    if profile == "normal":
        return round(random.uniform(0.1, 1.5), 4)
    if profile == "peak":
        return round(random.uniform(2.0, 5.0), 4)
    if profile == "abnormal":
        return round(random.uniform(3.1, 6.5), 4)

    # mixed profile: mostly normal, sometimes peak or abnormal
    roll = random.random()
    if roll < 0.82:
        return round(random.uniform(0.1, 1.5), 4)
    if roll < 0.96:
        return round(random.uniform(2.0, 5.0), 4)
    return round(random.uniform(3.1, 6.5), 4)


def send_reading(url: str, payload: dict, timeout: float) -> requests.Response:
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response


def run(config: SimulatorConfig) -> None:
    if config.seed is not None:
        random.seed(config.seed)

    start = time.monotonic()
    cycle = 0

    LOGGER.info(
        "Starting simulator | meters=%s interval=%.2fs duration=%s profile=%s url=%s",
        len(config.meter_ids),
        config.interval,
        "continuous" if config.duration is None else f"{config.duration:.0f}s",
        config.profile,
        config.url,
    )

    while True:
        cycle += 1
        for meter_id in config.meter_ids:
            payload = generate_reading(meter_id, config.profile)
            try:
                response = send_reading(config.url, payload, config.timeout)
                LOGGER.info(
                    "cycle=%s meter=%s energy=%.4f kWh status=%s",
                    cycle,
                    meter_id,
                    payload["energy_consumed_kwh"],
                    response.status_code,
                )
            except requests.RequestException as exc:
                LOGGER.error("cycle=%s meter=%s send_failed=%s", cycle, meter_id, exc)

        if config.duration is not None and (time.monotonic() - start) >= config.duration:
            LOGGER.info("Simulator finished after %.1fs", time.monotonic() - start)
            break

        time.sleep(config.interval)


def parse_args() -> SimulatorConfig:
    parser = argparse.ArgumentParser(description="Smart Energy meter reading simulator")
    parser.add_argument("--url", default="http://localhost:8000/readings", help="Backend readings endpoint")
    parser.add_argument("--meters", type=int, default=2, help="Number of sequential meter IDs to simulate")
    parser.add_argument("--meter-ids", default=None, help="Explicit comma-separated meter IDs, e.g. 1,2,5")
    parser.add_argument("--interval", type=float, default=60.0, help="Seconds between sending batches")
    parser.add_argument("--duration", type=float, default=None, help="Optional total runtime in seconds")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds")
    parser.add_argument(
        "--profile",
        choices=("normal", "peak", "abnormal", "mixed"),
        default="mixed",
        help="Reading pattern to simulate",
    )
    parser.add_argument("--seed", type=int, default=None, help="Seed for reproducible output")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s | %(levelname)s | %(message)s")

    meter_ids = build_meter_ids(args.meters, args.meter_ids)
    return SimulatorConfig(
        url=args.url,
        meter_ids=meter_ids,
        interval=args.interval,
        duration=args.duration,
        timeout=args.timeout,
        profile=args.profile,
        seed=args.seed,
    )


if __name__ == "__main__":
    run(parse_args())

"""Reproducible synthetic-processing and physical IBSEN benchmarks.

Synthetic mode measures InstrumentHub's numerical processing throughput.
IBSEN mode measures actual serial spectrum acquisition with the existing driver.

These modes are deliberately reported separately: synthetic sample rates do not
represent the physical acquisition rate of an IBSEN interrogator.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import psutil

from app.processing.filters import butterworth_filter
from app.processing.spectral import fft_spectrum
from app.processing.statistics import statistics as signal_statistics

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports" / "benchmarks"

SYNTHETIC_RATES_HZ = (100, 500, 1000, 5000)


def percentile(values: list[float], q: float) -> float:
    """Return a percentile in milliseconds-compatible input units."""
    if not values:
        raise ValueError("Cannot calculate percentiles from an empty sequence")

    return float(np.percentile(np.asarray(values, dtype=float), q))


def environment_metadata() -> dict[str, Any]:
    """Capture enough environment information to reproduce a benchmark."""
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor() or "unknown",
        "logical_cpu_count": psutil.cpu_count(logical=True),
        "physical_cpu_count": psutil.cpu_count(logical=False),
        "numpy_version": np.__version__,
        "psutil_version": psutil.__version__,
    }


def process_metrics(
    process: psutil.Process,
    *,
    wall_seconds: float,
    cpu_seconds: float,
    initial_rss_bytes: int,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    """Build common CPU and memory metrics."""
    return {
        "wall_time_seconds": wall_seconds,
        "process_cpu_time_seconds": cpu_seconds,
        "cpu_percent_one_core": (
            100.0 * cpu_seconds / wall_seconds if wall_seconds > 0 else 0.0
        ),
        "initial_rss_bytes": initial_rss_bytes,
        "final_rss_bytes": process.memory_info().rss,
        "peak_observed_rss_bytes": peak_rss_bytes,
    }


def run_synthetic_case(
    *,
    sampling_rate_hz: int,
    duration_seconds: float,
    iterations: int,
    warmup_iterations: int,
    seed: int,
) -> dict[str, Any]:
    """Benchmark FFT, Butterworth filtering, and statistics on synthetic data."""
    sample_count = max(32, int(round(sampling_rate_hz * duration_seconds)))

    # Pre-generate the signal outside the timed processing section.
    # This isolates numerical processing from signal generation overhead.
    rng = np.random.default_rng(seed + sampling_rate_hz)
    time_axis = np.arange(sample_count, dtype=float) / sampling_rate_hz
    samples = np.sin(2.0 * np.pi * 5.0 * time_axis) + 0.1 * rng.normal(
        size=sample_count
    )

    cutoff_hz = min(20.0, sampling_rate_hz * 0.2)
    process = psutil.Process()
    initial_rss = process.memory_info().rss
    peak_rss = initial_rss

    def process_block() -> None:
        """Run actual InstrumentHub numerical processing."""
        filtered = butterworth_filter(
            samples,
            sampling_rate_hz,
            cutoff_hz,
            btype="lowpass",
            order=4,
        )
        spectrum = fft_spectrum(filtered, sampling_rate_hz)
        summary = signal_statistics(filtered)

        # Consume results so the benchmark covers the full processing path.
        if spectrum.amplitudes.size == 0 or summary.number_of_samples != sample_count:
            raise RuntimeError("Unexpected processing output")

    for _ in range(warmup_iterations):
        process_block()

    latencies_ms: list[float] = []
    cpu_start = time.process_time()
    wall_start = time.perf_counter()

    for _ in range(iterations):
        start = time.perf_counter()
        process_block()
        latencies_ms.append((time.perf_counter() - start) * 1000.0)

        # RSS is sampled after each iteration. Very short-lived allocations
        # may not be captured by this sampling method.
        peak_rss = max(peak_rss, process.memory_info().rss)

    wall_seconds = time.perf_counter() - wall_start
    cpu_seconds = time.process_time() - cpu_start

    processed_samples = sample_count * iterations
    target_block_seconds = sample_count / sampling_rate_hz
    p50_ms = percentile(latencies_ms, 50)
    p95_ms = percentile(latencies_ms, 95)
    p99_ms = percentile(latencies_ms, 99)

    metrics = process_metrics(
        process,
        wall_seconds=wall_seconds,
        cpu_seconds=cpu_seconds,
        initial_rss_bytes=initial_rss,
        peak_rss_bytes=peak_rss,
    )

    return {
        "source": "synthetic_processing",
        "sampling_rate_hz": sampling_rate_hz,
        "block_duration_seconds": duration_seconds,
        "samples_per_block": sample_count,
        "iterations": iterations,
        "warmup_iterations": warmup_iterations,
        "processed_samples": processed_samples,
        "processing_latency_p50_ms": p50_ms,
        "processing_latency_p95_ms": p95_ms,
        "processing_latency_p99_ms": p99_ms,
        "throughput_samples_per_second": (
            processed_samples / wall_seconds if wall_seconds > 0 else 0.0
        ),
        "target_block_budget_ms": target_block_seconds * 1000.0,
        "p95_meets_realtime_budget": p95_ms < target_block_seconds * 1000.0,
        **metrics,
    }


async def run_ibsen_benchmark(
    *,
    port: str,
    baudrate: int,
    iterations: int,
    warmup_iterations: int,
    expected_pixel_count: int | None,
    calibration_coefficients: list[float],
) -> dict[str, Any]:
    """Measure real serial spectrum reads using the existing IBSEN driver."""
    from app.acquisition.protocols.ibsen import IBSENCalibration
    from app.devices.instruments.ibsen import IBSENInstrument

    calibration = IBSENCalibration(
        a=calibration_coefficients[0],
        b1=calibration_coefficients[1],
        b2=calibration_coefficients[2],
        b3=calibration_coefficients[3],
        b4=calibration_coefficients[4],
        b5=calibration_coefficients[5],
    )

    instrument = IBSENInstrument.from_serial(
        device_id="ibsen-benchmark",
        name="IBSEN physical benchmark",
        port=port,
        baudrate=baudrate,
        calibration=calibration,
        expected_pixel_count=expected_pixel_count,
        metadata={"benchmark": True},
    )

    process = psutil.Process()
    initial_rss = process.memory_info().rss
    peak_rss = initial_rss
    latencies_ms: list[float] = []
    pixels_per_spectrum: int | None = expected_pixel_count

    try:
        # Connection and protocol initialization are deliberately excluded
        # from per-spectrum latency; they are reported separately.
        connect_start = time.perf_counter()
        await instrument.connect()
        connect_seconds = time.perf_counter() - connect_start

        for _ in range(warmup_iterations):
            spectrum = await instrument.read_spectrum()
            pixels_per_spectrum = spectrum.number_of_pixels

        cpu_start = time.process_time()
        wall_start = time.perf_counter()

        for _ in range(iterations):
            start = time.perf_counter()
            spectrum = await instrument.read_spectrum()
            latencies_ms.append((time.perf_counter() - start) * 1000.0)
            pixels_per_spectrum = spectrum.number_of_pixels
            peak_rss = max(peak_rss, process.memory_info().rss)

        wall_seconds = time.perf_counter() - wall_start
        cpu_seconds = time.process_time() - cpu_start

    finally:
        await instrument.disconnect()

    if pixels_per_spectrum is None:
        raise RuntimeError("IBSEN did not report its pixel count")

    total_pixels = pixels_per_spectrum * iterations
    p50_ms = percentile(latencies_ms, 50)
    p95_ms = percentile(latencies_ms, 95)
    p99_ms = percentile(latencies_ms, 99)

    metrics = process_metrics(
        process,
        wall_seconds=wall_seconds,
        cpu_seconds=cpu_seconds,
        initial_rss_bytes=initial_rss,
        peak_rss_bytes=peak_rss,
    )

    return {
        "source": "physical_ibsen_serial",
        "serial_port": port,
        "baudrate": baudrate,
        "connection_initialization_seconds": connect_seconds,
        "iterations": iterations,
        "warmup_iterations": warmup_iterations,
        "pixels_per_spectrum": pixels_per_spectrum,
        "acquired_spectra": iterations,
        "acquisition_latency_p50_ms": p50_ms,
        "acquisition_latency_p95_ms": p95_ms,
        "acquisition_latency_p99_ms": p99_ms,
        "throughput_spectra_per_second": (
            iterations / wall_seconds if wall_seconds > 0 else 0.0
        ),
        "throughput_pixels_per_second": (
            total_pixels / wall_seconds if wall_seconds > 0 else 0.0
        ),
        "nominal_sampling_rate_hz": None,
        "sampling_rate_note": (
            "Not inferred from spectrum reads. The IBSEN's physical acquisition "
            "rate must be established from device specifications or independent "
            "timing validation."
        ),
        **metrics,
    }


def write_reports(
    *,
    result: dict[str, Any],
    output_dir: Path,
    run_id: str,
) -> tuple[Path, Path]:
    """Write JSON and CSV reports for a single benchmark case."""
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "environment": environment_metadata(),
        "result": result,
    }

    json_path = output_dir / f"{run_id}.json"
    csv_path = output_dir / f"{run_id}.csv"

    json_path.write_text(
        json.dumps(metadata, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    # The CSV contains the result fields. Environment metadata remains in JSON.
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)

    return json_path, csv_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark InstrumentHub synthetic processing or physical IBSEN."
    )
    parser.add_argument(
        "--source",
        choices=("synthetic", "ibsen"),
        default="synthetic",
        help="Synthetic numerical processing or physical IBSEN serial acquisition.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=1.0,
        help="Synthetic samples represented by each processing block.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of timed iterations per synthetic rate or hardware reads.",
    )
    parser.add_argument(
        "--warmup-iterations",
        type=int,
        default=10,
        help="Untimed warm-up operations.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )

    parser.add_argument("--port", help="Physical IBSEN serial port, e.g. COM3.")
    parser.add_argument("--baudrate", type=int, default=921600)
    parser.add_argument("--expected-pixel-count", type=int)
    parser.add_argument(
        "--calibration",
        type=float,
        nargs=6,
        metavar=("A", "B1", "B2", "B3", "B4", "B5"),
        default=[1500.0, 0.1, 0.0, 0.0, 0.0, 0.0],
        help=(
            "Six wavelength calibration coefficients. The default is only a "
            "placeholder for performance tests; supply the instrument's actual "
            "calibration coefficients for scientifically meaningful wavelengths."
        ),
    )

    args = parser.parse_args()

    if args.iterations <= 0:
        parser.error("--iterations must be greater than zero")

    if args.warmup_iterations < 0:
        parser.error("--warmup-iterations cannot be negative")

    if args.duration_seconds <= 0:
        parser.error("--duration-seconds must be greater than zero")

    if args.source == "ibsen" and not args.port:
        parser.error("--port is required when --source ibsen")

    return args


def main() -> None:
    args = parse_args()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    if args.source == "synthetic":
        results = [
            run_synthetic_case(
                sampling_rate_hz=rate,
                duration_seconds=args.duration_seconds,
                iterations=args.iterations,
                warmup_iterations=args.warmup_iterations,
                seed=args.seed,
            )
            for rate in SYNTHETIC_RATES_HZ
        ]

        for index, result in enumerate(results, start=1):
            json_path, csv_path = write_reports(
                result=result,
                output_dir=args.output_dir,
                run_id=f"synthetic_{timestamp}_{index}_{result['sampling_rate_hz']}hz",
            )
            print(json.dumps(result, indent=2))
            print(f"JSON: {json_path}")
            print(f"CSV:  {csv_path}")

        return

    result = asyncio.run(
        run_ibsen_benchmark(
            port=args.port,
            baudrate=args.baudrate,
            iterations=args.iterations,
            warmup_iterations=args.warmup_iterations,
            expected_pixel_count=args.expected_pixel_count,
            calibration_coefficients=args.calibration,
        )
    )

    json_path, csv_path = write_reports(
        result=result,
        output_dir=args.output_dir,
        run_id=f"ibsen_{timestamp}",
    )

    print(json.dumps(result, indent=2))
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")


if __name__ == "__main__":
    main()

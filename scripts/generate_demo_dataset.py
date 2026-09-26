from pathlib import Path

import pandas as pd

from app.devices.generators import (
    generate_ecg,
    generate_emg,
    generate_sine,
)

OUTPUT_DIR = Path("data/examples")


def save_signal_dataset(
    filename: str,
    signal,
    sampling_rate: float,
    unit: str,
    sensor_id: str,
) -> None:
    timestamps = pd.date_range(
        start="2026-01-01T00:00:00Z",
        periods=len(signal),
        freq=pd.Timedelta(seconds=1 / sampling_rate),
    )

    dataframe = pd.DataFrame(
        {
            "timestamp": timestamps,
            "value": signal,
            "unit": unit,
            "sensor_id": sensor_id,
        }
    )

    dataframe.to_csv(
        OUTPUT_DIR / f"{filename}.csv",
        index=False,
    )

    dataframe.to_json(
        OUTPUT_DIR / f"{filename}.json",
        orient="records",
        date_format="iso",
    )

    dataframe.to_parquet(
        OUTPUT_DIR / f"{filename}.parquet",
        index=False,
    )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    sine = generate_sine(
        frequency=2.0,
        amplitude=1.0,
        sampling_rate=100.0,
        duration=10.0,
    )

    save_signal_dataset(
        filename="sine_demo",
        signal=sine,
        sampling_rate=100.0,
        unit="V",
        sensor_id="sine-demo-001",
    )

    ecg = generate_ecg(
        sampling_rate=500.0,
        duration=10.0,
        heart_rate=72.0,
        amplitude=1.0,
        noise_amplitude=0.01,
        seed=42,
    )

    save_signal_dataset(
        filename="ecg_demo",
        signal=ecg,
        sampling_rate=500.0,
        unit="mV",
        sensor_id="ecg-demo-001",
    )

    emg = generate_emg(
        sampling_rate=1000.0,
        duration=10.0,
        amplitude=1.0,
        burst_frequency=50.0,
        noise_amplitude=0.05,
        seed=42,
    )

    save_signal_dataset(
        filename="emg_demo",
        signal=emg,
        sampling_rate=1000.0,
        unit="mV",
        sensor_id="emg-demo-001",
    )


if __name__ == "__main__":
    main()

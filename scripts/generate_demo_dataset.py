from pathlib import Path

import pandas as pd

from app.devices.generators import generate_sine


def main() -> None:
    output_dir = Path("data/examples")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    sampling_rate = 100.0
    duration = 10.0

    signal = generate_sine(
        frequency=2.0,
        amplitude=1.0,
        sampling_rate=sampling_rate,
        duration=duration,
    )

    timestamps = pd.date_range(
        start="2026-01-01T00:00:00Z",
        periods=len(signal),
        freq=pd.Timedelta(seconds=1 / sampling_rate),
    )

    dataframe = pd.DataFrame(
        {
            "timestamp": timestamps,
            "value": signal,
            "unit": "V",
            "sensor_id": "demo-sensor-01",
        }
    )

    dataframe.to_csv(
        output_dir / "sine_demo.csv",
        index=False,
    )

    dataframe.to_json(
        output_dir / "sine_demo.json",
        orient="records",
        date_format="iso",
    )

    dataframe.to_parquet(
        output_dir / "sine_demo.parquet",
        index=False,
    )


if __name__ == "__main__":
    main()

from dataclasses import dataclass, field

import numpy as np  # pyright: ignore[reportMissingImports]


@dataclass(slots=True)
class Signal:
    """
    Represents a sampled signal.
    """

    samples: np.ndarray
    sampling_rate: float
    unit: str
    channel: str
    start_time: float = 0.0
    metadata: dict[str, str | float | int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sampling_rate <= 0:
            raise ValueError("sampling_rate must be greater than zero")

        if self.samples.ndim != 1:
            raise ValueError("samples must be a one-dimensional array")

        if len(self.samples) == 0:
            raise ValueError("samples cannot be empty")

        if not self.unit:
            raise ValueError("unit cannot be empty")

        if not self.channel:
            raise ValueError("channel cannot be empty")

    @property
    def duration(self) -> float:
        return len(self.samples) / self.sampling_rate

    @property
    def number_of_samples(self) -> int:
        return len(self.samples)

    def time_axis(self) -> np.ndarray:
        return np.arange(len(self.samples)) / self.sampling_rate

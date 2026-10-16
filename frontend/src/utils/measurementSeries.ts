
import type {
  Measurement,
  MeasurementSeries,
} from "../api/types";

export function buildMeasurementSeries(
  measurements: Measurement[],
  selectedDeviceIds: string[] | null = null,
  maxPoints = 600,
): MeasurementSeries[] {
  const selected = selectedDeviceIds
    ? new Set(selectedDeviceIds)
    : null;

  const groups = new Map<string, Measurement[]>();

  for (const measurement of measurements) {
    if (
      selected &&
      !selected.has(measurement.device_id)
    ) {
      continue;
    }

    const key = [
      measurement.device_id,
      measurement.channel,
      measurement.unit,
    ].join("::");

    const group = groups.get(key) ?? [];
    group.push(measurement);
    groups.set(key, group);
  }

  return [...groups.entries()]
    .map(([key, points]) => {
      const sorted = [...points].sort(
        (a, b) =>
          Date.parse(a.timestamp) - Date.parse(b.timestamp),
      );

      const recentPoints = sorted.slice(-maxPoints);
      const first = recentPoints[0];

      return {
        key,
        deviceId: first.device_id,
        channel: first.channel,
        unit: first.unit,
        label:
          `${first.device_id} / ${first.channel} (${first.unit})`,
        points: recentPoints,
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label));
}

export function estimateSamplingRate(
  measurements: Measurement[],
): number | null {
  if (measurements.length < 2) return null;

  const sorted = [...measurements].sort(
    (a, b) =>
      Date.parse(a.timestamp) - Date.parse(b.timestamp),
  );

  const intervals: number[] = [];

  for (let index = 1; index < sorted.length; index += 1) {
    const previous = Date.parse(sorted[index - 1].timestamp);
    const current = Date.parse(sorted[index].timestamp);
    const intervalSeconds = (current - previous) / 1000;

    if (
      Number.isFinite(intervalSeconds) &&
      intervalSeconds > 0
    ) {
      intervals.push(intervalSeconds);
    }
  }

  if (intervals.length === 0) return null;

  intervals.sort((a, b) => a - b);

  const middle = Math.floor(intervals.length / 2);
  const median =
    intervals.length % 2 === 0
      ? (intervals[middle - 1] + intervals[middle]) / 2
      : intervals[middle];

  return median > 0 ? 1 / median : null;
}

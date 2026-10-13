
import {
  Activity,
  ArrowUpRight,
  Bell,
  Cpu,
  FlaskConical,
  RadioTower,
  Waves,
} from "lucide-react";
import { Link } from "react-router-dom";

import {
  useDevicesQuery,
  useExperimentsQuery,
  useMeasurementsQuery,
} from "../api/queries";

import type { Measurement } from "../api/types";

function formatTimestamp(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(date);
}

function MeasurementRow({
  measurement,
}: {
  measurement: Measurement;
}) {
  return (
    <tr className="border-t border-slate-800">
      <td className="whitespace-nowrap px-4 py-3 text-slate-400">
        {formatTimestamp(measurement.timestamp)}
      </td>

      <td className="px-4 py-3 font-medium text-slate-200">
        {measurement.device_id}
      </td>

      <td className="px-4 py-3 text-slate-300">
        {measurement.channel}
      </td>

      <td className="whitespace-nowrap px-4 py-3 text-right font-mono text-slate-200">
        {measurement.value.toLocaleString(undefined, {
          maximumFractionDigits: 5,
        })}{" "}
        {measurement.unit}
      </td>

      <td className="px-4 py-3 text-slate-400">
        {measurement.quality}
      </td>
    </tr>
  );
}

function DashboardPage() {
  const devices = useDevicesQuery();
  const experiments = useExperimentsQuery();
  const measurements = useMeasurementsQuery(10);

  const metrics = [
    {
      label: "Registered devices",
      value: devices.isSuccess ? String(devices.data.length) : "—",
      description: devices.isError
        ? "Could not load devices"
        : "Persisted device records",
      icon: Cpu,
      isError: devices.isError,
    },
    {
      label: "Recent measurements",
      value: measurements.isSuccess
        ? String(measurements.data.length)
        : "—",
      description: measurements.isError
        ? "Could not load measurements"
        : "Latest records returned by the API",
      icon: Activity,
      isError: measurements.isError,
    },
    {
      label: "Experiments",
      value: experiments.isSuccess
        ? String(experiments.data.length)
        : "—",
      description: experiments.isError
        ? "Could not load experiments"
        : "Persisted experiment records",
      icon: FlaskConical,
      isError: experiments.isError,
    },
    {
      label: "Active alerts",
      value: "—",
      description: "Alerts API not implemented",
      icon: Bell,
      isError: false,
    },
  ];

  const hasQueryError =
    devices.isError ||
    experiments.isError ||
    measurements.isError;

  return (
    <div className="space-y-8">
      <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-medium text-cyan-400">
            INSTRUMENTATION WORKSPACE
          </p>

          <h2 className="mt-2 text-3xl font-bold tracking-tight text-white">
            Platform overview
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Monitor instrumentation resources and access your scientific
            data analysis tools from one workspace.
          </p>
        </div>

        <span
          className={[
            "inline-flex w-fit items-center gap-2 rounded-lg border px-3 py-2 text-sm",
            hasQueryError
              ? "border-red-400/20 bg-red-400/5 text-red-300"
              : "border-slate-800 bg-slate-900 text-slate-300",
          ].join(" ")}
          role="status"
        >
          <span
            className={[
              "h-2 w-2 rounded-full",
              hasQueryError ? "bg-red-400" : "bg-cyan-400",
            ].join(" ")}
          />
          {hasQueryError
            ? "Some API queries failed"
            : "REST integration enabled"}
        </span>
      </section>

      <section
        aria-label="Platform metrics"
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        {metrics.map((metric) => {
          const Icon = metric.icon;

          return (
            <article
              key={metric.label}
              className="rounded-xl border border-slate-800 bg-slate-900/70 p-5"
            >
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-medium text-slate-400">
                  {metric.label}
                </p>

                <span className="rounded-lg border border-slate-800 bg-slate-950 p-2 text-cyan-300">
                  <Icon size={19} strokeWidth={1.8} />
                </span>
              </div>

              <p className="mt-5 text-3xl font-semibold tracking-tight text-white">
                {metric.value}
              </p>

              <p
                className={[
                  "mt-2 text-xs",
                  metric.isError
                    ? "text-red-300"
                    : "text-slate-500",
                ].join(" ")}
              >
                {metric.description}
              </p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <article className="min-w-0 rounded-xl border border-slate-800 bg-slate-900/70 p-5 sm:p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-semibold text-white">
                Recent measurements
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Latest persisted records returned by FastAPI
              </p>
            </div>

            <Activity size={20} className="shrink-0 text-cyan-300" />
          </div>

          {measurements.isPending && (
            <p className="mt-6 text-sm text-slate-400" role="status">
              Loading measurements…
            </p>
          )}

          {measurements.isError && (
            <div
              className="mt-6 rounded-lg border border-red-400/20 bg-red-400/5 p-4"
              role="alert"
            >
              <p className="text-sm font-medium text-red-300">
                Could not load measurements
              </p>

              <p className="mt-2 break-words text-sm text-slate-400">
                {measurements.error.message}
              </p>
            </div>
          )}

          {measurements.isSuccess &&
            measurements.data.length === 0 && (
              <div className="mt-6 rounded-lg border border-dashed border-slate-700 px-5 py-8 text-center">
                <RadioTower
                  size={28}
                  className="mx-auto text-slate-600"
                />

                <p className="mt-3 text-sm font-medium text-slate-300">
                  No measurements found
                </p>

                <p className="mt-2 text-sm text-slate-500">
                  The API returned an empty measurement list.
                </p>
              </div>
            )}

          {measurements.isSuccess &&
            measurements.data.length > 0 && (
              <div className="mt-5 overflow-x-auto">
                <table className="w-full min-w-[620px] text-left text-sm">
                  <thead className="text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-4 py-3 font-medium">
                        Timestamp
                      </th>
                      <th className="px-4 py-3 font-medium">
                        Device
                      </th>
                      <th className="px-4 py-3 font-medium">
                        Channel
                      </th>
                      <th className="px-4 py-3 text-right font-medium">
                        Value
                      </th>
                      <th className="px-4 py-3 font-medium">
                        Quality
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {measurements.data.map((measurement, index) => (
                      <MeasurementRow
                        key={`${measurement.timestamp}-${measurement.device_id}-${measurement.channel}-${index}`}
                        measurement={measurement}
                      />
                    ))}
                  </tbody>
                </table>
              </div>
            )}
        </article>

        <article className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 sm:p-6">
          <h3 className="text-base font-semibold text-white">
            Data services
          </h3>

          <p className="mt-1 text-sm text-slate-400">
            Status of the dashboard data queries
          </p>

          <div className="mt-6 space-y-5">
            <div className="flex items-start gap-3">
              <span
                className={[
                  "mt-1 h-2.5 w-2.5 rounded-full",
                  devices.isError
                    ? "bg-red-400"
                    : devices.isPending
                      ? "bg-amber-400"
                      : "bg-emerald-400",
                ].join(" ")}
              />

              <div>
                <p className="text-sm font-medium text-slate-200">
                  Devices endpoint
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  {devices.isPending
                    ? "Loading device records"
                    : devices.isError
                      ? devices.error.message
                      : `${devices.data.length} device records received`}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span
                className={[
                  "mt-1 h-2.5 w-2.5 rounded-full",
                  experiments.isError
                    ? "bg-red-400"
                    : experiments.isPending
                      ? "bg-amber-400"
                      : "bg-emerald-400",
                ].join(" ")}
              />

              <div>
                <p className="text-sm font-medium text-slate-200">
                  Experiments endpoint
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  {experiments.isPending
                    ? "Loading experiment records"
                    : experiments.isError
                      ? experiments.error.message
                      : `${experiments.data.length} experiment records received`}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span
                className={[
                  "mt-1 h-2.5 w-2.5 rounded-full",
                  measurements.isError
                    ? "bg-red-400"
                    : measurements.isPending
                      ? "bg-amber-400"
                      : "bg-emerald-400",
                ].join(" ")}
              />

              <div>
                <p className="text-sm font-medium text-slate-200">
                  Measurements endpoint
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  {measurements.isPending
                    ? "Loading recent measurements"
                    : measurements.isError
                      ? measurements.error.message
                      : `${measurements.data.length} recent records received`}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-7 border-t border-slate-800 pt-5">
            <h4 className="text-sm font-semibold text-slate-200">
              Scientific workspaces
            </h4>

            <div className="mt-4 grid gap-3">
              <Link
                to="/spectrum"
                className="flex items-center justify-between rounded-lg border border-slate-800 p-3 text-sm text-slate-300 hover:border-cyan-400/40 hover:bg-slate-950"
              >
                Spectrum
                <Waves size={17} className="text-cyan-300" />
              </Link>

              <Link
                to="/live-acquisition"
                className="flex items-center justify-between rounded-lg border border-slate-800 p-3 text-sm text-slate-300 hover:border-cyan-400/40 hover:bg-slate-950"
              >
                Live Acquisition
                <ArrowUpRight
                  size={17}
                  className="text-cyan-300"
                />
              </Link>
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}

export default DashboardPage;

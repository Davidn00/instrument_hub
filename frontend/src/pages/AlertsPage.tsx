
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";

import { apiRequest } from "../api/client";

interface AlertEvent {
  id: string;
  timestamp: string;
  device_id: string;
  channel: string | null;
  severity: "INFO" | "WARNING" | "CRITICAL" | string;
  message: string;
  value: number | null;
  acknowledged: boolean;
  metadata: Record<string, unknown>;
}

function severityClass(severity: string): string {
  // Use distinct visual treatment for critical and warning conditions.
  if (severity === "CRITICAL") {
    return "border-red-500/30 bg-red-500/10 text-red-300";
  }

  if (severity === "WARNING") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  }

  return "border-slate-700 bg-slate-800 text-slate-300";
}

export default function AlertsPage() {
  const queryClient = useQueryClient();

  const alertsQuery = useQuery({
    queryKey: ["alerts"],
    queryFn: () => apiRequest<AlertEvent[]>("alerts?limit=200"),
    // Poll the backend so newly persisted alerts appear automatically.
    refetchInterval: 5000,
  });

  async function acknowledge(alert: AlertEvent) {
    await apiRequest<AlertEvent>(
      `alerts/${alert.id}/acknowledge`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ acknowledged: !alert.acknowledged }),
      },
    );

    await queryClient.invalidateQueries({ queryKey: ["alerts"] });
  }

  const alerts = alertsQuery.data ?? [];
  const activeCount = alerts.filter((item) => !item.acknowledged).length;
  const criticalCount = alerts.filter(
    (item) => !item.acknowledged && item.severity === "CRITICAL",
  ).length;

  return (
    <main className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-cyan-400">
            InstrumentHub / Monitoring
          </p>
          <h1 className="mt-2 text-3xl font-bold text-white">
            Alert center
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Review threshold violations and acknowledge alert events.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void alertsQuery.refetch()}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </header>

      <section className="grid gap-4 sm:grid-cols-3">
        <article className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">Total loaded</p>
          <p className="mt-2 text-3xl font-semibold text-white">
            {alerts.length}
          </p>
        </article>

        <article className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">Unacknowledged</p>
          <p className="mt-2 text-3xl font-semibold text-amber-300">
            {activeCount}
          </p>
        </article>

        <article className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">Critical and unacknowledged</p>
          <p className="mt-2 text-3xl font-semibold text-red-300">
            {criticalCount}
          </p>
        </article>
      </section>

      {alertsQuery.isPending ? (
        <p className="text-sm text-slate-400">Loading alert history...</p>
      ) : alertsQuery.isError ? (
        <section className="rounded-xl border border-red-900 bg-red-950/30 p-5">
          <p className="font-medium text-red-300">
            Could not load alerts
          </p>
          <p className="mt-2 text-sm text-slate-400">
            {alertsQuery.error.message}
          </p>
        </section>
      ) : alerts.length === 0 ? (
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-10 text-center">
          <CheckCircle2 className="mx-auto text-emerald-400" size={30} />
          <h2 className="mt-3 font-semibold text-white">
            No alert events
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Alerts will appear here when an enabled rule is triggered.
          </p>
        </section>
      ) : (
        <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
          <div className="border-b border-slate-800 px-5 py-4">
            <h2 className="font-semibold text-white">Alert history</h2>
          </div>

          <div className="divide-y divide-slate-800">
            {alerts.map((alert) => (
              <article key={alert.id} className="space-y-3 p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-semibold ${severityClass(alert.severity)}`}
                  >
                    {alert.severity}
                  </span>

                  <time className="text-xs text-slate-500">
                    {new Date(alert.timestamp).toLocaleString()}
                  </time>
                </div>

                <p className="font-medium text-white">{alert.message}</p>

                <p className="text-sm text-slate-400">
                  Device: {alert.device_id}
                  {" · "}
                  Channel: {alert.channel ?? "N/A"}
                  {" · "}
                  Value: {alert.value ?? "N/A"}
                </p>

                <div className="flex items-center justify-between gap-3">
                  <span className="text-xs text-slate-500">
                    {alert.acknowledged
                      ? "Acknowledged"
                      : "Awaiting acknowledgement"}
                  </span>

                  <button
                    type="button"
                    onClick={() => void acknowledge(alert)}
                    className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800"
                  >
                    {alert.acknowledged ? "Reopen" : "Acknowledge"}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      <div className="flex items-center gap-2 text-xs text-slate-500">
        <AlertTriangle size={14} />
        Alert acknowledgement does not confirm that the physical condition
        has returned to a safe range.
      </div>
    </main>
  );
}

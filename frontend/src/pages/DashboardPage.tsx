
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

const metrics = [
  {
    label: "Registered devices",
    value: "—",
    description: "Awaiting API integration",
    icon: Cpu,
  },
  {
    label: "Measurements",
    value: "—",
    description: "Historical measurement data",
    icon: Activity,
  },
  {
    label: "Experiments",
    value: "—",
    description: "Experiment records",
    icon: FlaskConical,
  },
  {
    label: "Active alerts",
    value: "—",
    description: "Alert monitoring pending",
    icon: Bell,
  },
];

const quickActions = [
  {
    title: "Devices",
    description: "Inspect and manage instrumentation devices.",
    path: "/devices",
    icon: Cpu,
  },
  {
    title: "Live Acquisition",
    description: "Prepare the real-time acquisition workspace.",
    path: "/live-acquisition",
    icon: RadioTower,
  },
  {
    title: "Spectrum",
    description: "Explore the scientific spectrum viewer.",
    path: "/spectrum",
    icon: Waves,
  },
];

function DashboardPage() {
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

        <span className="inline-flex w-fit items-center gap-2 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-300">
          <span className="h-2 w-2 rounded-full bg-amber-400" />
          Awaiting backend integration
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

              <p className="mt-2 text-xs text-slate-500">
                {metric.description}
              </p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <article className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 sm:p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-semibold text-white">
                Acquisition overview
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Real-time acquisition summary
              </p>
            </div>

            <Activity size={20} className="text-cyan-300" />
          </div>

          <div className="mt-6 flex min-h-48 flex-col items-center justify-center rounded-lg border border-dashed border-slate-700 bg-slate-950/60 px-5 py-8 text-center">
            <RadioTower size={30} className="text-slate-600" />

            <h4 className="mt-4 text-sm font-medium text-slate-300">
              No acquisition data available
            </h4>

            <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
              Connect the frontend to the InstrumentHub API to display
              actual measurements and acquisition status.
            </p>

            <Link
              to="/live-acquisition"
              className="mt-5 inline-flex items-center gap-2 rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition-colors hover:bg-cyan-300"
            >
              Open acquisition
              <ArrowUpRight size={16} />
            </Link>
          </div>
        </article>

        <article className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 sm:p-6">
          <h3 className="text-base font-semibold text-white">
            Platform status
          </h3>

          <p className="mt-1 text-sm text-slate-400">
            Frontend integration checklist
          </p>

          <div className="mt-6 space-y-4">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 h-2.5 w-2.5 rounded-full bg-cyan-400" />

              <div>
                <p className="text-sm font-medium text-slate-200">
                  Dashboard interface
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Layout and navigation are available.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="mt-0.5 h-2.5 w-2.5 rounded-full bg-amber-400" />

              <div>
                <p className="text-sm font-medium text-slate-200">
                  REST API integration
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Planned for Part 29C.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="mt-0.5 h-2.5 w-2.5 rounded-full bg-amber-400" />

              <div>
                <p className="text-sm font-medium text-slate-200">
                  Real-time data stream
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Frontend WebSocket integration is pending.
                </p>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section>
        <div className="mb-4">
          <h3 className="text-base font-semibold text-white">
            Quick access
          </h3>

          <p className="mt-1 text-sm text-slate-400">
            Navigate to a workspace module.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {quickActions.map((action) => {
            const Icon = action.icon;

            return (
              <Link
                key={action.path}
                to={action.path}
                className="group rounded-xl border border-slate-800 bg-slate-900/50 p-5 transition-colors hover:border-cyan-400/40 hover:bg-slate-900"
              >
                <div className="flex items-center justify-between">
                  <span className="rounded-lg bg-slate-800 p-2.5 text-cyan-300">
                    <Icon size={20} />
                  </span>

                  <ArrowUpRight
                    size={18}
                    className="text-slate-500 transition-colors group-hover:text-cyan-300"
                  />
                </div>

                <h4 className="mt-5 text-sm font-semibold text-white">
                  {action.title}
                </h4>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  {action.description}
                </p>
              </Link>
            );
          })}
        </div>
      </section>
    </div>
  );
}

export default DashboardPage;

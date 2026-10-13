
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  Cable,
  ChartNoAxesCombined,
  Cpu,
  Download,
  FlaskConical,
  LayoutDashboard,
  RadioTower,
  Waves,
  X,
} from "lucide-react";
import { NavLink } from "react-router-dom";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navigation = [
  {
    label: "OVERVIEW",
    items: [
      {
        name: "Dashboard",
        path: "/",
        icon: LayoutDashboard,
      },
    ],
  },
  {
    label: "INSTRUMENTATION",
    items: [
      {
        name: "Devices",
        path: "/devices",
        icon: Cpu,
      },
      {
        name: "Live Acquisition",
        path: "/live-acquisition",
        icon: RadioTower,
      },
      {
        name: "Spectrum",
        path: "/spectrum",
        icon: Waves,
      },
      {
        name: "Time Series",
        path: "/time-series",
        icon: Activity,
      },
      {
        name: "FFT Analysis",
        path: "/fft",
        icon: BarChart3,
      },
      {
        name: "FBG Analysis",
        path: "/fbg-analysis",
        icon: ChartNoAxesCombined,
      },
    ],
  },
  {
    label: "WORKSPACE",
    items: [
      {
        name: "Experiments",
        path: "/experiments",
        icon: FlaskConical,
      },
      {
        name: "Alerts",
        path: "/alerts",
        icon: AlertTriangle,
      },
      {
        name: "Export",
        path: "/export",
        icon: Download,
      },
    ],
  },
];

function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <aside
      id="instrumenthub-sidebar"
      aria-label="Main navigation"
      className={[
        "fixed inset-y-0 left-0 z-40 flex w-64 flex-col",
        "border-r border-slate-800 bg-slate-950 text-slate-100",
        "transition-transform duration-200 ease-in-out",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:static lg:z-auto lg:translate-x-0 lg:flex-shrink-0",
      ].join(" ")}
    >
      <div className="flex h-20 items-center justify-between border-b border-slate-800 px-5">
        <NavLink
          to="/"
          onClick={onClose}
          className="flex items-center gap-3"
          aria-label="InstrumentHub home"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500 text-slate-950">
            <Activity size={23} strokeWidth={2.5} />
          </span>

          <span>
            <span className="block text-lg font-bold tracking-tight">
              InstrumentHub
            </span>
            <span className="block text-xs text-slate-400">
              Instrumentation platform
            </span>
          </span>
        </NavLink>

        <button
          type="button"
          onClick={onClose}
          className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
          aria-label="Close navigation"
        >
          <X size={20} />
        </button>
      </div>

      <nav className="flex-1 space-y-7 overflow-y-auto px-3 py-6">
        {navigation.map((group) => (
          <section key={group.label}>
            <h2 className="mb-3 px-3 text-xs font-semibold tracking-[0.16em] text-slate-500">
              {group.label}
            </h2>

            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === "/"}
                    onClick={onClose}
                    className={({ isActive }) =>
                      [
                        "flex items-center gap-3 rounded-lg px-3 py-2.5",
                        "text-sm font-medium transition-colors",
                        isActive
                          ? "bg-cyan-400/10 text-cyan-300 ring-1 ring-inset ring-cyan-400/20"
                          : "text-slate-400 hover:bg-slate-900 hover:text-slate-100",
                      ].join(" ")
                    }
                  >
                    <Icon size={18} strokeWidth={1.8} />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </div>
          </section>
        ))}
      </nav>

      <div className="border-t border-slate-800 p-4">
        <div className="flex items-center gap-3 rounded-lg bg-slate-900 p-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-800 text-cyan-300">
            <Cable size={18} />
          </span>

          <div className="min-w-0">
            <p className="text-sm font-medium text-slate-200">
              Development
            </p>
            <p className="text-xs text-slate-500">
              API integration pending
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;

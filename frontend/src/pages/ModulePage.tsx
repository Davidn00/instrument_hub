
import type { LucideIcon } from "lucide-react";
import { ArrowLeft, Construction } from "lucide-react";
import { Link } from "react-router-dom";

interface ModulePageProps {
  title: string;
  description: string;
  icon: LucideIcon;
  stage: string;
  features: string[];
}

function ModulePage({
  title,
  description,
  icon: Icon,
  stage,
  features,
}: ModulePageProps) {
  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-cyan-400">
          InstrumentHub / Workspace
        </p>

        <div className="mt-3 flex items-start gap-4">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-slate-800 bg-slate-900 text-cyan-300">
            <Icon size={24} />
          </span>

          <div>
            <h2 className="text-3xl font-bold tracking-tight text-white">
              {title}
            </h2>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
              {description}
            </p>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-6 sm:p-8">
        <div className="flex items-center gap-3">
          <Construction size={22} className="text-amber-400" />

          <span className="text-sm font-medium text-amber-300">
            Implementation in progress
          </span>
        </div>

        <h3 className="mt-5 text-lg font-semibold text-white">
          Module preparation
        </h3>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          This module has a navigation route and a dedicated page.
          Its operational features will be implemented in the corresponding
          stage of InstrumentHub.
        </p>

        <div className="mt-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Planned functionality
          </p>

          <ul className="mt-4 space-y-3">
            {features.map((feature) => (
              <li
                key={feature}
                className="flex items-start gap-3 text-sm text-slate-300"
              >
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-400" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-8 border-t border-slate-800 pt-5">
          <p className="text-xs text-slate-500">
            Planned implementation: {stage}
          </p>

          <Link
            to="/"
            className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-cyan-300 hover:text-cyan-200"
          >
            <ArrowLeft size={16} />
            Back to dashboard
          </Link>
        </div>
      </section>
    </div>
  );
}

export default ModulePage;

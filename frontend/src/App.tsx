
function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <header className="mb-10">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            Instrumentation platform
          </p>

          <h1 className="mt-3 text-4xl font-bold tracking-tight">
            InstrumentHub
          </h1>

          <p className="mt-3 max-w-2xl text-slate-400">
            Acquisition, monitoring and scientific analysis of instrument data.
          </p>
        </header>

        <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <article className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">Platform</p>
            <h2 className="mt-2 text-xl font-semibold">Dashboard</h2>
            <p className="mt-2 text-sm text-slate-400">
              Your instrumentation workspace.
            </p>
          </article>

          <article className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">Acquisition</p>
            <h2 className="mt-2 text-xl font-semibold">Devices</h2>
            <p className="mt-2 text-sm text-slate-400">
              Device management will be added next.
            </p>
          </article>

          <article className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">Visualization</p>
            <h2 className="mt-2 text-xl font-semibold">Live data</h2>
            <p className="mt-2 text-sm text-slate-400">
              Real-time charts will be integrated in a later part.
            </p>
          </article>
        </section>

        <footer className="mt-12 border-t border-slate-800 pt-5 text-sm text-slate-500">
          InstrumentHub · Development environment
        </footer>
      </div>
    </main>
  );
}

export default App;

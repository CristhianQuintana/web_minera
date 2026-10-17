"use client";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="grid min-h-screen place-items-center p-6 text-center">
      <div>
        <h1 className="text-2xl font-semibold">Algo salió mal</h1>
        <p className="mt-2 text-muted">No pudimos completar la solicitud.</p>
        <div className="mt-4 flex justify-center gap-3">
          <button className="rounded-xl bg-primary px-4 py-2 text-white" onClick={reset}>
            Reintentar
          </button>
          <a href="/dashboard" className="rounded-xl border border-border px-4 py-2">
            Volver al inicio
          </a>
        </div>
      </div>
    </main>
  );
}

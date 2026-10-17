import Link from "next/link";

export default function NotFound() {
  return (
    <main className="grid min-h-screen place-items-center p-6 text-center">
      <div>
        <h1 className="text-2xl font-semibold">Página no encontrada</h1>
        <p className="mt-2 text-muted">El recurso solicitado no existe o ya no está disponible.</p>
        <Link href="/dashboard" className="mt-4 inline-block text-primary">
          Volver al inicio
        </Link>
      </div>
    </main>
  );
}

import Link from "next/link";

export default function ForbiddenPage() {
  return (
    <main className="grid min-h-screen place-items-center p-6 text-center">
      <div>
        <h1 className="text-2xl font-semibold">Acceso no autorizado</h1>
        <p className="mt-2 text-muted">No tienes permisos para consultar este recurso.</p>
        <Link href="/dashboard" className="mt-4 inline-block text-primary">
          Volver al inicio
        </Link>
      </div>
    </main>
  );
}

"use client";

import { activateAccountUseCase, validateInvitationUseCase } from "@/composition/container";
import { Button, Input } from "@/shared/components/ui";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

function ActivateForm() {
  const token = useSearchParams().get("token") ?? "";
  const [info, setInfo] = useState<{ full_name: string; email: string } | null>(null);
  const [error, setError] = useState("");
  const [done, setDone] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      setError("Esta invitación ya no es válida.");
      return;
    }
    validateInvitationUseCase(token)
      .then((result) => {
        setInfo(result);
        setFullName(result.full_name);
      })
      .catch(() => setError("Esta invitación ya no es válida."));
  }, [token]);

  if (error) {
    return (
      <section className="w-full max-w-md rounded-3xl border border-border bg-white p-8">
        <h1 className="text-2xl font-semibold">Invitación no válida</h1>
        <p className="mt-2 text-sm text-muted">{error} El enlace expiró o ya fue utilizado.</p>
        <Link href="/login" className="mt-6 inline-block text-sm text-primary">
          Ir al inicio de sesión
        </Link>
      </section>
    );
  }

  return (
    <section className="w-full max-w-md rounded-3xl border border-border bg-white p-8">
      <h1 className="text-2xl font-semibold">Activar cuenta</h1>
      <form
        className="mt-6 space-y-4"
        onSubmit={async (event) => {
          event.preventDefault();
          if (password !== confirm) {
            setError("Las contraseñas no coinciden.");
            return;
          }
          setLoading(true);
          try {
            const result = await activateAccountUseCase({ token, full_name: fullName, password });
            setDone(result.message);
          } catch (err) {
            setError(err instanceof Error ? err.message : "No pudimos activar la cuenta.");
          } finally {
            setLoading(false);
          }
        }}
      >
        <Input label="Nombre" value={fullName} onChange={(event) => setFullName(event.target.value)} required />
        <Input label="Correo" value={info?.email ?? ""} readOnly />
        <Input label="Nueva contraseña" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        <Input label="Confirmar contraseña" type="password" value={confirm} onChange={(event) => setConfirm(event.target.value)} required />
        <Button type="submit" className="w-full" loading={loading}>
          Activar cuenta
        </Button>
      </form>
      {done ? (
        <div className="mt-4 text-sm text-success">
          {done}
          <Link href="/login" className="mt-2 block text-primary">
            Ir al inicio de sesión
          </Link>
        </div>
      ) : null}
    </section>
  );
}

export default function ActivatePage() {
  return (
    <main className="grid min-h-screen place-items-center p-4">
      <Suspense fallback={<p>Validando invitación...</p>}>
        <ActivateForm />
      </Suspense>
    </main>
  );
}

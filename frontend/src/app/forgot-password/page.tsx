"use client";

import { forgotPasswordUseCase } from "@/composition/container";
import { Button, Input } from "@/shared/components/ui";
import Link from "next/link";
import { useState } from "react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  return (
    <main className="grid min-h-screen place-items-center p-4">
      <section className="animate-fade-up w-full max-w-md rounded-3xl border border-border bg-white p-8">
        <h1 className="text-2xl font-semibold">Recuperar acceso</h1>
        <form
          className="mt-6 space-y-4"
          onSubmit={async (event) => {
            event.preventDefault();
            setLoading(true);
            await forgotPasswordUseCase(email);
            setSent(true);
            setLoading(false);
          }}
        >
          <Input label="Correo electrónico" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <Button type="submit" className="w-full" loading={loading}>
            Enviar instrucciones
          </Button>
        </form>
        {sent ? (
          <p className="mt-4 text-sm text-muted">
            Si existe una cuenta asociada a este correo, recibirás instrucciones para recuperar el acceso.
          </p>
        ) : null}
        <Link href="/login" className="mt-6 inline-block text-sm text-primary">
          Volver al inicio de sesión
        </Link>
      </section>
    </main>
  );
}

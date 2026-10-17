"use client";

import { loginUseCase } from "@/composition/container";
import { ApiError } from "@/adapters/outbound/api/http-client";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { Button, Input } from "@/shared/components/ui";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { loginSchema, type LoginFormValues } from "@/application/dto/login-schema";

export default function LoginPage() {
  const router = useRouter();
  const setUser = useSessionStore((state) => state.setUser);
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: LoginFormValues) {
    setMessage("");
    try {
      const result = await loginUseCase(values.email, values.password);
      setUser(result.user);
      router.replace("/dashboard");
    } catch (error) {
      const fallback = "No pudimos completar el inicio de sesión. Intenta nuevamente.";
      setMessage(error instanceof ApiError ? error.message : fallback);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-gradient-to-br from-slate-50 to-teal-50 p-4">
      <section className="animate-fade-up w-full max-w-md rounded-3xl border border-border bg-white p-8 shadow-[var(--shadow)]">
        <p className="text-sm font-semibold tracking-wide text-primary">WEB_MINERA</p>
        <h1 className="mt-2 text-2xl font-semibold">Iniciar sesión</h1>
        <p className="mt-1 text-sm text-muted">Acceso exclusivo por invitación del administrador.</p>
        <form className="mt-6 space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
          <Input
            label="Correo electrónico"
            type="email"
            hint="usuario@dominio.com"
            error={form.formState.errors.email?.message}
            {...form.register("email")}
          />
          <Input
            label="Contraseña"
            type={showPassword ? "text" : "password"}
            error={form.formState.errors.password?.message}
            {...form.register("password")}
          />
          <label className="flex items-center gap-2 text-sm text-muted">
            <input type="checkbox" checked={showPassword} onChange={(event) => setShowPassword(event.target.checked)} />
            Mostrar contraseña
          </label>
          <Link href="/forgot-password" className="block text-sm text-primary hover:underline">
            ¿Olvidaste tu contraseña?
          </Link>
          <Button type="submit" className="w-full" loading={form.formState.isSubmitting}>
            {form.formState.isSubmitting ? "Ingresando..." : "Ingresar"}
          </Button>
          {message ? <p className="text-sm text-error">{message}</p> : null}
          <p className="text-xs text-muted">
            Acceso de demostración: cristhian@gmail.com / Cristhian123
          </p>
        </form>
      </section>
    </main>
  );
}

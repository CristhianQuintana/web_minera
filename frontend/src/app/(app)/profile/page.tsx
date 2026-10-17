"use client";

import { api } from "@/adapters/outbound/api/http-client";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { PageHeader } from "@/presentation/layouts/app-shell";
import { Button, Card, Input } from "@/shared/components/ui";
import { useState } from "react";

export default function ProfilePage() {
  const user = useSessionStore((state) => state.user);
  const setUser = useSessionStore((state) => state.setUser);
  const [name, setName] = useState(user?.full_name ?? "");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  return (
    <div>
      <PageHeader title="Perfil" description="Datos de la cuenta activa." />
      <Card className="max-w-lg">
        <form
          className="space-y-4"
          onSubmit={async (event) => {
            event.preventDefault();
            setLoading(true);
            await api("/api/v1/profile", {
              method: "PATCH",
              body: JSON.stringify({ full_name: name }),
            });
            if (user) setUser({ ...user, full_name: name });
            setMessage("Perfil actualizado correctamente.");
            setLoading(false);
          }}
        >
          <Input label="Nombre" value={name} onChange={(event) => setName(event.target.value)} />
          <Input label="Correo" value={user?.email ?? ""} readOnly />
          <Input label="Rol" value={user?.role_label ?? ""} readOnly />
          <Button type="submit" loading={loading}>
            Guardar
          </Button>
          {message ? <p className="text-sm text-success">{message}</p> : null}
        </form>
      </Card>
    </div>
  );
}

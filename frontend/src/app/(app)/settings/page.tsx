"use client";

import { platform } from "@/composition/container";
import { PageHeader, PermissionGate } from "@/presentation/layouts/app-shell";
import { Button, Card, Input } from "@/shared/components/ui";
import { formatDateTime } from "@/shared/utils/format";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

export default function SettingsPage() {
  const client = useQueryClient();
  const query = useQuery({ queryKey: ["settings"], queryFn: () => platform.get<Record<string, unknown>>("/api/v1/settings") });
  const [value, setValue] = useState("3");
  const mutation = useMutation({
    mutationFn: () =>
      platform.post("/api/v1/settings/tolerances", {
        rule_key: "mass_balance_percent",
        name: "Tolerancia de balance de masas",
        value: Number(value),
        unit: "percent",
      }),
    onSuccess: () => client.invalidateQueries({ queryKey: ["settings"] }),
  });

  const tolerances = (query.data?.tolerances as Array<Record<string, unknown>>) ?? [];

  return (
    <PermissionGate permission="manage_settings">
      <PageHeader title="Configuración" description="General, seguridad, tolerancias versionadas y auditoría." />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="font-semibold">Tolerancias</h2>
          <p className="mt-1 text-sm text-muted">Las reglas no se sobrescriben: se crea una nueva versión.</p>
          <div className="mt-4 space-y-3">
            <Input label="Nuevo valor (%)" type="number" value={value} onChange={(event) => setValue(event.target.value)} />
            <Button loading={mutation.isPending} onClick={() => mutation.mutate()}>
              Guardar nueva versión
            </Button>
          </div>
          <ul className="mt-6 space-y-2 text-sm">
            {tolerances.map((rule) => (
              <li key={String(rule.id)} className="rounded-xl border border-border p-3">
                <p className="font-medium">
                  {String(rule.name)} · v{String(rule.version)} {rule.is_active ? "(vigente)" : ""}
                </p>
                <p className="text-muted">
                  {String(rule.value)} {String(rule.unit)} · {formatDateTime(String(rule.created_at))}
                </p>
              </li>
            ))}
          </ul>
        </Card>
        <Card>
          <h2 className="font-semibold">General</h2>
          <p className="mt-2 text-sm text-muted">Zona horaria: America/Bogota</p>
          <p className="text-sm text-muted">Integraciones: Supabase Auth + Storage.</p>
        </Card>
      </div>
    </PermissionGate>
  );
}

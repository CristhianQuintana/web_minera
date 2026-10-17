"use client";

import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import Link from "next/link";
import { Button } from "@/shared/components/ui";

export default function AuditPage() {
  return (
    <PermissionGate permission="view_audit">
      <ResourcePage
        title="Auditoría"
        description="Registro de acciones, actores y resultados."
        queryKey="audits"
        path="/api/v1/audits"
        emptyTitle="No hay eventos de auditoría."
        emptyDescription="Las acciones relevantes quedarán registradas aquí."
        columns={[
          { key: "created_at", label: "Fecha" },
          { key: "user_id", label: "Actor" },
          { key: "action", label: "Acción" },
          { key: "entity", label: "Entidad" },
          { key: "entity_id", label: "Identificador" },
          { key: "result", label: "Resultado" },
        ]}
        detailTitle="Evento de auditoría"
        extraActions={(row) =>
          row.lot_id ? (
            <Link href={`/audit/cases/${row.lot_id}`}>
              <Button variant="secondary">Expediente</Button>
            </Link>
          ) : null
        }
        renderDetail={(row) => (
          <div>
            <Field label="Acción" value={String(row.action)} />
            <Field label="Entidad" value={String(row.entity)} />
            <Field label="Identificador" value={String(row.entity_id ?? "—")} />
            <Field label="Resultado" value={String(row.result ?? "—")} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

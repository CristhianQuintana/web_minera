"use client";

import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import Link from "next/link";
import { Button } from "@/shared/components/ui";
import { formatDateTime } from "@/shared/utils/format";

function AuditDetail({ row }: Readonly<{ row: Record<string, unknown> }>) {
  return (
    <div>
      <Field label="Acción / operación" value={String(row.action)} />
      <Field label="Entidad" value={String(row.entity)} />
      <Field label="Registro afectado" value={String(row.entity_id ?? "—")} />
      <Field label="Usuario (id)" value={String(row.user_id ?? "—")} />
      <Field label="Usuario" value={String(row.actor_name ?? row.actor_email ?? "—")} />
      <Field label="Rol" value={String(row.actor_role ?? "—")} />
      <Field label="Resultado" value={String(row.result ?? "—")} />
      <Field label="Fecha y hora" value={formatDateTime(String(row.created_at ?? ""))} />
      <Field label="Lote asociado" value={row.lot_id ? String(row.lot_id) : "—"} />
      {row.lot_id ? (
        <div className="mt-4">
          <Link href={`/audit/cases/${String(row.lot_id)}`}>
            <Button variant="secondary">Abrir expediente</Button>
          </Link>
        </div>
      ) : null}
    </div>
  );
}

function renderAuditDetail(row: Record<string, unknown>) {
  return <AuditDetail row={row} />;
}

function auditExtraActions(row: Record<string, unknown>) {
  if (!row.lot_id) return null;
  return (
    <Link href={`/audit/cases/${String(row.lot_id)}`}>
      <Button variant="secondary">Expediente</Button>
    </Link>
  );
}

export default function AuditPage() {
  return (
    <PermissionGate permission="view_audit">
      <ResourcePage
        title="Auditoría"
        description="Registro de acciones relevantes: usuario, fecha, operación y resultado."
        queryKey="audits"
        path="/api/v1/audits"
        emptyTitle="No hay eventos de auditoría."
        emptyDescription="Las acciones relevantes quedarán registradas aquí."
        columns={[
          { key: "created_at", label: "Fecha" },
          {
            key: "actor_name",
            label: "Usuario",
            render: (row) => String(row.actor_name ?? row.user_id ?? "—"),
          },
          { key: "action", label: "Operación" },
          { key: "entity", label: "Entidad" },
          { key: "entity_id", label: "Registro" },
          { key: "result", label: "Resultado" },
        ]}
        detailTitle="Evento de auditoría"
        extraActions={auditExtraActions}
        renderDetail={renderAuditDetail}
      />
    </PermissionGate>
  );
}

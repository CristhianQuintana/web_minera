"use client";

import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import Link from "next/link";
import { Button } from "@/shared/components/ui";
import { formatDateTime } from "@/shared/utils/format";

function AuditDetail({ row }: Readonly<{ row: Record<string, unknown> }>) {
  const context = (row.context as Record<string, unknown> | undefined) ?? {};
  const actorName = String(row.actor_name ?? context.actor_name ?? "—");
  const actorEmail = String(row.actor_email ?? context.actor_email ?? "—");
  const actorRole = String(row.actor_role ?? context.actor_role ?? "—");
  return (
    <div>
      <Field label="Tipo de operación" value={String(row.action)} />
      <Field label="Entidad" value={String(row.entity)} />
      <Field label="Registro afectado" value={String(row.entity_id ?? "—")} />
      <Field label="Usuario responsable" value={`${actorName}${actorEmail !== "—" ? ` · ${actorEmail}` : ""}`} />
      <Field label="Rol" value={actorRole} />
      <Field label="Identificador de usuario" value={String(row.user_id ?? "—")} />
      <Field label="Fecha y hora" value={formatDateTime(String(row.created_at ?? ""))} />
      <Field label="Resultado" value={String(row.result ?? "—")} />
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
        description="Consulta las acciones relevantes registradas: usuario responsable, fecha, tipo de operación y registro afectado."
        queryKey="audits"
        path="/api/v1/audits"
        searchPlaceholder="Buscar por operación, entidad o usuario"
        emptyTitle="No hay eventos de auditoría."
        emptyDescription="Al crear o modificar un registro, el evento aparecerá aquí con usuario, fecha y operación."
        columns={[
          { key: "created_at", label: "Fecha y hora" },
          {
            key: "actor_name",
            label: "Usuario responsable",
            render: (row) => {
              const context = (row.context as Record<string, unknown> | undefined) ?? {};
              return String(row.actor_name ?? context.actor_name ?? row.actor_email ?? context.actor_email ?? row.user_id ?? "—");
            },
          },
          { key: "action", label: "Tipo de operación" },
          { key: "entity", label: "Entidad" },
          { key: "entity_id", label: "Registro afectado" },
          { key: "result", label: "Resultado" },
        ]}
        detailTitle="Evento de auditoría"
        extraActions={auditExtraActions}
        renderDetail={renderAuditDetail}
      />
    </PermissionGate>
  );
}

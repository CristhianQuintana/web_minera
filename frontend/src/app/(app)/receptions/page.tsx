"use client";

import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { formatQuantity } from "@/shared/utils/format";

export default function ReceptionsPage() {
  const user = useSessionStore((state) => state.user);
  return (
    <PermissionGate permission="view_receptions">
      <ResourcePage
        title="Recepción"
        description="Recepciones confirmadas y pendientes de pesaje."
        queryKey="receptions"
        path="/api/v1/receptions"
        canCreate={Boolean(user?.permissions.includes("register_reception"))}
        createLabel="Registrar recepción"
        createPath="/api/v1/receptions"
        emptyTitle="No hay recepciones registradas."
        emptyDescription="Las recepciones sincronizadas desde campo aparecerán aquí."
        columns={[
          { key: "lot_id", label: "Lote" },
          { key: "responsible", label: "Receptor" },
          { key: "occurred_at", label: "Fecha" },
          { key: "declared_quantity", label: "Declarada" },
          { key: "received_quantity", label: "Recibida" },
          { key: "status", label: "Estado" },
        ]}
        detailTitle="Detalle de recepción"
        createForm={({ onSubmit, loading }) => (
          <SimpleForm
            loading={loading}
            onSubmit={onSubmit}
            fields={[
              { name: "lot_id", label: "ID de lote" },
              { name: "declared_quantity", label: "Cantidad declarada", type: "number" },
              { name: "received_quantity", label: "Cantidad recibida", type: "number" },
              { name: "unit", label: "Unidad" },
              { name: "responsible", label: "Responsable" },
            ]}
          />
        )}
        renderDetail={(row) => (
          <div>
            <Field label="Lote" value={String(row.lot_id)} />
            <Field label="Declarada" value={formatQuantity(Number(row.declared_quantity), String(row.unit))} />
            <Field label="Recibida" value={formatQuantity(Number(row.received_quantity), String(row.unit))} />
            <Field label="Responsable" value={String(row.responsible)} />
            <Field label="Estado" value={String(row.status)} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

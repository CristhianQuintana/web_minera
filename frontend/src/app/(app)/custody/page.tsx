"use client";

import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { formatDateTime, formatQuantity } from "@/shared/utils/format";

export default function CustodyPage() {
  const user = useSessionStore((state) => state.user);
  return (
    <PermissionGate permission="view_custody">
      <ResourcePage
        title="Custodia"
        description="Transferencias de cadena de custodia."
        queryKey="custody"
        path="/api/v1/custody"
        canCreate={Boolean(user?.permissions.includes("transfer_custody"))}
        createLabel="Registrar transferencia"
        createPath="/api/v1/custody"
        emptyTitle="No hay transferencias registradas."
        emptyDescription="Las transferencias de custodia aparecerán aquí."
        columns={[
          { key: "lot_id", label: "Lote" },
          { key: "origin", label: "Origen" },
          { key: "destination", label: "Destino" },
          { key: "quantity", label: "Cantidad" },
          { key: "occurred_at", label: "Fecha" },
          { key: "status", label: "Estado" },
        ]}
        detailTitle="Detalle de custodia"
        createForm={({ onSubmit, loading }) => (
          <SimpleForm
            loading={loading}
            onSubmit={onSubmit}
            fields={[
              { name: "lot_id", label: "ID de lote" },
              { name: "origin", label: "Origen" },
              { name: "destination", label: "Destino" },
              { name: "quantity", label: "Cantidad", type: "number" },
              { name: "notes", label: "Observación" },
            ]}
          />
        )}
        renderDetail={(row) => (
          <div>
            <Field label="Lote" value={String(row.lot_id)} />
            <Field label="Origen" value={String(row.origin)} />
            <Field label="Destino" value={String(row.destination)} />
            <Field label="Cantidad" value={formatQuantity(Number(row.quantity), "kg")} />
            <Field label="Fecha" value={formatDateTime(String(row.occurred_at))} />
            <Field label="Responsable" value={String(row.responsible ?? "—")} />
            <Field label="Estado" value={String(row.status)} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

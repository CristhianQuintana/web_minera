"use client";

import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { formatQuantity } from "@/shared/utils/format";

export default function WeighingsPage() {
  const user = useSessionStore((state) => state.user);
  return (
    <PermissionGate permission="view_receptions">
      <ResourcePage
        title="Pesajes"
        description="Registros de pesaje asociados a lotes y recepciones."
        queryKey="weighings"
        path="/api/v1/weighings"
        canCreate={Boolean(user?.permissions.includes("register_weighing"))}
        createLabel="Registrar pesaje"
        createPath="/api/v1/weighings"
        emptyTitle="No hay pesajes registrados."
        emptyDescription="Los pesajes de planta aparecerán aquí."
        columns={[
          { key: "lot_id", label: "Lote" },
          { key: "responsible", label: "Receptor" },
          { key: "occurred_at", label: "Fecha" },
          { key: "weight", label: "Cantidad" },
          { key: "instrument", label: "Instrumento" },
        ]}
        detailTitle="Detalle de pesaje"
        createForm={({ onSubmit, loading }) => (
          <SimpleForm
            loading={loading}
            onSubmit={onSubmit}
            fields={[
              { name: "lot_id", label: "ID de lote" },
              { name: "weight", label: "Peso", type: "number" },
              { name: "unit", label: "Unidad" },
              { name: "instrument", label: "Instrumento" },
              { name: "responsible", label: "Responsable" },
            ]}
          />
        )}
        renderDetail={(row) => (
          <div>
            <Field label="Lote" value={String(row.lot_id)} />
            <Field label="Peso" value={formatQuantity(Number(row.weight), String(row.unit))} />
            <Field label="Instrumento" value={String(row.instrument)} />
            <Field label="Responsable" value={String(row.responsible)} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

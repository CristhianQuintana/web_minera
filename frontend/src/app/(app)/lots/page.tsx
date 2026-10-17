"use client";

import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { formatDateTime, formatQuantity } from "@/shared/utils/format";

export default function LotsPage() {
  const user = useSessionStore((state) => state.user);
  return (
    <PermissionGate permission="view_lots">
      <ResourcePage
        title="Lotes"
        description="Registro digital, evidencias y trazabilidad de lotes."
        queryKey="lots"
        path="/api/v1/lots"
        searchPlaceholder="Código, QR o mineral"
        canCreate={Boolean(user?.permissions.includes("register_lot"))}
        canExport={Boolean(user?.permissions.includes("export"))}
        createLabel="Registrar lote"
        createPath="/api/v1/lots"
        emptyTitle="No hay lotes registrados."
        emptyDescription="Cuando se registre un lote, aparecerá aquí."
        statuses={[
          { value: "registered", label: "Registrado" },
          { value: "inTransit", label: "En custodia" },
          { value: "transferred", label: "Transferido" },
          { value: "received", label: "Recibido" },
          { value: "closed", label: "Cerrado" },
        ]}
        columns={[
          { key: "code", label: "Código" },
          { key: "created_at", label: "Fecha" },
          { key: "mineral", label: "Mineral" },
          { key: "quantity", label: "Cantidad" },
          { key: "status", label: "Estado" },
        ]}
        detailTitle="Detalle del lote"
        createForm={({ onSubmit, loading }) => (
          <SimpleForm
            loading={loading}
            submitLabel="Guardar"
            onSubmit={onSubmit}
            fields={[
              { name: "code", label: "Código" },
              { name: "mineral", label: "Mineral" },
              { name: "quantity", label: "Cantidad", type: "number" },
              { name: "unit", label: "Unidad" },
              { name: "observation", label: "Observación" },
            ]}
          />
        )}
        renderDetail={(row) => (
          <div>
            <Field label="Código" value={String(row.code)} />
            <Field label="Estado" value={String(row.status)} />
            <Field label="Mineral" value={String(row.mineral)} />
            <Field label="Cantidad" value={formatQuantity(Number(row.quantity), String(row.unit))} />
            <Field label="Fecha" value={formatDateTime(String(row.created_at))} />
            <Field label="QR" value={String(row.qr_payload ?? row.code)} />
            <Field label="Ubicación" value={row.latitude ? `${row.latitude}, ${row.longitude}` : "—"} />
            <h3 className="mt-6 font-semibold">Evidencias</h3>
            <p className="text-sm text-muted">{Array.isArray(row.evidences) ? `${row.evidences.length} archivos` : "Sin evidencias"}</p>
            <h3 className="mt-4 font-semibold">Cadena de custodia</h3>
            <p className="text-sm text-muted">{Array.isArray(row.custody) ? `${row.custody.length} transferencias` : "—"}</p>
          </div>
        )}
      />
    </PermissionGate>
  );
}

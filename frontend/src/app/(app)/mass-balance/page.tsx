"use client";

import { platform } from "@/composition/container";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import { Button } from "@/shared/components/ui";
import { formatQuantity, labelOf } from "@/shared/utils/format";

export default function MassBalancePage() {
  return (
    <PermissionGate permission="view_balance">
      <ResourcePage
        title="Balance de masas"
        description="Comparación entre cantidad de origen y cantidad recibida."
        queryKey="mass-balance"
        path="/api/v1/mass-balance"
        emptyTitle="No hay balances calculados."
        emptyDescription="El balance se genera al registrar una recepción."
        columns={[
          { key: "lot_id", label: "Lote" },
          { key: "origin_quantity", label: "Origen" },
          { key: "received_quantity", label: "Recibida" },
          { key: "difference", label: "Diferencia" },
          { key: "tolerance_value", label: "Tolerancia" },
          { key: "status", label: "Estado" },
        ]}
        detailTitle="Detalle de balance"
        extraActions={(row, helpers) => (
          <Button
            variant="secondary"
            onClick={async () => {
              try {
                await platform.post(`/api/v1/mass-balance/${row.lot_id}/recalculate`);
                helpers.push("Balance recalculado correctamente.");
                helpers.refresh();
              } catch (error) {
                helpers.push(error instanceof Error ? error.message : "No se pudo recalcular.", "error");
              }
            }}
          >
            Recalcular
          </Button>
        )}
        renderDetail={(row) => (
          <div>
            <Field label="Cantidad de origen" value={formatQuantity(Number(row.origin_quantity), "kg")} />
            <Field label="Cantidad recibida" value={formatQuantity(Number(row.received_quantity), "kg")} />
            <Field label="Diferencia" value={row.difference != null ? `${row.difference} (${row.difference_percent}%)` : "—"} />
            <Field label="Tolerancia" value={`${row.tolerance_value} ${row.tolerance_unit} · v${row.tolerance_version ?? "—"}`} />
            <Field label="Estado" value={labelOf(String(row.status))} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

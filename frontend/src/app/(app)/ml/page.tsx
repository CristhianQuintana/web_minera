"use client";

import { platform } from "@/composition/container";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import { Button } from "@/shared/components/ui";
import { formatQuantity, labelOf } from "@/shared/utils/format";

export default function MLPage() {
  return (
    <PermissionGate permission="view_ml">
      <ResourcePage
        title="Análisis ML"
        description="Estimaciones de cantidad esperada y señales para revisión. No constituyen fraude ni sentencia."
        queryKey="ml-inferences"
        path="/api/v1/ml/inferences"
        emptyTitle="No hay inferencias."
        emptyDescription="Las estimaciones versionadas aparecerán aquí."
        columns={[
          { key: "lot_id", label: "Lote" },
          { key: "model_version", label: "Versión" },
          { key: "expected_quantity", label: "Esperada" },
          { key: "observed_quantity", label: "Observada" },
          { key: "deviation_percent", label: "Desviación" },
          { key: "signal", label: "Señal" },
        ]}
        detailTitle="Detalle de inferencia"
        extraActions={(row, helpers) => (
          <Button
            variant="secondary"
            onClick={async () => {
              try {
                await platform.post(`/api/v1/ml/estimate/${row.lot_id}`);
                helpers.push("Estimación registrada como señal para revisión.");
                helpers.refresh();
              } catch (error) {
                helpers.push(error instanceof Error ? error.message : "No se pudo estimar.", "error");
              }
            }}
          >
            Estimar
          </Button>
        )}
        renderDetail={(row) => (
          <div>
            <Field label="Lote" value={String(row.lot_id)} />
            <Field label="Modelo" value={String(row.model_version)} />
            <Field label="Cantidad esperada" value={formatQuantity(Number(row.expected_quantity), "kg")} />
            <Field label="Cantidad observada" value={formatQuantity(Number(row.observed_quantity), "kg")} />
            <Field label="Desviación estimada" value={row.deviation_percent != null ? `${row.deviation_percent}%` : "—"} />
            <Field label="Señal" value={labelOf(String(row.signal))} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

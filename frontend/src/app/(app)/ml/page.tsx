"use client";

import { platform } from "@/composition/container";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import { Button } from "@/shared/components/ui";
import { formatQuantity, labelOf } from "@/shared/utils/format";

type ActionHelpers = { refresh: () => void; push: (text: string, tone?: "success" | "error") => void };

function MLDetail({ row }: Readonly<{ row: Record<string, unknown> }>) {
  const features = (row.features as Record<string, unknown> | undefined) ?? {};
  return (
    <div>
      <Field label="Lote" value={String(features.lot_code ?? row.lot_id)} />
      <Field label="Mineral" value={String(features.mineral ?? "—")} />
      <Field label="Modelo" value={String(row.model_version)} />
      <Field label="Origen" value={formatQuantity(Number(features.origin_quantity ?? 0), "kg")} />
      <Field label="Cantidad esperada" value={formatQuantity(Number(row.expected_quantity), "kg")} />
      <Field
        label="Cantidad observada"
        value={row.observed_quantity == null ? "—" : formatQuantity(Number(row.observed_quantity), "kg")}
      />
      <Field
        label="Desviación estimada"
        value={row.deviation_percent != null ? `${Number(row.deviation_percent).toFixed(2)}%` : "—"}
      />
      <Field label="Señal" value={labelOf(String(row.signal))} />
      <Field label="Fuente" value={String(features.source ?? "—")} />
      <Field label="Fecha" value={String(row.created_at ?? "—")} />
    </div>
  );
}

function mlExtraActions(row: Record<string, unknown>, helpers: ActionHelpers) {
  return (
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
  );
}

function renderMLDetail(row: Record<string, unknown>) {
  return <MLDetail row={row} />;
}

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
          {
            key: "lot_code",
            label: "Lote",
            render: (row) =>
              String((row.features as Record<string, unknown> | undefined)?.lot_code ?? row.lot_id ?? "—"),
          },
          { key: "model_version", label: "Versión" },
          {
            key: "expected_quantity",
            label: "Esperada",
            render: (row) => formatQuantity(Number(row.expected_quantity), "kg"),
          },
          {
            key: "observed_quantity",
            label: "Observada",
            render: (row) =>
              row.observed_quantity == null ? "—" : formatQuantity(Number(row.observed_quantity), "kg"),
          },
          {
            key: "deviation_percent",
            label: "Desviación",
            render: (row) => (row.deviation_percent != null ? `${Number(row.deviation_percent).toFixed(2)}%` : "—"),
          },
          {
            key: "signal",
            label: "Señal",
            render: (row) => labelOf(String(row.signal)),
          },
        ]}
        detailTitle="Detalle de inferencia"
        extraActions={mlExtraActions}
        renderDetail={renderMLDetail}
      />
    </PermissionGate>
  );
}

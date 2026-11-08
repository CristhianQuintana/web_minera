"use client";

import { platform } from "@/composition/container";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import { Button } from "@/shared/components/ui";
import { formatQuantity, labelOf } from "@/shared/utils/format";

type ActionHelpers = { refresh: () => void; push: (text: string, tone?: "success" | "error") => void };

function RecalculateAction({
  row,
  helpers,
}: Readonly<{
  row: Record<string, unknown>;
  helpers: ActionHelpers;
}>) {
  return (
    <Button
      variant="secondary"
      onClick={async () => {
        try {
          await platform.post(`/api/v1/mass-balance/${String(row.lot_id)}/recalculate`);
          helpers.push("Balance recalculado correctamente.");
          helpers.refresh();
        } catch (error) {
          helpers.push(error instanceof Error ? error.message : "No se pudo recalcular.", "error");
        }
      }}
    >
      Recalcular
    </Button>
  );
}

function BalanceDetail({ row }: Readonly<{ row: Record<string, unknown> }>) {
  const difference =
    row.difference != null ? `${String(row.difference)} (${String(row.difference_percent)}%)` : "—";
  return (
    <div>
      <Field label="Lote" value={String(row.lot_code ?? row.lot_id)} />
      <Field label="Mineral" value={String(row.mineral ?? "—")} />
      <Field label="Cantidad de origen" value={formatQuantity(Number(row.origin_quantity), "kg")} />
      <Field
        label="Cantidad recibida"
        value={row.received_quantity == null ? "—" : formatQuantity(Number(row.received_quantity), "kg")}
      />
      <Field label="Diferencia" value={difference} />
      <Field
        label="Tolerancia"
        value={`${String(row.tolerance_value)} ${String(row.tolerance_unit)} · v${String(row.tolerance_version ?? "—")}`}
      />
      <Field label="Estado" value={labelOf(String(row.status))} />
    </div>
  );
}

function massBalanceExtraActions(row: Record<string, unknown>, helpers: ActionHelpers) {
  return <RecalculateAction row={row} helpers={helpers} />;
}

function renderBalanceDetail(row: Record<string, unknown>) {
  return <BalanceDetail row={row} />;
}

export default function MassBalancePage() {
  return (
    <PermissionGate permission="view_balance">
      <ResourcePage
        title="Balance de masas"
        description="Comparación entre cantidad de origen y cantidad recibida."
        queryKey="mass-balance"
        path="/api/v1/mass-balance"
        emptyTitle="No hay lotes para balance."
        emptyDescription="El balance se calcula automáticamente al comparar origen del lote con la recepción."
        statuses={[
          { value: "within_tolerance", label: "Dentro de tolerancia" },
          { value: "review_required", label: "Requiere revisión" },
          { value: "insufficient_data", label: "Datos insuficientes" },
        ]}
        columns={[
          {
            key: "lot_code",
            label: "Lote",
            render: (row) => String(row.lot_code ?? row.lot_id ?? "—"),
          },
          {
            key: "origin_quantity",
            label: "Origen",
            render: (row) => formatQuantity(Number(row.origin_quantity), "kg"),
          },
          {
            key: "received_quantity",
            label: "Recibida",
            render: (row) =>
              row.received_quantity == null ? "—" : formatQuantity(Number(row.received_quantity), "kg"),
          },
          {
            key: "difference",
            label: "Diferencia",
            render: (row) =>
              row.difference == null
                ? "—"
                : `${String(row.difference)} (${String(row.difference_percent ?? "—")}%)`,
          },
          {
            key: "tolerance_value",
            label: "Tolerancia",
            render: (row) => `${String(row.tolerance_value ?? "—")} ${String(row.tolerance_unit ?? "")}`.trim(),
          },
          {
            key: "status",
            label: "Estado",
            render: (row) => labelOf(String(row.status)),
          },
        ]}
        detailTitle="Detalle de balance"
        extraActions={massBalanceExtraActions}
        renderDetail={renderBalanceDetail}
      />
    </PermissionGate>
  );
}

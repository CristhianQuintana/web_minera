"use client";

import { platform } from "@/composition/container";
import { PageHeader, PermissionGate, StatusBadge } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { Button, Card, ErrorState, Input, Skeleton } from "@/shared/components/ui";
import { formatDateTime, formatQuantity, labelOf } from "@/shared/utils/format";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

type ActionHelpers = { refresh: () => void; push: (text: string, tone?: "success" | "error") => void };

function MLDetail({ row }: Readonly<{ row: Record<string, unknown> }>) {
  const features = (row.features as Record<string, unknown> | undefined) ?? {};
  return (
    <div>
      <Field label="Lote" value={String(features.lot_code ?? row.lot_id)} />
      <Field label="Mineral" value={String(features.mineral ?? "—")} />
      <Field label="Modelo" value={String(row.model_version)} />
      <Field label="Cantidad esperada" value={formatQuantity(Number(row.expected_quantity), "kg")} />
      <Field
        label="Cantidad observada"
        value={row.observed_quantity == null ? "—" : formatQuantity(Number(row.observed_quantity), "kg")}
      />
      <Field
        label="Desviación"
        value={row.deviation_percent != null ? `${Number(row.deviation_percent).toFixed(2)}%` : "—"}
      />
      <Field label="Señal revisable" value={labelOf(String(row.signal))} />
      <Field label="Fecha" value={formatDateTime(String(row.created_at ?? ""))} />
      <p className="mt-4 text-xs text-muted">La señal es revisable y no constituye una decisión automática definitiva.</p>
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
          helpers.push("Señal ML generada para revisión.");
          helpers.refresh();
        } catch (error) {
          helpers.push(error instanceof Error ? error.message : "No se pudo estimar.", "error");
        }
      }}
    >
      Regenerar señal
    </Button>
  );
}

function renderMLDetail(row: Record<string, unknown>) {
  return <MLDetail row={row} />;
}

function GenerateSignalPanel() {
  const client = useQueryClient();
  const [lotId, setLotId] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const mutation = useMutation({
    mutationFn: () => platform.post<Record<string, unknown>>(`/api/v1/ml/estimate/${lotId.trim()}`),
    onSuccess: (data) => {
      setMessage(
        `Señal generada (${String(data.signal)}) · esperada ${String(data.expected_quantity)} · observada ${String(data.observed_quantity ?? "—")}`,
      );
      client.invalidateQueries({ queryKey: ["ml-inferences"] });
      client.invalidateQueries({ queryKey: ["alerts"] });
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "No se pudo generar la señal."),
  });
  return (
    <Card>
      <h2 className="font-semibold">Generar señal revisable</h2>
      <p className="mt-1 text-sm text-muted">
        Ejecuta el modelo sobre un lote. El resultado es una señal para revisión humana, no una sentencia.
      </p>
      <div className="mt-4 flex flex-wrap items-end gap-3">
        <div className="min-w-[260px] flex-1">
          <Input label="ID de lote" value={lotId} onChange={(event) => setLotId(event.target.value)} />
        </div>
        <Button loading={mutation.isPending} disabled={!lotId.trim()} onClick={() => mutation.mutate()}>
          Ejecutar análisis ML
        </Button>
      </div>
      {message ? <p className="mt-3 text-sm text-muted">{message}</p> : null}
    </Card>
  );
}

function ModelsPanel() {
  const user = useSessionStore((state) => state.user);
  const canManage = Boolean(user?.permissions.includes("manage_settings"));
  const client = useQueryClient();
  const models = useQuery({
    queryKey: ["ml-models"],
    queryFn: () => platform.list<Record<string, unknown>>("/api/v1/ml/models", { page_size: 50 }),
  });
  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: "active" | "archived" }) =>
      platform.post(`/api/v1/ml/models/${id}/status`, { status }),
    onSuccess: () => client.invalidateQueries({ queryKey: ["ml-models"] }),
  });

  if (models.isLoading) return <Skeleton className="h-48" />;
  if (models.isError) return <ErrorState message="No se pudieron cargar los modelos." onRetry={() => models.refetch()} />;

  const items = models.data?.items ?? [];
  return (
    <Card>
      <h2 className="font-semibold">Versiones y desempeño del modelo</h2>
      <p className="mt-1 text-sm text-muted">Consulta métricas, estado y versión registrada de cada modelo.</p>
      <ul className="mt-4 space-y-3">
        {items.map((model) => {
          const metrics = (model.metrics as Record<string, unknown> | undefined) ?? {};
          return (
            <li key={String(model.id)} className="rounded-xl border border-border p-3">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium">
                    {String(model.name)} · v{String(model.version)}
                  </p>
                  <p className="text-sm text-muted">
                    Estado: <StatusBadge value={String(model.status)} /> · Registrado{" "}
                    {formatDateTime(String(model.registered_at ?? ""))}
                  </p>
                  <div className="mt-2 grid gap-1 text-sm text-muted sm:grid-cols-3">
                    <span>MAE: {String(metrics.mae ?? metrics.MAE ?? "—")}</span>
                    <span>MAPE: {String(metrics.mape ?? metrics.MAPE ?? "—")}</span>
                    <span>RMSE: {String(metrics.rmse ?? metrics.RMSE ?? "—")}</span>
                  </div>
                </div>
                {canManage ? (
                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      loading={statusMutation.isPending}
                      onClick={() => statusMutation.mutate({ id: String(model.id), status: "active" })}
                    >
                      Activar
                    </Button>
                    <Button
                      variant="secondary"
                      loading={statusMutation.isPending}
                      onClick={() => statusMutation.mutate({ id: String(model.id), status: "archived" })}
                    >
                      Archivar
                    </Button>
                  </div>
                ) : null}
              </div>
            </li>
          );
        })}
      </ul>
      {!items.length ? <p className="mt-3 text-sm text-muted">No hay modelos registrados.</p> : null}
    </Card>
  );
}

export default function MLPage() {
  const user = useSessionStore((state) => state.user);
  const canEstimate = Boolean(user?.permissions.includes("estimate_ml"));
  return (
    <PermissionGate permission="view_ml">
      <PageHeader
        title="Análisis ML"
        description="Comparación esperada vs observada, señales revisables, métricas y versiones del modelo."
      />
      <div className="mb-6 grid gap-4 lg:grid-cols-2">
        {canEstimate ? <GenerateSignalPanel /> : null}
        <ModelsPanel />
      </div>
      <ResourcePage
        title="Inferencias y señales"
        description="Resultados del modelo asociados a lotes. Úsalos como apoyo a la revisión."
        queryKey="ml-inferences"
        path="/api/v1/ml/inferences"
        emptyTitle="No hay inferencias."
        emptyDescription="Genera una señal con el ID de un lote o desde un registro existente."
        statuses={[
          { value: "review_signal", label: "Señal revisable" },
          { value: "none", label: "Sin señal" },
        ]}
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
        detailTitle="Comparación esperada vs observada"
        extraActions={canEstimate ? mlExtraActions : undefined}
        renderDetail={renderMLDetail}
      />
    </PermissionGate>
  );
}

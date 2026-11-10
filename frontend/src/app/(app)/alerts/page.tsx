"use client";

import { platform } from "@/composition/container";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { Button, Input } from "@/shared/components/ui";
import { formatDateTime } from "@/shared/utils/format";
import Link from "next/link";
import { useState } from "react";

type ActionHelpers = { refresh: () => void; push: (text: string, tone?: "success" | "error") => void };

function AlertDetail({ row }: Readonly<{ row: Record<string, unknown> }>) {
  const reviews = (row.reviews as Array<Record<string, unknown>> | undefined) ?? [];
  return (
    <div>
      <Field label="Resumen" value={String(row.title)} />
      <Field label="Motivo" value={String(row.reason ?? row.summary ?? "—")} />
      <Field label="Tipo" value={String(row.alert_type ?? "—")} />
      <Field label="Severidad" value={String(row.severity ?? "—")} />
      <Field label="Regla aplicada" value={String(row.rule_applied ?? "—")} />
      <Field label="Lote" value={row.lot_id ? String(row.lot_id) : "—"} />
      <Field label="Resultado ML" value={row.ml_inference_id ? String(row.ml_inference_id) : "Sin inferencia"} />
      <Field label="Estado" value={String(row.status)} />
      <Field label="Fecha" value={formatDateTime(String(row.created_at ?? ""))} />
      {row.lot_id ? (
        <div className="mt-4">
          <Link href={`/audit/cases/${String(row.lot_id)}`}>
            <Button variant="secondary">Ver expediente del lote</Button>
          </Link>
        </div>
      ) : null}
      <h3 className="mt-6 font-semibold">Atenciones registradas</h3>
      {!reviews.length ? (
        <p className="mt-2 text-sm text-muted">Sin atenciones previas.</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {reviews.map((item) => (
            <li key={String(item.id)} className="rounded-xl border border-border px-3 py-2 text-sm">
              <p className="font-medium">{String(item.result)}</p>
              <p className="text-muted">{String(item.observation ?? "Sin observación")}</p>
              <p className="text-xs text-muted">{formatDateTime(String(item.created_at ?? ""))}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ReviewAction({
  row,
  onDone,
  mode,
}: Readonly<{
  row: Record<string, unknown>;
  onDone: ActionHelpers;
  mode: "review" | "close";
}>) {
  const [open, setOpen] = useState(false);
  const [result, setResult] = useState(mode === "close" ? "Cierre de revisión" : "");
  const [observation, setObservation] = useState("");
  const [loading, setLoading] = useState(false);
  const alertId = String(row.id);
  const status = String(row.status ?? "");
  if (mode === "review" && ["attended", "closed"].includes(status)) return null;
  if (mode === "close" && status === "closed") return null;
  if (mode === "close" && !["attended", "in_review", "new"].includes(status)) return null;

  return (
    <>
      <Button variant={mode === "close" ? "danger" : "secondary"} onClick={() => setOpen(true)}>
        {mode === "close" ? "Cerrar revisión" : "Atender alerta"}
      </Button>
      {open ? (
        <div className="fixed inset-0 z-[55] grid place-items-center p-4">
          <button className="absolute inset-0 bg-[var(--overlay)]" onClick={() => setOpen(false)} />
          <form
            className="relative w-full max-w-md space-y-4 rounded-2xl bg-white p-6"
            onSubmit={async (event) => {
              event.preventDefault();
              setLoading(true);
              try {
                const path =
                  mode === "close" ? `/api/v1/alerts/${alertId}/close` : `/api/v1/alerts/${alertId}/review`;
                await platform.post(path, {
                  result,
                  observation,
                  close: mode === "close",
                });
                onDone.push(mode === "close" ? "Revisión cerrada correctamente." : "Atención registrada correctamente.");
                onDone.refresh();
                setOpen(false);
              } catch (error) {
                onDone.push(error instanceof Error ? error.message : "No se pudo guardar.", "error");
              } finally {
                setLoading(false);
              }
            }}
          >
            <h3 className="text-lg font-semibold">{mode === "close" ? "Cerrar revisión" : "Atender alerta"}</h3>
            <p className="text-sm text-muted">{String(row.title)}</p>
            <Input label="Resultado de revisión" value={result} onChange={(event) => setResult(event.target.value)} required />
            <Input
              label="Observación / acciones realizadas"
              value={observation}
              onChange={(event) => setObservation(event.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button type="button" variant="secondary" onClick={() => setOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit" loading={loading} variant={mode === "close" ? "danger" : "primary"}>
                {loading ? "Guardando..." : mode === "close" ? "Confirmar cierre" : "Guardar atención"}
              </Button>
            </div>
          </form>
        </div>
      ) : null}
    </>
  );
}

function alertExtraActions(row: Record<string, unknown>, helpers: ActionHelpers) {
  return (
    <div className="flex flex-wrap gap-2">
      <ReviewAction row={row} onDone={helpers} mode="review" />
      <ReviewAction row={row} onDone={helpers} mode="close" />
    </div>
  );
}

function renderAlertDetail(row: Record<string, unknown>) {
  return <AlertDetail row={row} />;
}

export default function AlertsPage() {
  const user = useSessionStore((state) => state.user);
  const canReview = Boolean(user?.permissions.includes("review_alert"));
  return (
    <PermissionGate permission="view_alerts">
      <ResourcePage
        title="Alertas"
        description="Señales operativas para revisión. No constituyen sentencia."
        queryKey="alerts"
        path="/api/v1/alerts"
        emptyTitle="No hay alertas."
        emptyDescription="Las desviaciones y señales revisables aparecerán aquí."
        statuses={[
          { value: "new", label: "Nueva" },
          { value: "in_review", label: "En revisión" },
          { value: "attended", label: "Atendida" },
          { value: "closed", label: "Cerrada" },
        ]}
        columns={[
          { key: "severity", label: "Severidad" },
          { key: "alert_type", label: "Tipo" },
          { key: "lot_id", label: "Lote" },
          { key: "created_at", label: "Fecha" },
          { key: "status", label: "Estado" },
          { key: "title", label: "Resumen" },
        ]}
        detailTitle="Detalle de alerta"
        extraActions={canReview ? alertExtraActions : undefined}
        renderDetail={renderAlertDetail}
      />
    </PermissionGate>
  );
}

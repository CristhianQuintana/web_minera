"use client";

import { platform } from "@/composition/container";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage } from "@/presentation/modules/resource-page";
import { Button, Input } from "@/shared/components/ui";
import { useState } from "react";

export default function AlertsPage() {
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
        detailTitle="Revisar alerta"
        extraActions={(row, helpers) => <ReviewAction alertId={String(row.id)} onDone={helpers} />}
        renderDetail={(row) => (
          <div>
            <Field label="Resumen" value={String(row.title)} />
            <Field label="Motivo" value={String(row.reason ?? row.summary ?? "—")} />
            <Field label="Regla aplicada" value={String(row.rule_applied ?? "—")} />
            <Field label="Resultado ML" value={row.ml_inference_id ? String(row.ml_inference_id) : "Sin inferencia"} />
            <Field label="Estado" value={String(row.status)} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

function ReviewAction({
  alertId,
  onDone,
}: {
  alertId: string;
  onDone: { refresh: () => void; push: (text: string, tone?: "success" | "error") => void };
}) {
  const [open, setOpen] = useState(false);
  const [result, setResult] = useState("");
  const [observation, setObservation] = useState("");
  const [loading, setLoading] = useState(false);
  return (
    <>
      <Button variant="secondary" onClick={() => setOpen(true)}>
        Revisar
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
                await platform.post(`/api/v1/alerts/${alertId}/review`, { result, observation });
                onDone.push("Revisión registrada correctamente.");
                onDone.refresh();
                setOpen(false);
              } catch (error) {
                onDone.push(error instanceof Error ? error.message : "No se pudo guardar.", "error");
              } finally {
                setLoading(false);
              }
            }}
          >
            <h3 className="text-lg font-semibold">Atender alerta</h3>
            <Input label="Resultado de revisión" value={result} onChange={(event) => setResult(event.target.value)} required />
            <Input label="Observación" value={observation} onChange={(event) => setObservation(event.target.value)} />
            <div className="flex justify-end gap-2">
              <Button type="button" variant="secondary" onClick={() => setOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit" loading={loading}>
                {loading ? "Guardando..." : "Guardar revisión"}
              </Button>
            </div>
          </form>
        </div>
      ) : null}
    </>
  );
}

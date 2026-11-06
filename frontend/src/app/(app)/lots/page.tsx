"use client";

import { parseForm, registerLotSchema } from "@/application/dto/resource-schemas";
import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { useDetail } from "@/shared/hooks/use-platform";
import { formatDateTime, formatQuantity } from "@/shared/utils/format";
import { ErrorState, Skeleton } from "@/shared/components/ui";

type TimelineItem = {
  id?: string;
  event_type?: string;
  occurred_at?: string;
  notes?: string;
  user_id?: string;
};

function LotTimeline({ lotId }: Readonly<{ lotId: string }>) {
  const timeline = useDetail<{ items: TimelineItem[] }>(
    "lot-timeline",
    `/api/v1/lots/${lotId}/timeline`,
  );
  if (timeline.isLoading) return <Skeleton className="mt-3 h-24 w-full" />;
  if (timeline.isError) {
    return <ErrorState message="No se pudo cargar el historial." onRetry={() => timeline.refetch()} />;
  }
  const items = timeline.data?.items ?? [];
  if (!items.length) {
    return <p className="mt-2 text-sm text-muted">Sin eventos registrados.</p>;
  }
  return (
    <ol className="mt-3 space-y-3 border-l border-border pl-4">
      {items.map((event, index) => (
        <li key={String(event.id ?? index)} className="relative">
          <span className="absolute -left-[1.28rem] mt-1.5 h-2.5 w-2.5 rounded-full bg-primary" aria-hidden />
          <p className="text-sm font-medium text-text">{event.event_type ?? "evento"}</p>
          <p className="text-xs text-muted">{formatDateTime(String(event.occurred_at ?? ""))}</p>
          {event.notes ? <p className="text-sm text-muted">{event.notes}</p> : null}
        </li>
      ))}
    </ol>
  );
}

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
            validate={(body) => {
              const parsed = parseForm(registerLotSchema, body);
              if (!parsed.ok) return parsed;
              return { ok: true, data: parsed.data as Record<string, unknown> };
            }}
            onSubmit={onSubmit}
            fields={[
              { name: "code", label: "Código" },
              { name: "mineral", label: "Mineral" },
              { name: "quantity", label: "Cantidad", type: "number" },
              { name: "unit", label: "Unidad" },
              { name: "observation", label: "Observación", required: false },
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
            <Field
              label="Ubicación"
              value={row.latitude != null && row.longitude != null ? `${String(row.latitude)}, ${String(row.longitude)}` : "—"}
            />
            <h3 className="mt-6 font-semibold">Evidencias</h3>
            <p className="text-sm text-muted">
              {Array.isArray(row.evidences) ? `${row.evidences.length} archivos (consulta WEB; carga desde APP_MINERA)` : "Sin evidencias"}
            </p>
            <h3 className="mt-4 font-semibold">Cadena de custodia</h3>
            <p className="text-sm text-muted">{Array.isArray(row.custody) ? `${row.custody.length} transferencias` : "—"}</p>
            <h3 className="mt-4 font-semibold">Historial / timeline</h3>
            <LotTimeline lotId={String(row.id)} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

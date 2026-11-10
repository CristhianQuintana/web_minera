"use client";

import { parseForm, registerLotSchema, transportSchema } from "@/application/dto/resource-schemas";
import { platform } from "@/composition/container";
import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { useDetail } from "@/shared/hooks/use-platform";
import { formatDateTime, formatQuantity } from "@/shared/utils/format";
import { Button, ErrorState, Skeleton } from "@/shared/components/ui";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

type TimelineItem = {
  id?: string;
  event_type?: string;
  occurred_at?: string;
  notes?: string;
  user_id?: string;
};

type CreateFormArgs = {
  onSubmit: (body: Record<string, unknown>) => void;
  loading: boolean;
};

type ActionHelpers = { refresh: () => void; push: (text: string, tone?: "success" | "error") => void };

type CarrierOption = { id: string; full_name?: string; email?: string; role?: string };

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

function LotsCreateForm({ onSubmit, loading }: Readonly<CreateFormArgs>) {
  return (
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
  );
}

function LotDetail({ row }: Readonly<{ row: Record<string, unknown> }>) {
  const transports = Array.isArray(row.transports) ? (row.transports as Array<Record<string, unknown>>) : [];
  return (
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
      <h3 className="mt-4 font-semibold">Transportes asignados</h3>
      {!transports.length ? (
        <p className="text-sm text-muted">Sin transportes. Usa «Asignar transportista» para registrar uno.</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {transports.map((item) => (
            <li key={String(item.id)} className="rounded-xl border border-border px-3 py-2 text-sm">
              <p className="font-medium">
                {String(item.code ?? item.id)} · {String(item.driver ?? "—")}
              </p>
              <p className="text-muted">
                {String(item.vehicle ?? "—")} · {String(item.plate ?? "—")} · estado {String(item.status ?? "—")}
              </p>
            </li>
          ))}
        </ul>
      )}
      <h3 className="mt-4 font-semibold">Historial / timeline</h3>
      <LotTimeline lotId={String(row.id)} />
      <div className="mt-4">
        <Link href={`/audit/cases/${String(row.id)}`}>
          <Button variant="secondary">Abrir expediente de trazabilidad</Button>
        </Link>
      </div>
    </div>
  );
}

function AssignTransportAction({
  row,
  helpers,
}: Readonly<{
  row: Record<string, unknown>;
  helpers: ActionHelpers;
}>) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const carriers = useQuery({
    queryKey: ["transport-carriers"],
    queryFn: () => platform.list<CarrierOption>("/api/v1/transport/carriers", { page_size: 100 }),
    enabled: open,
  });
  const options = (carriers.data?.items ?? []).map((item) => ({
    value: String(item.id),
    label: `${String(item.full_name ?? "Transportista")}${item.email ? ` · ${item.email}` : ""}`,
  }));

  return (
    <>
      <Button variant="secondary" onClick={() => setOpen(true)}>
        Asignar transportista
      </Button>
      {open ? (
        <div className="fixed inset-0 z-[55] grid place-items-center p-4">
          <button className="absolute inset-0 bg-[var(--overlay)]" onClick={() => setOpen(false)} />
          <div className="relative w-full max-w-md space-y-4 rounded-2xl bg-white p-6">
            <h3 className="text-lg font-semibold">Asignar transportista al lote</h3>
            <p className="text-sm text-muted">
              Lote <span className="font-medium text-text">{String(row.code ?? row.id)}</span>. Selecciona el
              transportista responsable del traslado.
            </p>
            {carriers.isLoading ? <Skeleton className="h-24 w-full" /> : null}
            {carriers.isError ? (
              <ErrorState message="No se pudieron cargar transportistas." onRetry={() => carriers.refetch()} />
            ) : null}
            {!carriers.isLoading && !carriers.isError && options.length === 0 ? (
              <p className="rounded-xl bg-amber-50 px-3 py-2 text-sm text-amber-800">
                No hay usuarios con rol transportista en la organización. Invita uno desde Usuarios o ejecuta el
                seed <code>assign_transports_to_carrier.sql</code>.
              </p>
            ) : null}
            {options.length > 0 ? (
              <SimpleForm
                loading={loading}
                submitLabel="Asignar y registrar transporte"
                validate={(body) => {
                  if (!String(body.assigned_to ?? "").trim()) {
                    return {
                      ok: false,
                      errors: { assigned_to: "Debes seleccionar un transportista." },
                      message: "Debes seleccionar un transportista.",
                    };
                  }
                  const selected = options.find((item) => item.value === String(body.assigned_to ?? ""));
                  const parsed = parseForm(transportSchema, {
                    ...body,
                    lot_id: String(row.id),
                    driver: selected?.label.split(" · ")[0] ?? "Transportista",
                  });
                  if (!parsed.ok) return parsed;
                  return { ok: true, data: parsed.data as Record<string, unknown> };
                }}
                onSubmit={async (body) => {
                  setLoading(true);
                  try {
                    await platform.post("/api/v1/transport", body);
                    helpers.push("Transportista asignado correctamente.");
                    helpers.refresh();
                    setOpen(false);
                  } catch (error) {
                    helpers.push(error instanceof Error ? error.message : "No se pudo asignar.", "error");
                  } finally {
                    setLoading(false);
                  }
                }}
                fields={[
                  { name: "assigned_to", label: "Transportista", options },
                  { name: "vehicle", label: "Vehículo" },
                  { name: "plate", label: "Placa" },
                  { name: "origin", label: "Origen", required: false },
                  { name: "destination", label: "Destino", required: false },
                ]}
              />
            ) : null}
            <div className="flex justify-end">
              <Button type="button" variant="secondary" onClick={() => setOpen(false)}>
                Cerrar
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}

function renderLotDetail(row: Record<string, unknown>) {
  return <LotDetail row={row} />;
}

function lotExtraActions(row: Record<string, unknown>, helpers: ActionHelpers) {
  const user = useSessionStore.getState().user;
  const canAssignTransport = Boolean(user?.permissions.includes("register_transport"));
  const canViewAudit = Boolean(user?.permissions.includes("view_audit"));
  return (
    <div className="flex flex-wrap gap-2">
      {canViewAudit ? (
        <Link href={`/audit/cases/${String(row.id)}`}>
          <Button variant="secondary">Expediente</Button>
        </Link>
      ) : null}
      {canAssignTransport ? <AssignTransportAction row={row} helpers={helpers} /> : null}
    </div>
  );
}

export default function LotsPage() {
  const user = useSessionStore((state) => state.user);
  const canAssignTransport = Boolean(user?.permissions.includes("register_transport"));
  const canViewAudit = Boolean(user?.permissions.includes("view_audit"));
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
        createForm={LotsCreateForm}
        renderDetail={renderLotDetail}
        extraActions={canAssignTransport || canViewAudit ? lotExtraActions : undefined}
      />
    </PermissionGate>
  );
}

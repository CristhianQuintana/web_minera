"use client";

import { parseForm, transportEventSchema, transportSchema } from "@/application/dto/resource-schemas";
import { platform } from "@/composition/container";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { useAction, useDetail } from "@/shared/hooks/use-platform";
import { Button, ErrorState, Skeleton } from "@/shared/components/ui";
import { formatDateTime } from "@/shared/utils/format";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

type TransportEvent = {
  id?: string;
  description?: string;
  event_type?: string;
  occurred_at?: string;
  is_incident?: boolean;
};

type CreateFormArgs = {
  onSubmit: (body: Record<string, unknown>) => void;
  loading: boolean;
};

type CarrierOption = { id: string; full_name?: string; email?: string; role?: string };

function TransportEventsPanel({ transportId, canRegister }: Readonly<{ transportId: string; canRegister: boolean }>) {
  const [open, setOpen] = useState(false);
  const events = useDetail<{ items: TransportEvent[] }>(
    "transport-events",
    `/api/v1/transport/${transportId}/events`,
  );
  const action = useAction(["transport-events", "transport"]);

  if (events.isLoading) return <Skeleton className="mt-3 h-20 w-full" />;
  if (events.isError) {
    return <ErrorState message="No se pudieron cargar los eventos." onRetry={() => events.refetch()} />;
  }
  const items = events.data?.items ?? [];

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-semibold">Eventos de transporte</h3>
        {canRegister ? (
          <Button type="button" variant="secondary" onClick={() => setOpen((value) => !value)}>
            {open ? "Cerrar" : "Registrar evento"}
          </Button>
        ) : null}
      </div>
      {open ? (
        <div className="mt-3 rounded-xl border border-border p-3">
          <SimpleForm
            loading={action.isPending}
            submitLabel="Guardar evento"
            validate={(body) => {
              const parsed = parseForm(transportEventSchema, body);
              if (!parsed.ok) return parsed;
              return { ok: true, data: parsed.data as Record<string, unknown> };
            }}
            onSubmit={(body) => {
              action.mutate(
                { path: `/api/v1/transport/${transportId}/events`, body },
                {
                  onSuccess: () => {
                    setOpen(false);
                    events.refetch();
                  },
                },
              );
            }}
            fields={[
              { name: "event_type", label: "Tipo", options: [
                { value: "departure", label: "Salida" },
                { value: "checkpoint", label: "Punto de control" },
                { value: "arrival", label: "Llegada" },
                { value: "incident", label: "Incidente" },
              ] },
              { name: "description", label: "Descripción" },
            ]}
          />
        </div>
      ) : null}
      {!items.length ? (
        <p className="mt-2 text-sm text-muted">Sin eventos registrados.</p>
      ) : (
        <ol className="mt-3 space-y-2">
          {items.map((event, index) => (
            <li key={String(event.id ?? index)} className="rounded-xl border border-border px-3 py-2 text-sm">
              <p className="font-medium">
                {event.event_type ?? "evento"}
                {event.is_incident ? " · incidente" : ""}
              </p>
              <p className="text-muted">{event.description}</p>
              <p className="text-xs text-muted">{formatDateTime(String(event.occurred_at ?? ""))}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function TransportCreateForm({ onSubmit, loading }: Readonly<CreateFormArgs>) {
  const user = useSessionStore((state) => state.user);
  const isCarrier = user?.role === "carrier";
  const carriers = useQuery({
    queryKey: ["transport-carriers"],
    queryFn: () => platform.list<CarrierOption>("/api/v1/transport/carriers", { page_size: 100 }),
    enabled: !isCarrier,
  });
  const options = (carriers.data?.items ?? []).map((item) => ({
    value: String(item.id),
    label: `${String(item.full_name ?? "Transportista")}${item.email ? ` · ${item.email}` : ""}`,
  }));

  return (
    <SimpleForm
      loading={loading || (!isCarrier && carriers.isLoading)}
      validate={(body) => {
        const selected = options.find((item) => item.value === String(body.assigned_to ?? ""));
        const parsed = parseForm(transportSchema, {
          ...body,
          driver: isCarrier
            ? (user?.full_name ?? body.driver ?? "Transportista")
            : (selected?.label.split(" · ")[0] ?? body.driver ?? "Transportista"),
          assigned_to: isCarrier ? user?.id : body.assigned_to,
        });
        if (!parsed.ok) return parsed;
        if (!isCarrier && !String(body.assigned_to ?? "").trim()) {
          return {
            ok: false,
            errors: { assigned_to: "Debes seleccionar un transportista." },
            message: "Debes seleccionar un transportista.",
          };
        }
        return { ok: true, data: parsed.data as Record<string, unknown> };
      }}
      onSubmit={onSubmit}
      fields={[
        { name: "lot_id", label: "ID de lote" },
        ...(isCarrier
          ? []
          : [{ name: "assigned_to", label: "Transportista", options }]),
        { name: "vehicle", label: "Vehículo" },
        { name: "plate", label: "Placa" },
        { name: "origin", label: "Origen", required: false },
        { name: "destination", label: "Destino", required: false },
      ]}
    />
  );
}

function TransportDetail({ row }: Readonly<{ row: Record<string, unknown> }>) {
  const user = useSessionStore((state) => state.user);
  const canRegister = Boolean(user?.permissions.includes("register_transport"));
  return (
    <div>
      <Field label="Lote" value={String(row.lot_id)} />
      <Field label="Transportista" value={String(row.driver)} />
      <Field label="Vehículo" value={`${row.vehicle} · ${row.plate}`} />
      <Field label="Origen" value={String(row.origin ?? "—")} />
      <Field label="Destino" value={String(row.destination ?? "—")} />
      <Field label="Estado" value={String(row.status)} />
      <TransportEventsPanel transportId={String(row.id)} canRegister={canRegister} />
    </div>
  );
}

function renderTransportDetail(row: Record<string, unknown>) {
  return <TransportDetail row={row} />;
}

export default function TransportPage() {
  const user = useSessionStore((state) => state.user);
  const canRegister = Boolean(user?.permissions.includes("register_transport"));
  return (
    <PermissionGate permission="view_transport">
      <ResourcePage
        title="Transporte"
        description="Salidas, llegadas y estados de traslado."
        queryKey="transport"
        path="/api/v1/transport"
        canCreate={canRegister}
        createLabel="Registrar transporte"
        createPath="/api/v1/transport"
        emptyTitle="No hay transportes registrados."
        emptyDescription="Los transportes asignados aparecerán aquí."
        columns={[
          { key: "lot_id", label: "Lote" },
          { key: "driver", label: "Transportista" },
          { key: "vehicle", label: "Vehículo" },
          { key: "started_at", label: "Salida" },
          { key: "ended_at", label: "Llegada" },
          { key: "status", label: "Estado" },
        ]}
        detailTitle="Detalle de transporte"
        createForm={TransportCreateForm}
        renderDetail={renderTransportDetail}
      />
    </PermissionGate>
  );
}

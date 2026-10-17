"use client";

import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { useSessionStore } from "@/infrastructure/auth/session-store";

export default function TransportPage() {
  const user = useSessionStore((state) => state.user);
  return (
    <PermissionGate permission="view_transport">
      <ResourcePage
        title="Transporte"
        description="Salidas, llegadas y estados de traslado."
        queryKey="transport"
        path="/api/v1/transport"
        canCreate={Boolean(user?.permissions.includes("register_transport"))}
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
        createForm={({ onSubmit, loading }) => (
          <SimpleForm
            loading={loading}
            onSubmit={onSubmit}
            fields={[
              { name: "lot_id", label: "ID de lote" },
              { name: "vehicle", label: "Vehículo" },
              { name: "plate", label: "Placa" },
              { name: "driver", label: "Conductor" },
              { name: "origin", label: "Origen" },
              { name: "destination", label: "Destino" },
            ]}
          />
        )}
        renderDetail={(row) => (
          <div>
            <Field label="Lote" value={String(row.lot_id)} />
            <Field label="Conductor" value={String(row.driver)} />
            <Field label="Vehículo" value={`${row.vehicle} · ${row.plate}`} />
            <Field label="Origen" value={String(row.origin ?? "—")} />
            <Field label="Destino" value={String(row.destination ?? "—")} />
            <Field label="Estado" value={String(row.status)} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

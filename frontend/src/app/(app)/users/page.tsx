"use client";

import { platform } from "@/composition/container";
import { PermissionGate } from "@/presentation/layouts/app-shell";
import { Field, ResourcePage, SimpleForm } from "@/presentation/modules/resource-page";
import { Button, Modal } from "@/shared/components/ui";
import { useState } from "react";

export default function UsersPage() {
  return (
    <PermissionGate permission="manage_users">
      <ResourcePage
        title="Usuarios"
        description="Invitación, activación y control de acceso. No existe registro público."
        queryKey="users"
        path="/api/v1/users"
        canCreate
        createLabel="Invitar usuario"
        createPath="/api/v1/users/invite"
        emptyTitle="No hay usuarios."
        emptyDescription="Invita a una persona para que active su cuenta."
        columns={[
          { key: "full_name", label: "Nombre" },
          { key: "email", label: "Correo" },
          { key: "role", label: "Rol" },
          { key: "invitation_status", label: "Estado" },
          { key: "last_activity_at", label: "Última actividad" },
        ]}
        detailTitle="Detalle de usuario"
        createForm={({ onSubmit, loading }) => (
          <SimpleForm
            loading={loading}
            submitLabel="Enviar invitación"
            onSubmit={onSubmit}
            fields={[
              { name: "full_name", label: "Nombre" },
              { name: "email", label: "Correo", type: "email" },
              {
                name: "role",
                label: "Rol",
                options: [
                  { value: "admin", label: "Administrador" },
                  { value: "auditor", label: "Auditor" },
                  { value: "producer", label: "Productor" },
                  { value: "carrier", label: "Transportista" },
                  { value: "receiver", label: "Receptor" },
                  { value: "supervisor", label: "Supervisor" },
                ],
              },
            ]}
          />
        )}
        extraActions={(row, helpers) => <UserActions row={row} helpers={helpers} />}
        renderDetail={(row) => (
          <div>
            <Field label="Nombre" value={String(row.full_name)} />
            <Field label="Correo" value={String(row.email ?? "—")} />
            <Field label="Rol" value={String(row.role)} />
            <Field label="Estado" value={String(row.invitation_status ?? row.status)} />
          </div>
        )}
      />
    </PermissionGate>
  );
}

function UserActions({
  row,
  helpers,
}: {
  row: Record<string, unknown>;
  helpers: { refresh: () => void; push: (text: string, tone?: "success" | "error") => void };
}) {
  const [confirm, setConfirm] = useState<"activate" | "deactivate" | null>(null);
  const [loading, setLoading] = useState(false);
  const active = row.status === "active" && row.invitation_status !== "inactive";
  async function run(path: string, success: string) {
    setLoading(true);
    try {
      await platform.post(path);
      helpers.push(success);
      helpers.refresh();
    } catch (error) {
      helpers.push(error instanceof Error ? error.message : "No se pudo completar.", "error");
    } finally {
      setLoading(false);
      setConfirm(null);
    }
  }
  return (
    <>
      {row.invitation_status === "pending" ? (
        <Button variant="secondary" onClick={() => run(`/api/v1/users/${row.id}/resend-invite`, "Invitación reenviada correctamente.")}>
          Reenviar invitación
        </Button>
      ) : null}
      <Button variant={active ? "danger" : "secondary"} onClick={() => setConfirm(active ? "deactivate" : "activate")}>
        {active ? "Desactivar" : "Activar"}
      </Button>
      <Modal
        open={confirm !== null}
        title={confirm === "deactivate" ? "¿Desactivar usuario?" : "¿Activar usuario?"}
        onClose={() => setConfirm(null)}
      >
        <p className="mb-4 text-sm text-muted">
          {confirm === "deactivate" ? "El usuario ya no podrá ingresar al sistema." : "El usuario podrá volver a ingresar."}
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirm(null)}>
            Cancelar
          </Button>
          <Button
            variant={confirm === "deactivate" ? "danger" : "primary"}
            loading={loading}
            onClick={() =>
              run(
                `/api/v1/users/${row.id}/${confirm}`,
                confirm === "deactivate" ? "Usuario desactivado correctamente." : "Usuario activado correctamente.",
              )
            }
          >
            {loading ? (confirm === "deactivate" ? "Desactivando..." : "Activando...") : confirm === "deactivate" ? "Desactivar" : "Activar"}
          </Button>
        </div>
      </Modal>
    </>
  );
}

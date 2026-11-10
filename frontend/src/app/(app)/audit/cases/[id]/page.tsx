"use client";

import { platform } from "@/composition/container";
import { PageHeader, PermissionGate, StatusBadge } from "@/presentation/layouts/app-shell";
import { Button, Card, ErrorState, Skeleton } from "@/shared/components/ui";
import { formatDateTime, formatQuantity } from "@/shared/utils/format";
import { env } from "@/config/env";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { useState } from "react";

function SectionList({
  title,
  rows,
  empty,
  render,
}: Readonly<{
  title: string;
  rows: Array<Record<string, unknown>>;
  empty: string;
  render: (row: Record<string, unknown>, index: number) => React.ReactNode;
}>) {
  return (
    <Card>
      <h2 className="font-semibold">{title}</h2>
      {!rows.length ? (
        <p className="mt-2 text-sm text-muted">{empty}</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {rows.map((row, index) => (
            <li key={String(row.id ?? index)} className="rounded-xl border border-border px-3 py-2 text-sm">
              {render(row, index)}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

export default function AuditCasePage() {
  const params = useParams<{ id: string }>();
  const user = useSessionStore((state) => state.user);
  const canExport = Boolean(user?.permissions.includes("export"));
  const [exporting, setExporting] = useState(false);
  const query = useQuery({
    queryKey: ["audit-case", params.id],
    queryFn: () => platform.get<Record<string, unknown>>(`/api/v1/audits/cases/${params.id}`),
  });

  async function downloadExpediente() {
    setExporting(true);
    try {
      const token = typeof window !== "undefined" ? sessionStorage.getItem("wm_access_token") : null;
      const response = await fetch(`${env.apiUrl}/api/v1/audits/cases/${params.id}/export`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) throw new Error("No se pudo exportar el expediente.");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `expediente-${params.id}.csv`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo exportar el expediente.");
    } finally {
      setExporting(false);
    }
  }

  const custody = (query.data?.custody as Array<Record<string, unknown>> | undefined) ?? [];
  const transports = (query.data?.transports as Array<Record<string, unknown>> | undefined) ?? [];
  const receptions = (query.data?.receptions as Array<Record<string, unknown>> | undefined) ?? [];
  const weighings = (query.data?.weighings as Array<Record<string, unknown>> | undefined) ?? [];
  const evidences = (query.data?.evidences as Array<Record<string, unknown>> | undefined) ?? [];
  const audit = (query.data?.audit as Array<Record<string, unknown>> | undefined) ?? [];
  const alerts = (query.data?.alerts as Array<Record<string, unknown>> | undefined) ?? [];
  const inferences = (query.data?.ml_inferences as Array<Record<string, unknown>> | undefined) ?? [];
  const balance = (query.data?.balance as Record<string, unknown> | null | undefined) ?? null;

  return (
    <PermissionGate permission="view_audit">
      <PageHeader
        title={`Expediente ${String(query.data?.code ?? params.id)}`}
        description="Trazabilidad consolidada del lote: operaciones, evidencias, alertas y auditoría."
        actions={
          canExport ? (
            <Button variant="secondary" loading={exporting} onClick={() => void downloadExpediente()}>
              Exportar expediente (CSV)
            </Button>
          ) : null
        }
      />
      {query.isLoading ? <Skeleton className="h-80" /> : null}
      {query.isError ? <ErrorState message="No pudimos cargar el expediente." onRetry={() => query.refetch()} /> : null}
      {query.data ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <h2 className="font-semibold">Datos del lote</h2>
            <p className="mt-2 text-sm">
              {String(query.data.code)} · {String(query.data.mineral)}
            </p>
            <p className="text-sm text-muted">
              {formatQuantity(Number(query.data.quantity), String(query.data.unit))} ·{" "}
              <StatusBadge value={String(query.data.status)} />
            </p>
            <p className="mt-2 text-xs text-muted">Registrado: {formatDateTime(String(query.data.created_at))}</p>
          </Card>
          <Card>
            <h2 className="font-semibold">Esperado vs observado (balance)</h2>
            {!balance ? (
              <p className="mt-2 text-sm text-muted">Sin balance calculado.</p>
            ) : (
              <div className="mt-2 space-y-1 text-sm">
                <p>Origen: {formatQuantity(Number(balance.origin_quantity), "kg")}</p>
                <p>
                  Observado/recibido:{" "}
                  {balance.received_quantity == null
                    ? "—"
                    : formatQuantity(Number(balance.received_quantity), "kg")}
                </p>
                <p>
                  Desviación:{" "}
                  {balance.difference == null
                    ? "—"
                    : `${String(balance.difference)} (${String(balance.difference_percent ?? "—")}%)`}
                </p>
                <p>
                  Estado: <StatusBadge value={String(balance.status)} />
                </p>
              </div>
            )}
          </Card>
          <SectionList
            title="Cadena de custodia"
            rows={custody}
            empty="Sin transferencias."
            render={(row) => (
              <>
                <p className="font-medium">
                  {String(row.origin)} → {String(row.destination)}
                </p>
                <p className="text-muted">
                  {formatQuantity(Number(row.quantity), "kg")} · {formatDateTime(String(row.occurred_at))}
                </p>
              </>
            )}
          />
          <SectionList
            title="Transportes"
            rows={transports}
            empty="Sin transportes."
            render={(row) => (
              <>
                <p className="font-medium">
                  {String(row.code ?? row.id)} · {String(row.driver ?? "—")}
                </p>
                <p className="text-muted">
                  {String(row.vehicle)} · {String(row.plate)} · <StatusBadge value={String(row.status)} />
                </p>
              </>
            )}
          />
          <SectionList
            title="Recepciones"
            rows={receptions}
            empty="Sin recepciones."
            render={(row) => (
              <>
                <p className="font-medium">{String(row.responsible ?? "Receptor")}</p>
                <p className="text-muted">
                  Declarada {formatQuantity(Number(row.declared_quantity), String(row.unit))} · Recibida{" "}
                  {formatQuantity(Number(row.received_quantity), String(row.unit))}
                </p>
              </>
            )}
          />
          <SectionList
            title="Pesajes"
            rows={weighings}
            empty="Sin pesajes."
            render={(row) => (
              <>
                <p className="font-medium">{formatQuantity(Number(row.weight), String(row.unit))}</p>
                <p className="text-muted">
                  {String(row.instrument)} · {formatDateTime(String(row.occurred_at ?? row.created_at))}
                </p>
              </>
            )}
          />
          <SectionList
            title="Evidencias"
            rows={evidences}
            empty="Sin evidencias asociadas."
            render={(row) => (
              <>
                <p className="font-medium">{String(row.file_name ?? row.id)}</p>
                <p className="text-muted">{String(row.content_type ?? row.kind ?? "archivo")}</p>
              </>
            )}
          />
          <SectionList
            title="Alertas del lote"
            rows={alerts}
            empty="Sin alertas."
            render={(row) => (
              <>
                <p className="font-medium">{String(row.title)}</p>
                <p className="text-muted">
                  {String(row.alert_type)} · <StatusBadge value={String(row.status)} /> ·{" "}
                  {formatDateTime(String(row.created_at))}
                </p>
              </>
            )}
          />
          <SectionList
            title="Inferencias ML"
            rows={inferences}
            empty="Sin inferencias."
            render={(row) => (
              <>
                <p className="font-medium">
                  Esperada {formatQuantity(Number(row.expected_quantity), "kg")} · Observada{" "}
                  {row.observed_quantity == null ? "—" : formatQuantity(Number(row.observed_quantity), "kg")}
                </p>
                <p className="text-muted">
                  Señal {String(row.signal)} · v{String(row.model_version)} ·{" "}
                  {row.deviation_percent != null ? `${Number(row.deviation_percent).toFixed(2)}%` : "sin %"}
                </p>
              </>
            )}
          />
          <SectionList
            title="Auditoría del expediente"
            rows={audit}
            empty="Sin eventos de auditoría vinculados al lote."
            render={(row) => (
              <>
                <p className="font-medium">
                  {String(row.action)} · {String(row.entity)}
                </p>
                <p className="text-muted">
                  Usuario {String(row.user_id)} · {formatDateTime(String(row.created_at))} · {String(row.result)}
                </p>
              </>
            )}
          />
        </div>
      ) : null}
    </PermissionGate>
  );
}

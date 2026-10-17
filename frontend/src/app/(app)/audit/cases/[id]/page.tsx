"use client";

import { platform } from "@/composition/container";
import { PageHeader, PermissionGate } from "@/presentation/layouts/app-shell";
import { Card, ErrorState, Skeleton } from "@/shared/components/ui";
import { formatDateTime, formatQuantity } from "@/shared/utils/format";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

export default function AuditCasePage() {
  const params = useParams<{ id: string }>();
  const query = useQuery({
    queryKey: ["audit-case", params.id],
    queryFn: () => platform.get<Record<string, unknown>>(`/api/v1/audits/cases/${params.id}`),
  });

  return (
    <PermissionGate permission="view_audit">
      <PageHeader title={`Expediente ${query.data?.code ?? params.id}`} description="Vista completa de trazabilidad." />
      {query.isLoading ? <Skeleton className="h-80" /> : null}
      {query.isError ? <ErrorState message="No pudimos cargar el expediente." onRetry={() => query.refetch()} /> : null}
      {query.data ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <h2 className="font-semibold">Datos del lote</h2>
            <p className="mt-2 text-sm">{String(query.data.code)} · {String(query.data.mineral)}</p>
            <p className="text-sm text-muted">{formatQuantity(Number(query.data.quantity), String(query.data.unit))}</p>
          </Card>
          <Card>
            <h2 className="font-semibold">Balance</h2>
            <pre className="mt-2 overflow-auto text-xs">{JSON.stringify(query.data.balance, null, 2)}</pre>
          </Card>
          <Card>
            <h2 className="font-semibold">Cadena de custodia</h2>
            <p className="mt-2 text-sm">{Array.isArray(query.data.custody) ? `${query.data.custody.length} eventos` : "—"}</p>
          </Card>
          <Card>
            <h2 className="font-semibold">Auditoría</h2>
            <p className="mt-2 text-sm">{Array.isArray(query.data.audit) ? `${query.data.audit.length} registros` : "—"}</p>
            <p className="text-xs text-muted">{formatDateTime(String(query.data.created_at))}</p>
          </Card>
        </div>
      ) : null}
    </PermissionGate>
  );
}

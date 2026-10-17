"use client";

import { platform } from "@/composition/container";
import { PageHeader } from "@/presentation/layouts/app-shell";
import { Card, ErrorState, Skeleton } from "@/shared/components/ui";
import { formatDateTime } from "@/shared/utils/format";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

export default function DashboardPage() {
  const query = useQuery({ queryKey: ["dashboard"], queryFn: () => platform.dashboard() });

  if (query.isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-4">
        <Skeleton className="h-28" />
        <Skeleton className="h-28" />
        <Skeleton className="h-28" />
        <Skeleton className="h-28" />
        <Skeleton className="col-span-full h-64" />
      </div>
    );
  }
  if (query.isError) {
    return <ErrorState message="No pudimos cargar el dashboard." onRetry={() => query.refetch()} />;
  }

  const data = query.data as {
    cards: Array<{ key: string; label: string; value: number; href: string }>;
    recent_lots: Array<Record<string, string>>;
    recent_alerts: Array<Record<string, string>>;
  };

  return (
    <div>
      <PageHeader title="Dashboard" description="Resumen operativo según tu rol." />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {data.cards.map((card) => (
          <Link key={card.key} href={card.href}>
            <Card className="hover:-translate-y-0.5">
              <p className="text-sm text-muted">{card.label}</p>
              <p className="mt-2 text-3xl font-semibold">{card.value}</p>
            </Card>
          </Link>
        ))}
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="mb-3 font-semibold">Operaciones recientes</h2>
          {(data.recent_lots ?? []).length === 0 ? (
            <p className="text-sm text-muted">No hay información disponible para este periodo.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {data.recent_lots.map((lot) => (
                <li key={lot.id} className="flex justify-between border-b border-border py-2">
                  <span>{lot.code}</span>
                  <span className="text-muted">{formatDateTime(lot.created_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card>
          <h2 className="mb-3 font-semibold">Alertas</h2>
          {(data.recent_alerts ?? []).length === 0 ? (
            <p className="text-sm text-muted">No hay alertas abiertas.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {data.recent_alerts.map((alert) => (
                <li key={alert.id} className="border-b border-border py-2">
                  <p className="font-medium">{alert.title}</p>
                  <p className="text-muted">{alert.summary}</p>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}

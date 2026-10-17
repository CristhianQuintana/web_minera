"use client";

import { getCurrentUserUseCase, logoutUseCase } from "@/composition/container";
import { platform } from "@/composition/container";
import { useSessionStore } from "@/infrastructure/auth/session-store";
import { Badge, Button, Skeleton } from "@/shared/components/ui";
import { cn } from "@/shared/utils/format";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  AlertTriangle,
  Bell,
  Boxes,
  Brain,
  ChevronLeft,
  FileSearch,
  LayoutDashboard,
  LogOut,
  Menu,
  Scale,
  Search,
  Settings,
  Shield,
  Truck,
  UserRound,
  Users,
  Warehouse,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, permission: "view_lots" },
  { href: "/lots", label: "Lotes", icon: Boxes, permission: "view_lots" },
  { href: "/custody", label: "Custodia", icon: Shield, permission: "view_custody" },
  { href: "/transport", label: "Transporte", icon: Truck, permission: "view_transport" },
  { href: "/receptions", label: "Recepción", icon: Warehouse, permission: "view_receptions" },
  { href: "/weighings", label: "Pesajes", icon: Scale, permission: "view_receptions" },
  { href: "/mass-balance", label: "Balance", icon: Activity, permission: "view_balance" },
  { href: "/alerts", label: "Alertas", icon: AlertTriangle, permission: "view_alerts" },
  { href: "/audit", label: "Auditoría", icon: FileSearch, permission: "view_audit" },
  { href: "/ml", label: "ML", icon: Brain, permission: "view_ml" },
  { href: "/users", label: "Usuarios", icon: Users, permission: "manage_users" },
  { href: "/settings", label: "Configuración", icon: Settings, permission: "manage_settings" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, setUser, sidebarCollapsed, toggleSidebar } = useSessionStore();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [notifyOpen, setNotifyOpen] = useState(false);
  const [search, setSearch] = useState("");

  const me = useQuery({ queryKey: ["me"], queryFn: getCurrentUserUseCase, retry: false });
  const notifications = useQuery({
    queryKey: ["notifications"],
    queryFn: () => platform.list("/api/v1/notifications", { page_size: 8 }),
    enabled: Boolean(user),
  });
  const results = useQuery({
    queryKey: ["search", search],
    queryFn: () => platform.search(search),
    enabled: search.length > 1,
  });

  useEffect(() => {
    if (me.data) setUser(me.data);
    if (me.isError) router.replace("/login");
  }, [me.data, me.isError, router, setUser]);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const crumbs = useMemo(() => pathname.split("/").filter(Boolean), [pathname]);
  const items = nav.filter((item) => !user || user.permissions.includes(item.permission) || user.role === "admin");

  if (!user && me.isLoading) {
    return (
      <div className="grid min-h-screen grid-cols-[240px_1fr] gap-4 p-4">
        <Skeleton className="h-full" />
        <div className="space-y-4">
          <Skeleton className="h-16" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  async function logout() {
    await logoutUseCase();
    setUser(null);
    router.replace("/login");
  }

  return (
    <div className="min-h-screen bg-background">
      {mobileOpen ? (
        <button className="fixed inset-0 z-[40] bg-[var(--overlay)] lg:hidden" onClick={() => setMobileOpen(false)} />
      ) : null}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-[41] flex flex-col border-r border-border bg-white transition-all duration-300",
          sidebarCollapsed ? "w-[76px]" : "w-[260px]",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex h-16 items-center justify-between px-4">
          <span className="font-semibold text-primary">{sidebarCollapsed ? "WM" : "WEB_MINERA"}</span>
          <button className="hidden rounded-lg p-1 hover:bg-slate-100 lg:block" onClick={toggleSidebar} aria-label="Colapsar menú">
            <ChevronLeft className={cn("h-4 w-4 transition", sidebarCollapsed && "rotate-180")} />
          </button>
        </div>
        <nav className="flex-1 space-y-1 overflow-auto px-3 pb-4">
          {items.map((item) => {
            const Icon = item.icon;
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                title={sidebarCollapsed ? item.label : undefined}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm",
                  active ? "bg-primary/10 font-medium text-primary" : "text-slate-600 hover:bg-slate-50",
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {!sidebarCollapsed ? item.label : null}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-border p-3">
          <Link href="/profile" className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm hover:bg-slate-50">
            <UserRound className="h-4 w-4" />
            {!sidebarCollapsed ? "Perfil" : null}
          </Link>
          <button onClick={logout} className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-error hover:bg-red-50">
            <LogOut className="h-4 w-4" />
            {!sidebarCollapsed ? "Cerrar sesión" : null}
          </button>
        </div>
      </aside>

      <div className={cn("min-h-screen transition-all duration-300", sidebarCollapsed ? "lg:pl-[76px]" : "lg:pl-[260px]")}>
        <header className="sticky top-0 z-[30] flex h-16 items-center justify-between gap-3 border-b border-border bg-white/90 px-4 backdrop-blur">
          <div className="flex items-center gap-3">
            <button className="rounded-lg p-2 hover:bg-slate-100 lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Abrir menú">
              <Menu className="h-5 w-5" />
            </button>
            <nav aria-label="breadcrumb" className="text-sm text-muted">
              {crumbs.map((crumb, index) => (
                <span key={crumb}>
                  {index > 0 ? " / " : ""}
                  <span className={index === crumbs.length - 1 ? "font-medium text-text" : ""}>{crumb}</span>
                </span>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Buscar lotes, QR..."
                className="w-64 rounded-xl border border-border bg-slate-50 py-2 pl-9 pr-3 text-sm"
              />
              {results.data?.lots?.length ? (
                <div className="absolute mt-1 w-full rounded-xl border border-border bg-white p-2 shadow-lg">
                  {results.data.lots.map((lot) => (
                    <Link key={String(lot.id)} href="/lots" className="block rounded-lg px-2 py-1.5 text-sm hover:bg-slate-50">
                      {String(lot.code)} · {String(lot.mineral)}
                    </Link>
                  ))}
                </div>
              ) : null}
            </div>
            <button className="relative rounded-xl p-2 hover:bg-slate-100" onClick={() => setNotifyOpen((value) => !value)} aria-label="Notificaciones">
              <Bell className="h-5 w-5" />
            </button>
            <button className="flex items-center gap-2 rounded-xl px-2 py-1 hover:bg-slate-100" onClick={() => setMenuOpen((value) => !value)}>
              <span className="grid h-8 w-8 place-items-center rounded-full bg-primary text-xs text-white">
                {user?.full_name?.slice(0, 1) ?? "U"}
              </span>
              <span className="hidden text-left text-sm md:block">
                <span className="block font-medium">{user?.full_name}</span>
                <span className="block text-xs text-muted">{user?.role_label}</span>
              </span>
            </button>
          </div>
        </header>
        {notifyOpen ? (
          <div className="absolute right-4 top-16 z-[20] w-80 rounded-2xl border border-border bg-white p-3 shadow-xl">
            <p className="mb-2 text-sm font-semibold">Notificaciones</p>
            {(notifications.data?.items ?? []).length === 0 ? (
              <p className="p-3 text-sm text-muted">No hay notificaciones recientes.</p>
            ) : (
              (notifications.data?.items as Array<Record<string, string>> | undefined)?.map((item) => (
                <div key={item.id} className="rounded-xl px-3 py-2 hover:bg-slate-50">
                  <p className="text-sm font-medium">{item.title}</p>
                  <p className="text-xs text-muted">{item.body}</p>
                </div>
              ))
            )}
          </div>
        ) : null}
        {menuOpen ? (
          <div className="absolute right-4 top-16 z-[20] w-52 rounded-2xl border border-border bg-white p-2 shadow-xl">
            <Link href="/profile" className="block rounded-xl px-3 py-2 text-sm hover:bg-slate-50">Perfil</Link>
            <Link href="/settings" className="block rounded-xl px-3 py-2 text-sm hover:bg-slate-50">Preferencias</Link>
            <button onClick={logout} className="block w-full rounded-xl px-3 py-2 text-left text-sm text-error hover:bg-red-50">
              Cerrar sesión
            </button>
          </div>
        ) : null}
        <main className="p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {description ? <p className="mt-1 text-sm text-muted">{description}</p> : null}
      </div>
      <div className="flex gap-2">{actions}</div>
    </div>
  );
}

export function PermissionGate({ permission, children }: { permission: string; children: React.ReactNode }) {
  const user = useSessionStore((state) => state.user);
  if (user && !user.permissions.includes(permission) && user.role !== "admin") {
    return (
      <div className="mx-auto max-w-lg py-20 text-center">
        <h1 className="text-2xl font-semibold">Acceso no autorizado</h1>
        <p className="mt-2 text-muted">No tienes permisos para consultar este recurso.</p>
        <Link href="/dashboard" className="mt-4 inline-block">
          <Button>Volver al inicio</Button>
        </Link>
      </div>
    );
  }
  return <>{children}</>;
}

export function StatusBadge({ value }: { value?: string }) {
  return <Badge value={labelOfStatus(value)} tone={toneForStatus(value)} />;
}

function labelOfStatus(value?: string) {
  return value ? (statusMap[value] ?? value) : "—";
}

const statusMap: Record<string, string> = {
  registered: "Registrado",
  inTransit: "En custodia",
  transferred: "Transferido",
  received: "Recibido",
  closed: "Cerrado",
  new: "Nueva",
  in_review: "En revisión",
  attended: "Atendida",
  pending: "Pendiente",
  active: "Activo",
  inactive: "Inactivo",
  expired: "Invitación expirada",
  assigned: "Asignado",
  in_progress: "En curso",
  arrived: "En destino",
  delivered: "Entregado",
  cancelled: "Cancelado",
  confirmed: "Confirmada",
  completed: "Completada",
  within_tolerance: "Dentro de tolerancia",
  review_required: "Revisión requerida",
  insufficient_data: "Sin información suficiente",
};

function toneForStatus(status?: string): "neutral" | "success" | "warning" | "error" | "info" {
  if (!status) return "neutral";
  if (["active", "confirmed", "within_tolerance", "attended", "delivered"].includes(status)) return "success";
  if (["new", "pending", "in_review", "review_required"].includes(status)) return "warning";
  if (["inactive", "expired", "cancelled", "critical", "high"].includes(status)) return "error";
  if (["inTransit", "in_progress", "assigned"].includes(status)) return "info";
  return "neutral";
}

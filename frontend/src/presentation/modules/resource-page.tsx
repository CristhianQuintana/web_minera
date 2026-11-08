"use client";

import { useAction, useDetail, useResource } from "@/shared/hooks/use-platform";
import { Button, EmptyState, ErrorState, Input, Modal, Select, Skeleton, ToastHost, useToasts } from "@/shared/components/ui";
import { StatusBadge } from "@/presentation/layouts/app-shell";
import { formatDateTime, formatQuantity, labelOf } from "@/shared/utils/format";
import { Download, RefreshCw, Search, X } from "lucide-react";
import { useEffect, useMemo, useState, type ReactNode } from "react";

export interface Column {
  key: string;
  label: string;
  render?: (row: Record<string, unknown>) => ReactNode;
}

interface ResourcePageProps {
  title: string;
  description: string;
  queryKey: string;
  path: string;
  columns: Column[];
  searchPlaceholder?: string;
  statuses?: Array<{ value: string; label: string }>;
  emptyTitle: string;
  emptyDescription: string;
  createLabel?: string;
  createForm?: (args: {
    onSubmit: (body: Record<string, unknown>) => void;
    loading: boolean;
  }) => ReactNode;
  createPath?: string;
  detailTitle: string;
  renderDetail?: (row: Record<string, unknown>) => ReactNode;
  canCreate?: boolean;
  canExport?: boolean;
  extraActions?: (row: Record<string, unknown>, helpers: { refresh: () => void; push: (text: string, tone?: "success" | "error") => void }) => ReactNode;
}

export function ResourcePage({
  title,
  description,
  queryKey,
  path,
  columns,
  searchPlaceholder = "Buscar",
  statuses,
  emptyTitle,
  emptyDescription,
  createLabel,
  createForm,
  createPath,
  detailTitle,
  renderDetail,
  canCreate,
  canExport,
  extraActions,
}: Readonly<ResourcePageProps>) {
  const [page, setPage] = useState(1);
  const [q, setQ] = useState("");
  const [debounced, setDebounced] = useState("");
  const [status, setStatus] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [confirmClose, setConfirmClose] = useState(false);
  const { toasts, push } = useToasts();

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(q), 350);
    return () => clearTimeout(timer);
  }, [q]);

  const list = useResource<Record<string, unknown>>(queryKey, path, {
    page,
    page_size: 20,
    q: debounced,
    status: status || undefined,
  });
  const detail = useDetail<Record<string, unknown>>(`${queryKey}-detail`, selectedId ? `${path}/${selectedId}` : null);
  const action = useAction([queryKey, `${queryKey}-detail`]);

  const items = list.data?.items ?? [];
  const total = list.data?.total ?? 0;
  const from = total === 0 ? 0 : (page - 1) * 20 + 1;
  const to = Math.min(page * 20, total);

  const selected = useMemo(
    () => items.find((item) => String(item.id) === selectedId) ?? detail.data,
    [items, selectedId, detail.data],
  );

  function closeDrawer() {
    if (dirty) {
      setConfirmClose(true);
      return;
    }
    setSelectedId(null);
    setCreateOpen(false);
  }

  function cell(row: Record<string, unknown>, column: Column) {
    if (column.render) return column.render(row);
    const value = row[column.key];
    if (column.key.includes("at") && typeof value === "string") return formatDateTime(value);
    if (column.key === "quantity" || column.key === "weight") return formatQuantity(Number(value), String(row.unit ?? ""));
    if (column.key === "status" || column.key === "severity") return <StatusBadge value={String(value ?? "")} />;
    return value === undefined || value === null || value === "" ? "—" : String(value);
  }

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-1 text-sm text-muted">{description}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={() => list.refetch()}>
            <RefreshCw className="h-4 w-4" /> Actualizar
          </Button>
          {canExport ? (
            <a href={`${typeof process.env.NEXT_PUBLIC_API_URL === "string" ? process.env.NEXT_PUBLIC_API_URL : "http://localhost:8000"}${path}/export`} target="_blank" rel="noreferrer">
              <Button variant="secondary">
                <Download className="h-4 w-4" /> Exportar
              </Button>
            </a>
          ) : null}
          {canCreate && createLabel ? (
            <Button onClick={() => setCreateOpen(true)}>{createLabel}</Button>
          ) : null}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="relative min-w-[240px] flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted" />
          <input
            value={q}
            onChange={(event) => {
              setQ(event.target.value);
              setPage(1);
            }}
            placeholder={searchPlaceholder}
            className="w-full rounded-xl border border-border bg-white py-2.5 pl-9 pr-3 text-sm"
          />
        </div>
        {statuses ? (
          <Select
            label="Estado"
            name="status-filter"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(1);
            }}
          >
            <option value="">Todos los estados</option>
            {statuses.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </Select>
        ) : null}
        <Button
          variant="ghost"
          onClick={() => {
            setQ("");
            setStatus("");
            setPage(1);
          }}
        >
          Limpiar
        </Button>
      </div>
      {(q || status) && (
        <div className="mb-3 flex gap-2">
          {q ? <span className="rounded-full bg-slate-100 px-3 py-1 text-xs">Búsqueda: {q}</span> : null}
          {status ? <span className="rounded-full bg-slate-100 px-3 py-1 text-xs">Estado: {labelOf(status)}</span> : null}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-border bg-white">
        <ResourceTableBody
          loading={list.isLoading}
          error={list.isError}
          empty={!items.length}
          emptyTitle={emptyTitle}
          emptyDescription={emptyDescription}
          onRetry={() => list.refetch()}
          columns={columns}
          items={items}
          cell={cell}
          onOpen={(id) => setSelectedId(id)}
          extraActions={extraActions}
          refresh={() => list.refetch()}
          push={push}
        />
        <div className="flex items-center justify-between border-t border-border px-4 py-3 text-sm text-muted">
          <span>
            {from}–{to} de {total}
          </span>
          <div className="flex gap-2">
            <Button variant="secondary" disabled={page === 1} onClick={() => setPage((value) => value - 1)}>
              Anterior
            </Button>
            <Button variant="secondary" disabled={to >= total} onClick={() => setPage((value) => value + 1)}>
              Siguiente
            </Button>
          </div>
        </div>
      </div>

      {selectedId ? (
        <div className="fixed inset-0 z-[40]">
          <button className="absolute inset-0 bg-[var(--overlay)]" onClick={closeDrawer} aria-label="Cerrar detalle" />
          <aside className="absolute inset-y-0 right-0 flex w-full max-w-[520px] flex-col bg-white shadow-2xl transition duration-300 md:w-[70vw] lg:w-[480px]">
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <h2 className="text-lg font-semibold">{detailTitle}</h2>
              <button onClick={closeDrawer} aria-label="Cerrar">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-5">
              <ResourceDetailBody
                loading={detail.isLoading}
                error={detail.isError}
                selected={selected}
                renderDetail={renderDetail}
                onRetry={() => detail.refetch()}
              />
            </div>
          </aside>
        </div>
      ) : null}

      {createOpen && createForm && createPath ? (
        <div className="fixed inset-0 z-[40]">
          <button className="absolute inset-0 bg-[var(--overlay)]" onClick={closeDrawer} aria-label="Cerrar" />
          <aside className="absolute inset-y-0 right-0 flex w-full max-w-[480px] flex-col bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <h2 className="text-lg font-semibold">{createLabel}</h2>
              <button onClick={closeDrawer} aria-label="Cerrar">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-5" onChange={() => setDirty(true)}>
              {createForm({
                loading: action.isPending,
                onSubmit: (body) => {
                  action.mutate(
                    { path: createPath, body },
                    {
                      onSuccess: () => {
                        push(`${title.slice(0, -1)} registrado correctamente.`);
                        setCreateOpen(false);
                        setDirty(false);
                        list.refetch();
                      },
                      onError: (error) => push(error.message, "error"),
                    },
                  );
                },
              })}
            </div>
          </aside>
        </div>
      ) : null}

      <Modal open={confirmClose} title="¿Descartar cambios?" onClose={() => setConfirmClose(false)}>
        <p className="mb-4 text-sm text-muted">Tienes cambios que aún no se han guardado.</p>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmClose(false)}>
            Seguir editando
          </Button>
          <Button
            variant="danger"
            onClick={() => {
              setDirty(false);
              setConfirmClose(false);
              setSelectedId(null);
              setCreateOpen(false);
            }}
          >
            Descartar
          </Button>
        </div>
      </Modal>
      <ToastHost toasts={toasts} />
    </div>
  );
}


function ResourceTableBody({
  loading,
  error,
  empty,
  emptyTitle,
  emptyDescription,
  onRetry,
  columns,
  items,
  cell,
  onOpen,
  extraActions,
  refresh,
  push,
}: Readonly<{
  loading: boolean;
  error: boolean;
  empty: boolean;
  emptyTitle: string;
  emptyDescription: string;
  onRetry: () => void;
  columns: Column[];
  items: Record<string, unknown>[];
  cell: (row: Record<string, unknown>, column: Column) => ReactNode;
  onOpen: (id: string) => void;
  extraActions?: ResourcePageProps["extraActions"];
  refresh: () => void;
  push: (text: string, tone?: "success" | "error") => void;
}>) {
  if (loading) {
    return (
      <div className="space-y-2 p-4">
        <Skeleton className="h-10" />
        <Skeleton className="h-10" />
        <Skeleton className="h-10" />
      </div>
    );
  }
  if (error) {
    return <ErrorState message="No pudimos cargar esta información." onRetry={onRetry} />;
  }
  if (empty) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-muted">
          <tr>
            {columns.map((column) => (
              <th key={column.key} className="px-4 py-3 font-medium">
                {column.label}
              </th>
            ))}
            <th className="px-4 py-3 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.map((row) => (
            <tr key={String(row.id)} className="border-t border-border hover:bg-slate-50">
              {columns.map((column) => (
                <td key={column.key} className="px-4 py-3">
                  {cell(row, column)}
                </td>
              ))}
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-2">
                  <Button variant="ghost" onClick={() => onOpen(String(row.id))}>
                    Detalle
                  </Button>
                  {extraActions?.(row, { refresh, push })}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ResourceDetailBody({
  loading,
  error,
  selected,
  renderDetail,
  onRetry,
}: Readonly<{
  loading: boolean;
  error: boolean;
  selected?: Record<string, unknown> | null;
  renderDetail?: (row: Record<string, unknown>) => ReactNode;
  onRetry: () => void;
}>) {
  if (loading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-8" />
        <Skeleton className="h-32" />
      </div>
    );
  }
  if (error) {
    return <ErrorState message="No pudimos cargar el detalle." onRetry={onRetry} />;
  }
  if (!selected) return null;
  if (renderDetail) return <>{renderDetail(selected)}</>;
  return <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(selected, null, 2)}</pre>;
}

export function Field({ label, value }: Readonly<{ label: string; value?: ReactNode }>) {
  return (
    <div className="border-b border-border py-3">
      <p className="text-xs uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-1 text-sm text-text">{value ?? "—"}</p>
    </div>
  );
}

export function SimpleForm({
  fields,
  onSubmit,
  loading,
  submitLabel = "Guardar",
  validate,
}: Readonly<{
  fields: Array<{
    name: string;
    label: string;
    type?: string;
    required?: boolean;
    options?: Array<{ value: string; label: string }>;
  }>;
  onSubmit: (body: Record<string, unknown>) => void;
  loading?: boolean;
  submitLabel?: string;
  validate?: (
    body: Record<string, unknown>,
  ) => { ok: true; data: Record<string, unknown> } | { ok: false; errors: Record<string, string>; message: string };
}>) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  return (
    <form
      className="space-y-4"
      noValidate={Boolean(validate)}
      onSubmit={(event) => {
        event.preventDefault();
        const body: Record<string, unknown> = { ...values };
        fields.forEach((field) => {
          if (field.type === "number" && values[field.name]) body[field.name] = Number(values[field.name]);
          if (field.type === "checkbox") body[field.name] = values[field.name] === "true";
        });
        if (validate) {
          const result = validate(body);
          if (!result.ok) {
            setErrors(result.errors);
            setFormError(result.message);
            return;
          }
          setErrors({});
          setFormError(null);
          onSubmit(result.data);
          return;
        }
        onSubmit(body);
      }}
    >
      {formError ? (
        <p className="rounded-xl bg-red-50 px-3 py-2 text-sm text-error" role="alert">
          {formError}
        </p>
      ) : null}
      {fields.map((field) =>
        field.options ? (
          <Select
            key={field.name}
            label={field.label}
            value={values[field.name] ?? ""}
            error={errors[field.name]}
            onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))}
            required={field.required !== false}
          >
            <option value="">Selecciona</option>
            {field.options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        ) : (
          <Input
            key={field.name}
            label={field.label}
            type={field.type ?? "text"}
            value={values[field.name] ?? ""}
            error={errors[field.name]}
            onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))}
            required={field.required !== false}
          />
        ),
      )}
      <div className="sticky bottom-0 flex justify-end gap-2 bg-white pt-4">
        <Button type="submit" loading={loading}>
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}

import { statusLabels } from "@/domain/entities";

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    timeZone: "America/Bogota",
  }).format(date);
}

export function formatDateTime(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "America/Bogota",
  }).format(date);
}

export function formatQuantity(value?: number | null, unit?: string | null): string {
  if (value === undefined || value === null) return "—";
  const amount = Number(value).toLocaleString("es-CO", { maximumFractionDigits: 2 });
  return unit ? `${amount} ${unit}` : amount;
}

export function labelOf(value?: string | null): string {
  if (!value) return "—";
  return statusLabels[value] ?? value;
}

export function cn(...values: Array<string | false | null | undefined>): string {
  return values.filter(Boolean).join(" ");
}

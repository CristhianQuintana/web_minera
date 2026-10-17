"use client";

import { cn } from "@/shared/utils/format";
import { AlertCircle, Loader2 } from "lucide-react";
import { type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode, useState } from "react";

export function Button({
  children,
  loading,
  variant = "primary",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
  variant?: "primary" | "secondary" | "ghost" | "danger";
}) {
  const styles = {
    primary: "bg-primary text-white hover:bg-primary-dark",
    secondary: "bg-white border border-border text-text hover:bg-slate-50",
    ghost: "bg-transparent text-text hover:bg-slate-100",
    danger: "bg-error text-white hover:bg-red-700",
  }[variant];
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium disabled:opacity-60",
        styles,
        className,
      )}
      disabled={props.disabled || loading}
      {...props}
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
      {children}
    </button>
  );
}

export function Input({
  label,
  error,
  hint,
  className,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label?: string; error?: string; hint?: string }) {
  return (
    <label className="block space-y-1.5">
      {label ? <span className="text-sm font-medium text-text">{label}</span> : null}
      <input
        className={cn(
          "w-full rounded-xl border border-border bg-white px-3 py-2.5 text-sm text-text placeholder:text-muted",
          error && "border-error",
          className,
        )}
        {...props}
      />
      {hint && !error ? <span className="text-xs text-muted">{hint}</span> : null}
      {error ? <span className="text-xs text-error">{error}</span> : null}
    </label>
  );
}

export function Select({
  label,
  error,
  children,
  className,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & { label?: string; error?: string }) {
  return (
    <label className="block space-y-1.5">
      {label ? <span className="text-sm font-medium text-text">{label}</span> : null}
      <select
        className={cn("w-full rounded-xl border border-border bg-white px-3 py-2.5 text-sm", className)}
        {...props}
      >
        {children}
      </select>
      {error ? <span className="text-xs text-error">{error}</span> : null}
    </label>
  );
}

export function Badge({ value, tone = "neutral" }: { value: string; tone?: "neutral" | "success" | "warning" | "error" | "info" }) {
  const colors = {
    neutral: "bg-slate-100 text-slate-700",
    success: "bg-emerald-50 text-success",
    warning: "bg-amber-50 text-warning",
    error: "bg-red-50 text-error",
    info: "bg-sky-50 text-info",
  }[tone];
  return <span className={cn("inline-flex rounded-full px-2.5 py-1 text-xs font-medium", colors)}>{value}</span>;
}

export function toneFor(status?: string): "neutral" | "success" | "warning" | "error" | "info" {
  if (!status) return "neutral";
  if (["active", "confirmed", "within_tolerance", "attended", "delivered"].includes(status)) return "success";
  if (["new", "pending", "in_review", "review_required", "review_signal"].includes(status)) return "warning";
  if (["inactive", "expired", "cancelled", "critical", "high"].includes(status)) return "error";
  if (["inTransit", "in_progress", "assigned"].includes(status)) return "info";
  return "neutral";
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("rounded-2xl border border-border bg-surface p-5 shadow-[var(--shadow)]", className)}>{children}</div>;
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <p className="text-base font-semibold text-text">{title}</p>
      {description ? <p className="max-w-md text-sm text-muted">{description}</p> : null}
      {action}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <AlertCircle className="h-8 w-8 text-error" />
      <p className="text-base font-semibold text-text">{message}</p>
      {onRetry ? <Button onClick={onRetry}>Reintentar</Button> : null}
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-xl bg-slate-200", className)} />;
}

export function ToastHost({ toasts }: { toasts: Array<{ id: string; text: string; tone: "success" | "error" }> }) {
  return (
    <div className="fixed right-4 top-4 z-[60] space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "rounded-xl px-4 py-3 text-sm text-white shadow-lg",
            toast.tone === "success" ? "bg-success" : "bg-error",
          )}
        >
          {toast.text}
        </div>
      ))}
    </div>
  );
}

export function useToasts() {
  const [toasts, setToasts] = useState<Array<{ id: string; text: string; tone: "success" | "error" }>>([]);
  const push = (text: string, tone: "success" | "error" = "success") => {
    const id = crypto.randomUUID();
    setToasts((current) => [...current, { id, text, tone }]);
    setTimeout(() => setToasts((current) => current.filter((item) => item.id !== id)), 3200);
  };
  return { toasts, push };
}

export function Modal({
  open,
  title,
  children,
  onClose,
}: {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[50] flex items-center justify-center p-4">
      <button className="absolute inset-0 bg-[var(--overlay)]" onClick={onClose} aria-label="Cerrar" />
      <div className="relative z-10 w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-lg font-semibold">{title}</h2>
        {children}
      </div>
    </div>
  );
}

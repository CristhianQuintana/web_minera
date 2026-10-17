import { AppShell } from "@/presentation/layouts/app-shell";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}

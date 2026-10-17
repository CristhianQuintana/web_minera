"use client";

import type { CurrentUser } from "@/domain/entities";
import { create } from "zustand";

interface SessionState {
  user: CurrentUser | null;
  setUser: (user: CurrentUser | null) => void;
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  sidebarCollapsed: false,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}));

export function can(permission: string): boolean {
  const user = useSessionStore.getState().user;
  return Boolean(user?.permissions.includes(permission));
}

"use client";

import { platform } from "@/composition/container";
import type { ListQuery } from "@/ports/outbound/platform-port";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export function useResource<T>(key: string, path: string, query: ListQuery) {
  return useQuery({
    queryKey: [key, query],
    queryFn: () => platform.list<T>(path, query),
  });
}

export function useDetail<T>(key: string, path: string | null) {
  return useQuery({
    queryKey: [key, path],
    queryFn: () => platform.get<T>(path as string),
    enabled: Boolean(path),
  });
}

export function useAction<T>(invalidate: string[]) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ path, body }: { path: string; body?: unknown }) =>
      platform.post<T>(path, body),
    onSuccess: () => {
      invalidate.forEach((key) => client.invalidateQueries({ queryKey: [key] }));
    },
  });
}

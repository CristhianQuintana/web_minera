import type { CurrentUser, PageResult } from "@/domain/entities";

export interface ListQuery {
  page?: number;
  page_size?: number;
  q?: string;
  status?: string;
  sort?: string;
  order?: string;
}

export interface PlatformPort {
  login(email: string, password: string): Promise<{ user: CurrentUser; access_token: string; refresh_token: string }>;
  logout(): Promise<void>;
  me(): Promise<CurrentUser>;
  forgotPassword(email: string): Promise<{ message: string }>;
  validateActivation(token: string): Promise<{ full_name: string; email: string }>;
  activate(payload: { token: string; full_name: string; password: string }): Promise<{ message: string }>;
  dashboard(): Promise<Record<string, unknown>>;
  list<T>(path: string, query?: ListQuery): Promise<PageResult<T>>;
  get<T>(path: string): Promise<T>;
  post<T>(path: string, body?: unknown): Promise<T>;
  search(q: string): Promise<{ lots: Array<Record<string, unknown>> }>;
}

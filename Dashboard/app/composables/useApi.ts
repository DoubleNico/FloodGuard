import type { FetchOptions } from "ofetch";

export const useApi = () => {
  const config = useRuntimeConfig();
  const token = useCookie<string | null>("hydralis_token");

  const apiFetch = <T>(path: string, opts: FetchOptions = {}): Promise<T> => {
    const headers: Record<string, string> = {
      ...(opts.headers as Record<string, string>),
    };
    if (token.value) {
      headers.Authorization = `Bearer ${token.value}`;
    }
    return $fetch<T>(`${config.public.apiBase}${path}`, {
      ...opts,
      headers,
    });
  };

  const get = <T>(path: string, opts?: FetchOptions) =>
    apiFetch<T>(path, { ...opts, method: "GET" });

  const post = <T>(path: string, body?: unknown, opts?: FetchOptions) =>
    apiFetch<T>(path, { ...opts, method: "POST", body: body as any });

  const patch = <T>(path: string, body?: unknown, opts?: FetchOptions) =>
    apiFetch<T>(path, { ...opts, method: "PATCH", body: body as any });

  const del = <T>(path: string, opts?: FetchOptions) =>
    apiFetch<T>(path, { ...opts, method: "DELETE" });

  return { apiFetch, get, post, patch, del };
};

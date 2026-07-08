const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function apiDelete(path: string): Promise<void> {
  const response = await fetch(`${API_BASE}${path}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(await response.text());
  }
}


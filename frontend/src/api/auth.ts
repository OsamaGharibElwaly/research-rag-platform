// src/api/auth.ts — Native Fetch API, no axios
import type { LoginCredentials, RegisterData, APIResponse, User, Tokens } from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Helper: get auth headers
function getHeaders(jsonContentType = true): Record<string, string> {
  const headers: Record<string, string> = {};
  const token = localStorage.getItem("access_token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (jsonContentType) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

function buildHeaders(options: RequestInit): Record<string, string> {
  const isFormData = options.body instanceof FormData;
  return {
    ...getHeaders(!isFormData),
    ...(options.headers as Record<string, string> | undefined),
  };
}

// Helper: parse JSON safely
async function parseJSON(response: Response): Promise<any> {
  const text = await response.text();
  return text ? JSON.parse(text) : {};
}

export function extractApiErrorMessage(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object") return fallback;

  const payload = data as Record<string, unknown>;

  if (typeof payload.message === "string") return payload.message;
  if (typeof payload.detail === "string") return payload.detail;

  if (Array.isArray(payload.detail)) {
    const messages = payload.detail.map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object") {
        const entry = item as { loc?: unknown[]; msg?: string };
        const field = Array.isArray(entry.loc)
          ? String(entry.loc[entry.loc.length - 1])
          : "field";
        return entry.msg ? `${field}: ${entry.msg}` : fallback;
      }
      return fallback;
    });
    return messages.join("; ");
  }

  return fallback;
}

// Core fetch wrapper with token refresh
async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const fullUrl = url.startsWith("http") ? url : `${API_BASE}${url}`;
  const response = await fetch(fullUrl, {
    ...options,
    headers: buildHeaders(options),
  });

  // Token expired — try refresh and retry once
  if (response.status === 401 && !url.includes('/auth/refresh')) {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        const refreshRes = await fetch(`${API_BASE}/api/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshRes.ok) {
          const refreshData = await parseJSON(refreshRes);
          const { access_token, refresh_token } = refreshData.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          // Retry original request with new token
          return fetch(fullUrl, {
            ...options,
            headers: buildHeaders(options),
          });
        }
      } catch {
        // Refresh failed
      }
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
  }

  return response;
}

// Helper: throw on error status
async function handleResponse<T>(response: Response): Promise<APIResponse<T>> {
  const data = await parseJSON(response);
  if (!response.ok) {
    const message = extractApiErrorMessage(data, `HTTP ${response.status}`);
    const error = new Error(message);
    (error as any).response = { status: response.status, data };
    throw error;
  }
  return data as APIResponse<T>;
}

// Auth API methods — each returns Promise<APIResponse<T>>
export const authApi = {
  register: (data: RegisterData): Promise<APIResponse<{ user: User; tokens: Tokens }>> =>
    fetchWithAuth('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }).then((res) => handleResponse<{ user: User; tokens: Tokens }>(res)),

  login: (data: LoginCredentials): Promise<APIResponse<{ user: User; tokens: Tokens }>> =>
    fetchWithAuth('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }).then((res) => handleResponse<{ user: User; tokens: Tokens }>(res)),

  refresh: (refreshToken: string): Promise<APIResponse<Tokens>> =>
    fetch(`${API_BASE}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    }).then((res) => handleResponse<Tokens>(res)),

  getMe: (): Promise<APIResponse<{ user: User }>> =>
    fetchWithAuth('/api/auth/me').then((res) =>
      handleResponse<{ user: User }>(res)
    ),

  health: (): Promise<any> =>
    fetch(`${API_BASE}/health`).then((res) => res.json()),
};

// Generic fetch for other services
export async function apiFetch<T>(
  url: string,
  options: RequestInit = {}
): Promise<APIResponse<T>> {
  const response = await fetchWithAuth(url, options);
  return handleResponse<T>(response);
}

export default authApi;
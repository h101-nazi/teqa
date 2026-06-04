const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, token } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Auth
  signup: (data: { email: string; password: string; full_name: string }) =>
    request<{ access_token: string; refresh_token: string }>("/auth/signup", {
      method: "POST",
      body: data,
    }),

  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: data,
    }),

  getMe: (token: string) =>
    request<{ id: string; email: string; full_name: string }>("/auth/me", { token }),

  // Business
  createBusiness: (token: string, data: Record<string, string>) =>
    request("/businesses/", { method: "POST", body: data, token }),

  getBusinesses: (token: string) =>
    request<Array<{ id: string; name: string; industry: string; is_onboarded: boolean }>>(
      "/businesses/",
      { token }
    ),

  // Reports
  getReports: (token: string, businessId: string) =>
    request<Array<Record<string, unknown>>>(`/reports/${businessId}`, { token }),

  getDashboard: (token: string, businessId: string) =>
    request<Record<string, unknown>>(`/reports/${businessId}/dashboard`, { token }),

  generateReport: (token: string, businessId: string) =>
    request(`/reports/${businessId}/generate`, { method: "POST", token }),

  // Integrations
  connectIntegration: (token: string, businessId: string, data: Record<string, unknown>) =>
    request(`/integrations/${businessId}/connect`, { method: "POST", body: data, token }),

  getIntegrations: (token: string, businessId: string) =>
    request<Array<Record<string, string>>>(`/integrations/${businessId}`, { token }),

  // Billing
  subscribe: (token: string, businessId: string, plan: string) =>
    request<{ checkout_url: string }>(`/billing/${businessId}/subscribe?plan=${plan}`, {
      method: "POST",
      token,
    }),

  getSubscription: (token: string, businessId: string) =>
    request<Record<string, unknown>>(`/billing/${businessId}/subscription`, { token }),
};

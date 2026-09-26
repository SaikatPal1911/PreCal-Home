const BASE_URL = 'http://localhost:8000';

function getToken(): string | null {
  return localStorage.getItem('renoai_token');
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ─── Auth ─────────────────────────────────────────────────────────────────
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: { id: string; name: string; email: string; phone?: string; avatar?: string; created_at: string };
}

export const authApi = {
  register: (name: string, email: string, phone: string, password: string) =>
    request<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, phone, password }),
    }),

  login: (email: string, password: string) =>
    request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<AuthResponse['user']>('/api/auth/me'),

  updateProfile: (data: { name?: string; phone?: string; avatar?: string }) =>
    request<AuthResponse['user']>('/api/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};

// ─── Analysis ─────────────────────────────────────────────────────────────
export const analysisApi = {
  run: (payload: object) =>
    request<any>('/api/analysis/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};

// ─── Projects ─────────────────────────────────────────────────────────────
export const projectsApi = {
  list: () => request<any[]>('/api/projects/'),

  create: (payload: { name: string; category: string; thumbnail?: string; budget?: number; result: object }) =>
    request<any>('/api/projects/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  delete: (id: string) =>
    request<void>(`/api/projects/${id}`, { method: 'DELETE' }),
};

// ─── Professionals ────────────────────────────────────────────────────────
export const professionalsApi = {
  list: (params?: { profession?: string; availability?: string; min_rating?: number }) => {
    const qs = new URLSearchParams();
    if (params?.profession) qs.set('profession', params.profession);
    if (params?.availability) qs.set('availability', params.availability);
    if (params?.min_rating !== undefined) qs.set('min_rating', String(params.min_rating));
    const query = qs.toString();
    return request<any[]>(`/api/professionals/${query ? '?' + query : ''}`);
  },

  get: (id: string) => request<any>(`/api/professionals/${id}`),

  book: (payload: {
    professional_id: string;
    customer_name: string;
    phone: string;
    location: string;
    category?: string;
    date: string;
    time_slot: string;
    requirements?: string;
  }) =>
    request<any>('/api/professionals/book', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  myBookings: () => request<any[]>('/api/professionals/bookings/me'),
};

// ─── Images ───────────────────────────────────────────────────────────────
export const imagesApi = {
  upload: async (file: File): Promise<{ id: string; filename: string; url: string }> => {
    const token = getToken();
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${BASE_URL}/api/images/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Upload failed');
    }
    const data = await res.json();
    return { ...data, url: `${BASE_URL}${data.url}` };
  },
};

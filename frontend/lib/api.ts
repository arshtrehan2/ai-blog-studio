const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  display_name: string;
  bio?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Post {
  id: string;
  title: string;
  slug: string;
  content: string;
  tags: string[];
  status: "draft" | "published";
  summary?: string;
  seo_title?: string;
  seo_description?: string;
  author_id: string;
  author: { id: string; display_name: string };
  published_at?: string;
  created_at: string;
  updated_at: string;
}

export interface PostListItem {
  id: string;
  title: string;
  slug: string;
  summary?: string;
  tags: string[];
  author: { id: string; display_name: string };
  created_at: string;
  updated_at: string;
}

export interface PostListResponse {
  items: PostListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PostCreatePayload {
  title: string;
  content: string;
  tags?: string[];
  status?: "draft" | "published";
  summary?: string;
  seo_title?: string;
  seo_description?: string;
}

export interface AIUsage {
  input_tokens: number;
  output_tokens: number;
}

// ─── API Client ─────────────────────────────────────────────────────────────

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = true
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw { status: res.status, detail: error.detail ?? "Unknown error" };
  }

  if (res.status === 204) return undefined as unknown as T;
  return res.json();
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export const authApi = {
  signup: (email: string, password: string, display_name: string) =>
    request<AuthResponse>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }, false),

  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false),

  logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),

  me: () => request<User>("/auth/me"),
};

// ─── Posts ───────────────────────────────────────────────────────────────────

export const postsApi = {
  list: (params?: { page?: number; page_size?: number; tag?: string; author_id?: string }) => {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    if (params?.tag) qs.set("tag", params.tag);
    if (params?.author_id) qs.set("author_id", params.author_id);
    return request<PostListResponse>(`/posts?${qs.toString()}`, {}, false);
  },

  get: (idOrSlug: string) => request<Post>(`/posts/${idOrSlug}`, {}, false),

  create: (payload: PostCreatePayload) =>
    request<Post>("/posts", { method: "POST", body: JSON.stringify(payload) }),

  update: (id: string, payload: Partial<PostCreatePayload>) =>
    request<Post>(`/posts/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  delete: (id: string) =>
    request<void>(`/posts/${id}`, { method: "DELETE" }),

  publish: (id: string) =>
    request<{ id: string; status: string; published_at: string; slug: string }>(
      `/posts/${id}/publish`,
      { method: "PATCH" }
    ),
};

// ─── AI ──────────────────────────────────────────────────────────────────────

export const aiApi = {
  improve: (content: string, context?: string) =>
    request<{ improved_content: string; model: string; usage: AIUsage }>(
      "/ai/improve",
      { method: "POST", body: JSON.stringify({ content, context }) }
    ),

  summary: (content: string, max_sentences = 3) =>
    request<{ summary: string; model: string; usage: AIUsage }>(
      "/ai/summary",
      { method: "POST", body: JSON.stringify({ content, max_sentences }) }
    ),

  tags: (content: string, title?: string, max_tags = 5) =>
    request<{ tags: string[]; model: string; usage: AIUsage }>(
      "/ai/tags",
      { method: "POST", body: JSON.stringify({ content, title, max_tags }) }
    ),

  seoTitle: (content: string, title?: string, target_keyword?: string) =>
    request<{
      seo_title: string;
      seo_description: string;
      model: string;
      usage: AIUsage;
    }>("/ai/seo-title", {
      method: "POST",
      body: JSON.stringify({ content, title, target_keyword }),
    }),

  tldr: (content: string) =>
    request<{ tldr: string; model: string; usage: AIUsage }>(
      "/ai/tldr",
      { method: "POST", body: JSON.stringify({ content }) }
    ),
};

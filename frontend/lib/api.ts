const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface User {
  id: string;
  email: string;
  display_name: string;
  bio?: string | null;
  created_at: string;
}

export interface TokenResponse {
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
  summary?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
  author_id?: string;
  author?: { id: string; display_name: string } | null;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PostListItem {
  id: string;
  title: string;
  slug: string;
  summary?: string | null;
  tags: string[];
  author?: { id: string; display_name: string } | null;
  published_at?: string | null;
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

export interface CreatePostRequest {
  title: string;
  content: string;
  tags?: string[];
  status?: "draft" | "published";
  summary?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
}

export interface UpdatePostRequest {
  title?: string;
  content?: string;
  tags?: string[];
  summary?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
}

export interface UsageInfo { input_tokens: number; output_tokens: number; }
export interface ImproveResponse { improved_content: string; model: string; usage: UsageInfo; }
export interface SummaryResponse { summary: string; model: string; usage: UsageInfo; }
export interface TagsResponse { tags: string[]; model: string; usage: UsageInfo; }
export interface SEOTitleResponse { seo_title: string; seo_description: string; model: string; usage: UsageInfo; }
export interface TLDRResponse { tldr: string; model: string; usage: UsageInfo; }

export class APIError extends Error {
  constructor(public status: number, message: string, public detail?: unknown) {
    super(message);
    this.name = "APIError";
  }
}

async function request<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    let detail: unknown;
    try { detail = await response.json(); } catch { detail = response.statusText; }
    throw new APIError(response.status, `API Error ${response.status}`, detail);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const authAPI = {
  signup: (data: { email: string; password: string; display_name: string }) =>
    request<TokenResponse>("/auth/signup", { method: "POST", body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  logout: (token: string) =>
    request<{ message: string }>("/auth/logout", { method: "POST" }, token),
  me: (token: string) => request<User>("/auth/me", {}, token),
};

export const postsAPI = {
  list: (params?: { page?: number; page_size?: number; tag?: string; author_id?: string }) => {
    const query = new URLSearchParams();
    if (params?.page) query.set("page", String(params.page));
    if (params?.page_size) query.set("page_size", String(params.page_size));
    if (params?.tag) query.set("tag", params.tag);
    if (params?.author_id) query.set("author_id", params.author_id);
    return request<PostListResponse>(`/posts?${query.toString()}`);
  },
  get: (idOrSlug: string, token?: string | null) => request<Post>(`/posts/${idOrSlug}`, {}, token),
  create: (data: CreatePostRequest, token: string) =>
    request<Post>("/posts", { method: "POST", body: JSON.stringify(data) }, token),
  update: (id: string, data: UpdatePostRequest, token: string) =>
    request<Post>(`/posts/${id}`, { method: "PUT", body: JSON.stringify(data) }, token),
  delete: (id: string, token: string) =>
    request<void>(`/posts/${id}`, { method: "DELETE" }, token),
  publish: (id: string, token: string) =>
    request<{ id: string; status: string; published_at: string; slug: string }>(
      `/posts/${id}/publish`, { method: "PATCH" }, token),
};

export const aiAPI = {
  improve: (data: { content: string; context?: string }, token: string) =>
    request<ImproveResponse>("/ai/improve", { method: "POST", body: JSON.stringify(data) }, token),
  summary: (data: { content: string; max_sentences?: number }, token: string) =>
    request<SummaryResponse>("/ai/summary", { method: "POST", body: JSON.stringify(data) }, token),
  tags: (data: { content: string; title?: string; max_tags?: number }, token: string) =>
    request<TagsResponse>("/ai/tags", { method: "POST", body: JSON.stringify(data) }, token),
  seoTitle: (data: { content: string; title?: string; target_keyword?: string }, token: string) =>
    request<SEOTitleResponse>("/ai/seo-title", { method: "POST", body: JSON.stringify(data) }, token),
  tldr: (data: { content: string }, token: string) =>
    request<TLDRResponse>("/ai/tldr", { method: "POST", body: JSON.stringify(data) }, token),
};

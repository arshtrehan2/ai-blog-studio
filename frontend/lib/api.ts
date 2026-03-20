import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT from localStorage on every request (browser only)
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Shared types ─────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  display_name: string;
  bio?: string;
  created_at: string;
}

export interface Author {
  id: string;
  display_name: string;
}

export interface Post {
  id: string;
  title: string;
  slug: string;
  content: string;
  tags: string[];
  status: 'draft' | 'published';
  summary?: string;
  seo_title?: string;
  seo_description?: string;
  author_id: string;
  author?: Author;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export interface PostListItem {
  id: string;
  title: string;
  slug: string;
  summary?: string;
  tags: string[];
  author: Author;
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

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AIUsage {
  input_tokens: number;
  output_tokens: number;
}

// ── Auth API ───────────────────────────────────────────────────────────────────

export const authAPI = {
  signup: (email: string, password: string, display_name: string) =>
    apiClient
      .post<AuthResponse>('/auth/signup', { email, password, display_name })
      .then((r) => r.data),

  login: (email: string, password: string) =>
    apiClient
      .post<AuthResponse>('/auth/login', { email, password })
      .then((r) => r.data),

  logout: () => apiClient.post('/auth/logout'),

  me: () => apiClient.get<User>('/auth/me').then((r) => r.data),
};

// ── Posts API ──────────────────────────────────────────────────────────────────

export const postsAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    tag?: string;
    author_id?: string;
  }) =>
    apiClient.get<PostListResponse>('/posts', { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Post>(`/posts/${id}`).then((r) => r.data),

  create: (post: Partial<Post>) =>
    apiClient.post<Post>('/posts', post).then((r) => r.data),

  update: (id: string, post: Partial<Post>) =>
    apiClient.put<Post>(`/posts/${id}`, post).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/posts/${id}`),

  publish: (id: string) =>
    apiClient
      .patch<{ id: string; status: string; published_at: string; slug: string }>(
        `/posts/${id}/publish`,
      )
      .then((r) => r.data),
};

// ── AI API ─────────────────────────────────────────────────────────────────────

export const aiAPI = {
  improve: (content: string, context?: string) =>
    apiClient
      .post<{ improved_content: string; model: string; usage: AIUsage }>(
        '/ai/improve',
        { content, context },
      )
      .then((r) => r.data),

  summary: (content: string, max_sentences?: number) =>
    apiClient
      .post<{ summary: string; model: string; usage: AIUsage }>('/ai/summary', {
        content,
        max_sentences,
      })
      .then((r) => r.data),

  tags: (content: string, title?: string, max_tags?: number) =>
    apiClient
      .post<{ tags: string[]; model: string; usage: AIUsage }>('/ai/tags', {
        content,
        title,
        max_tags,
      })
      .then((r) => r.data),

  seoTitle: (content: string, title?: string, target_keyword?: string) =>
    apiClient
      .post<{
        seo_title: string;
        seo_description: string;
        model: string;
        usage: AIUsage;
      }>('/ai/seo-title', { content, title, target_keyword })
      .then((r) => r.data),

  tldr: (content: string) =>
    apiClient
      .post<{ tldr: string; model: string; usage: AIUsage }>('/ai/tldr', { content })
      .then((r) => r.data),
};

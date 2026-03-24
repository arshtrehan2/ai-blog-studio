const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type User = {
  id: string;
  email: string;
  display_name: string;
  bio?: string | null;
  created_at: string;
};

export type Post = {
  id: string;
  title: string;
  slug: string;
  content: string;
  tags: string[];
  status: "draft" | "published";
  summary?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
  author_id: string;
  author?: { id: string; display_name: string } | null;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type PostListItem = {
  id: string;
  title: string;
  slug: string;
  summary?: string | null;
  tags: string[];
  author: { id: string; display_name: string };
  created_at: string;
  updated_at: string;
};

export type PaginatedPosts = {
  items: PostListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type AIUsage = {
  input_tokens: number;
  output_tokens: number;
};

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private getHeaders(auth = false): HeadersInit {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (auth) {
      const token = this.getToken();
      if (token) {
        (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
      }
    }
    return headers;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {},
    auth = false
  ): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: { ...this.getHeaders(auth), ...(options.headers || {}) },
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      const err = new Error(error.detail || "Request failed");
      (err as any).status = res.status;
      throw err;
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  }

  // Auth
  async signup(email: string, password: string, display_name: string): Promise<AuthResponse> {
    return this.request("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    });
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async logout(): Promise<void> {
    return this.request("/auth/logout", { method: "POST" }, true);
  }

  async getMe(): Promise<User> {
    return this.request("/auth/me", {}, true);
  }

  // Posts
  async getPosts(params?: {
    page?: number;
    page_size?: number;
    tag?: string;
    author_id?: string;
  }): Promise<PaginatedPosts> {
    const query = new URLSearchParams();
    if (params?.page) query.set("page", String(params.page));
    if (params?.page_size) query.set("page_size", String(params.page_size));
    if (params?.tag) query.set("tag", params.tag);
    if (params?.author_id) query.set("author_id", params.author_id);
    const qs = query.toString();
    return this.request(`/posts${qs ? `?${qs}` : ""}`);
  }

  async getPost(idOrSlug: string): Promise<Post> {
    return this.request(`/posts/${idOrSlug}`, {}, true);
  }

  async createPost(data: {
    title: string;
    content: string;
    tags?: string[];
    status?: string;
    summary?: string;
    seo_title?: string;
    seo_description?: string;
  }): Promise<Post> {
    return this.request("/posts", { method: "POST", body: JSON.stringify(data) }, true);
  }

  async updatePost(
    id: string,
    data: {
      title?: string;
      content?: string;
      tags?: string[];
      summary?: string;
      seo_title?: string;
      seo_description?: string;
    }
  ): Promise<Post> {
    return this.request(`/posts/${id}`, { method: "PUT", body: JSON.stringify(data) }, true);
  }

  async deletePost(id: string): Promise<void> {
    return this.request(`/posts/${id}`, { method: "DELETE" }, true);
  }

  async publishPost(id: string): Promise<{ id: string; status: string; published_at: string; slug: string }> {
    return this.request(`/posts/${id}/publish`, { method: "PATCH" }, true);
  }

  // AI
  async improveContent(content: string, context?: string): Promise<{
    improved_content: string;
    model: string;
    usage: AIUsage;
  }> {
    return this.request("/ai/improve", {
      method: "POST",
      body: JSON.stringify({ content, context }),
    }, true);
  }

  async summarizeContent(content: string, max_sentences = 3): Promise<{
    summary: string;
    model: string;
    usage: AIUsage;
  }> {
    return this.request("/ai/summary", {
      method: "POST",
      body: JSON.stringify({ content, max_sentences }),
    }, true);
  }

  async suggestTags(content: string, title?: string, max_tags = 5): Promise<{
    tags: string[];
    model: string;
    usage: AIUsage;
  }> {
    return this.request("/ai/tags", {
      method: "POST",
      body: JSON.stringify({ content, title, max_tags }),
    }, true);
  }

  async generateSeoTitle(content: string, title?: string, target_keyword?: string): Promise<{
    seo_title: string;
    seo_description: string;
    model: string;
    usage: AIUsage;
  }> {
    return this.request("/ai/seo-title", {
      method: "POST",
      body: JSON.stringify({ content, title, target_keyword }),
    }, true);
  }

  async generateTldr(content: string): Promise<{
    tldr: string;
    model: string;
    usage: AIUsage;
  }> {
    return this.request("/ai/tldr", {
      method: "POST",
      body: JSON.stringify({ content }),
    }, true);
  }
}

export const api = new ApiClient(API_URL);

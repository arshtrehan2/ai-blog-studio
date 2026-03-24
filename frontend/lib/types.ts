/** Shared TypeScript types that mirror the backend Pydantic schemas. */

export interface User {
  id: string;
  email: string;
  display_name: string;
  bio?: string | null;
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
  status: "draft" | "published";
  summary?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
  author_id?: string | null;
  author?: Author | null;
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
  author?: Author | null;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedPosts {
  items: PostListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type AIToolStatus = "idle" | "loading" | "suggestion" | "accepted";

export interface ImproveResponse {
  improved_content: string;
  model: string;
  usage: { input_tokens: number; output_tokens: number };
}

export interface SummaryResponse {
  summary: string;
  model: string;
  usage: { input_tokens: number; output_tokens: number };
}

export interface TagsResponse {
  tags: string[];
  model: string;
  usage: { input_tokens: number; output_tokens: number };
}

export interface SeoTitleResponse {
  seo_title: string;
  seo_description: string;
  model: string;
  usage: { input_tokens: number; output_tokens: number };
}

export interface TldrResponse {
  tldr: string;
  model: string;
  usage: { input_tokens: number; output_tokens: number };
}

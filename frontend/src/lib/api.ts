import { Article, ArticleDetail, Category, Subcategory } from "@/types/article";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type ArticlesResponse = {
  items: Article[];
  nextCursor: string | null;
};

type ArticleSort = "recent" | "confidence";

type FetchArticlesOptions = {
  limit?: number;
  sort?: ArticleSort;
  subcategory?: Subcategory;
  cursor?: string;
};

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, init);

  if (!res.ok) {
    const error = (await res.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(error?.detail ?? `API request failed: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function fetchArticlesByCategory(
  category: Category,
  options: FetchArticlesOptions = {},
): Promise<ArticlesResponse> {
  const params = new URLSearchParams({
    category,
    limit: String(options.limit ?? 3),
    sort: options.sort ?? "recent",
  });

  if (options.subcategory) params.set("subcategory", options.subcategory);
  if (options.cursor) params.set("cursor", options.cursor);

  return fetchJson<ArticlesResponse>(`/articles?${params.toString()}`, { cache: "no-store" });
}

export async function fetchRandomArticles(limit = 10): Promise<Article[]> {
  const params = new URLSearchParams({ limit: String(limit) });

  return fetchJson<Article[]>(`/articles/random?${params.toString()}`);
}

export async function fetchArticleById(id: string): Promise<ArticleDetail | null> {
  const res = await fetch(`${API_BASE_URL}/articles/${id}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`API request failed: ${res.status}`);
  return res.json();
}

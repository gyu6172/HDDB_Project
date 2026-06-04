import { Article, ArticleDetail } from "@/types/article";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface ArticleListResponse {
  items: Article[];
  nextCursor: string | null;
}

export async function fetchArticlesByCategory(params: {
  category: string;
  sort?: "recent" | "confidence";
  limit?: number;
}): Promise<ArticleListResponse> {
  const sp = new URLSearchParams({
    category: params.category,
    sort: params.sort ?? "recent",
    limit: String(params.limit ?? 100),
  });
  const res = await fetch(`${BASE}/articles?${sp}`, { cache: "no-store" });
  if (!res.ok) return { items: [], nextCursor: null };
  return res.json();
}

export async function fetchArticleById(id: string): Promise<ArticleDetail | null> {
  const res = await fetch(`${BASE}/articles/${id}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch article");
  return res.json();
}

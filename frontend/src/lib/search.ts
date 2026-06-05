import { CATEGORY_META } from "@/constants/category";
import { Article, Category } from "@/types/article";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type SearchCategory = Category | "all";
export type SearchSort = "latest" | "relevance";
export type SearchStatus = "idle" | "success" | "error";

export type SearchResultArticle = Omit<Article, "confidence"> & {
  confidence: number | null;
  similarity: number;
};

export interface SearchArticlesParams {
  query: string;
  category: SearchCategory;
  sort: SearchSort;
}

export type SearchCategoryCounts = Record<SearchCategory, number>;

export interface SearchArticlesResult {
  items: SearchResultArticle[];
  categoryCounts: SearchCategoryCounts;
  status: SearchStatus;
}

interface SearchApiResponse {
  items: SearchResultArticle[];
}

interface SearchFetchResult {
  items: SearchResultArticle[];
  failed: boolean;
}

export const SEARCH_CATEGORY_OPTIONS: { value: SearchCategory; label: string }[] = [
  { value: "all", label: "전체" },
  { value: "sky", label: CATEGORY_META.sky.label },
  { value: "land", label: CATEGORY_META.land.label },
  { value: "sea", label: CATEGORY_META.sea.label },
];

export const SEARCH_SORT_OPTIONS: { value: SearchSort; label: string }[] = [
  { value: "latest", label: "최신순" },
  { value: "relevance", label: "관련도순" },
];

export function normalizeSearchCategory(value?: string): SearchCategory {
  return SEARCH_CATEGORY_OPTIONS.some((option) => option.value === value)
    ? (value as SearchCategory)
    : "all";
}

export function normalizeSearchSort(value?: string): SearchSort {
  return value === "relevance" ? "relevance" : "latest";
}

export function getSearchCategoryCounts(articles: { category: Category }[]): SearchCategoryCounts {
  return articles.reduce<SearchCategoryCounts>(
    (counts, article) => {
      counts.all += 1;
      counts[article.category] += 1;
      return counts;
    },
    { all: 0, sky: 0, land: 0, sea: 0 },
  );
}

export async function fetchSearchResults(query: string, sort: SearchSort): Promise<SearchFetchResult> {
  const trimmedQuery = query.trim();
  if (!trimmedQuery) return { items: [], failed: false };

  try {
    const res = await fetch(`${API_BASE_URL}/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: trimmedQuery,
        sort,
      }),
      cache: "no-store",
    });

    if (!res.ok) return { items: [], failed: true };

    const data = (await res.json()) as SearchApiResponse;
    return { items: data.items, failed: false };
  } catch {
    return { items: [], failed: true };
  }
}

export async function searchArticles({
  query,
  category,
  sort,
}: SearchArticlesParams): Promise<SearchArticlesResult> {
  const isIdle = query.trim().length === 0;
  const searchResponse = await fetchSearchResults(query, sort);
  const searchResults = searchResponse.items;
  const categoryCounts = getSearchCategoryCounts(searchResults);
  const filteredResults = category === "all"
    ? searchResults
    : searchResults.filter((article) => article.category === category);

  return {
    items: filteredResults,
    categoryCounts,
    status: isIdle ? "idle" : searchResponse.failed ? "error" : "success",
  };
}

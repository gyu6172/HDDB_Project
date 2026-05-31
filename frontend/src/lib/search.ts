import { CATEGORY_META } from "@/constants/category";
import { mockArticles } from "@/lib/mockData";
import { Article, Category } from "@/types/article";

export type SearchCategory = Category | "all";
export type SearchSort = "latest" | "relevance";

export interface SearchArticlesParams {
  query: string;
  category: SearchCategory;
  sort: SearchSort;
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

export async function searchArticles({
  category,
  sort,
}: SearchArticlesParams): Promise<Article[]> {
  const results = category === "all"
    ? [...mockArticles]
    : mockArticles.filter((article) => article.category === category);

  return results.sort((a, b) => {
    if (sort === "relevance") {
      return b.confidence - a.confidence;
    }

    return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
  });
}

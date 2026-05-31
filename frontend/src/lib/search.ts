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

export type SearchCategoryCounts = Record<SearchCategory, number>;

export interface SearchArticlesResult {
  items: Article[];
  categoryCounts: SearchCategoryCounts;
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

export function sortSearchResults(articles: Article[], sort: SearchSort) {
  return [...articles].sort((a, b) => {
    if (sort === "relevance") {
      return b.confidence - a.confidence;
    }

    return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
  });
}

export function getSearchCategoryCounts(articles: Article[]): SearchCategoryCounts {
  return articles.reduce<SearchCategoryCounts>(
    (counts, article) => {
      counts.all += 1;
      counts[article.category] += 1;
      return counts;
    },
    { all: 0, sky: 0, land: 0, sea: 0 },
  );
}

export async function searchArticles({
  category,
  sort,
}: SearchArticlesParams): Promise<SearchArticlesResult> {
  const categoryCounts = getSearchCategoryCounts(mockArticles);
  const filteredResults = category === "all"
    ? mockArticles
    : mockArticles.filter((article) => article.category === category);

  return {
    items: sortSearchResults(filteredResults, sort),
    categoryCounts,
  };
}

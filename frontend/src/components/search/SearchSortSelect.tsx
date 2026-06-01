"use client";

import { useRouter } from "next/navigation";
import { SEARCH_SORT_OPTIONS, SearchCategory, SearchSort } from "@/lib/search";

interface Props {
  query: string;
  category: SearchCategory;
  sort: SearchSort;
}

export default function SearchSortSelect({ query, category, sort }: Props) {
  const router = useRouter();

  function handleSortChange(nextSort: SearchSort) {
    const params = new URLSearchParams();

    if (query) params.set("q", query);
    if (category !== "all") params.set("category", category);
    if (nextSort !== "latest") params.set("sort", nextSort);

    const nextQuery = params.toString();
    router.push(`/search${nextQuery ? `?${nextQuery}` : ""}`);
  }

  return (
    <select
      value={sort}
      onChange={(event) => handleSortChange(event.target.value as SearchSort)}
      className="h-14 rounded-xl border border-line bg-card px-5 text-body-sm font-bold text-text outline-none transition focus:border-brand"
    >
      {SEARCH_SORT_OPTIONS.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}

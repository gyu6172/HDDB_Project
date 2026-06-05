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
    router.replace(`/search${nextQuery ? `?${nextQuery}` : ""}`);
  }

  return (
    <div className="flex items-center gap-1 rounded-lg border border-line bg-card p-0.5">
      {SEARCH_SORT_OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => handleSortChange(option.value)}
          className={`rounded-md px-3 py-1 text-label font-medium transition-colors ${
            option.value === sort
              ? "bg-brand text-white"
              : "text-muted hover:text-text"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

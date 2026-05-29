"use client";

import { useRouter } from "next/navigation";

interface Props {
  category: string;
  activeSubs: string[];
  activeSort: string;
}

export default function Sort({ category, activeSubs, activeSort }: Props) {
  const router = useRouter();
  const hasFilter = activeSubs.length > 0;

  function buildUrl(sort: string) {
    const subParam = activeSubs.length > 0 ? `sub=${activeSubs.join(",")}` : "";
    const sortParam = sort === "relevance" ? "sort=relevance" : "";
    const query = [subParam, sortParam].filter(Boolean).join("&");
    return `/category/${category}${query ? `?${query}` : ""}`;
  }

  return (
    <div className="flex items-center gap-1 rounded-lg border border-line bg-card p-0.5">
      <button
        onClick={() => router.push(buildUrl("latest"))}
        className={`px-3 py-1 rounded-md text-label font-medium transition-colors ${
          activeSort === "latest"
            ? "bg-brand text-white"
            : "text-muted hover:text-text"
        }`}
      >
        최신순
      </button>

      <div className="relative group">
        <button
          onClick={() => hasFilter && router.push(buildUrl("relevance"))}
          disabled={!hasFilter}
          className={`px-3 py-1 rounded-md text-label font-medium transition-colors ${
            activeSort === "relevance"
              ? "bg-brand text-white"
              : hasFilter
              ? "text-muted hover:text-text"
              : "text-muted/40 cursor-not-allowed"
          }`}
        >
          관련도순
        </button>
        {!hasFilter && (
          <div className="absolute right-0 top-full mt-1.5 px-2.5 py-1.5 rounded-md bg-text text-white text-caption whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
            필터를 먼저 선택해주세요!
          </div>
        )}
      </div>
    </div>
  );
}

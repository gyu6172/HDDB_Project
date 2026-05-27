"use client";

import { useRouter } from "next/navigation";

interface Props {
  category: string;
  activeSubs: string[];
  activeSort: string;
}

const SORT_OPTIONS = [
  { value: "latest", label: "최신순" },
  { value: "relevance", label: "관련도순" },
];

export default function Sort({ category, activeSubs, activeSort }: Props) {
  const router = useRouter();

  function buildUrl(sort: string) {
    const subParam = activeSubs.length > 0 ? `sub=${activeSubs.join(",")}` : "";
    const sortParam = sort === "relevance" ? "sort=relevance" : "";
    const query = [subParam, sortParam].filter(Boolean).join("&");
    return `/category/${category}${query ? `?${query}` : ""}`;
  }

  return (
    <select
      value={activeSort}
      onChange={(e) => router.push(buildUrl(e.target.value))}
      className="px-3 py-1.5 rounded-lg text-label text-text bg-card border border-line cursor-pointer focus:outline-none focus:border-brand"
    >
      {SORT_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

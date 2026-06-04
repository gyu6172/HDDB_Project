"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SearchButton() {
  const [query, setQuery] = useState("");
  const router = useRouter();

  function handleSearch() {
    const trimmed = query.trim();
    if (trimmed) {
      router.push(`/search?q=${encodeURIComponent(trimmed)}`);
    }
  }

  return (
    <div className="flex items-center gap-1.5 rounded-full border border-line px-3 py-1 bg-white/80">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted flex-shrink-0">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        placeholder="검색어 입력..."
        className="w-32 text-label text-text placeholder:text-muted outline-none bg-transparent"
      />
    </div>
  );
}

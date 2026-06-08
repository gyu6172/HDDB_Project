"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SearchIcon, SendIcon } from "@/components/main/MainIcons";

export default function SearchDock() {
  const [query, setQuery] = useState("");
  const router = useRouter();

  function handleSearch() {
    const trimmed = query.trim();
    if (trimmed) {
      router.push(`/search?q=${encodeURIComponent(trimmed)}`);
    }
  }

  return (
    <div className="flex h-16 w-full max-w-[440px] items-center gap-4 rounded-full bg-card px-7 shadow-sm">
      <SearchIcon className="size-7 text-muted" />

      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        placeholder="원하는 뉴스를 검색해보세요"
        className="flex-1 bg-transparent text-xl font-semibold text-text placeholder:text-muted outline-none"
      />

      <button
        type="button"
        onClick={handleSearch}
        aria-label="검색 전송"
        className="flex size-12 items-center justify-center rounded-full bg-brand text-white"
      >
        <SendIcon />
      </button>
    </div>
  );
}

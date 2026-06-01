import Link from "next/link";

export default function SearchButton() {
  return (
    <Link
      href="/search"
      className="p-1.5 text-muted hover:text-text transition-colors"
      aria-label="검색"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
    </Link>
  );
}

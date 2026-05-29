import Link from "next/link";

interface Props {
  currentPage: number;
  totalPages: number;
  buildUrl: (page: number) => string;
}

export default function Pagination({ currentPage, totalPages, buildUrl }: Props) {
  if (totalPages <= 1) return null;

  const pages = getPageNumbers(currentPage, totalPages);

  return (
    <div className="flex items-center justify-center gap-1 mt-10">
      <Link
        href={buildUrl(currentPage - 1)}
        aria-disabled={currentPage === 1}
        className={`w-8 h-8 flex items-center justify-center rounded-lg text-label transition-colors ${
          currentPage === 1
            ? "text-muted/30 pointer-events-none"
            : "text-muted hover:bg-black/5"
        }`}
      >
        ‹
      </Link>

      {pages.map((page, i) =>
        page === "..." ? (
          <span key={`ellipsis-${i}`} className="w-8 h-8 flex items-center justify-center text-label text-muted/50">
            …
          </span>
        ) : (
          <Link
            key={page}
            href={buildUrl(page as number)}
            className={`w-8 h-8 flex items-center justify-center rounded-lg text-label font-medium transition-colors ${
              page === currentPage
                ? "bg-brand text-white"
                : "text-muted hover:bg-black/5"
            }`}
          >
            {page}
          </Link>
        )
      )}

      <Link
        href={buildUrl(currentPage + 1)}
        aria-disabled={currentPage === totalPages}
        className={`w-8 h-8 flex items-center justify-center rounded-lg text-label transition-colors ${
          currentPage === totalPages
            ? "text-muted/30 pointer-events-none"
            : "text-muted hover:bg-black/5"
        }`}
      >
        ›
      </Link>
    </div>
  );
}

function getPageNumbers(current: number, total: number): (number | "...")[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);

  if (current <= 4) return [1, 2, 3, 4, 5, "...", total];
  if (current >= total - 3) return [1, "...", total - 4, total - 3, total - 2, total - 1, total];
  return [1, "...", current - 1, current, current + 1, "...", total];
}

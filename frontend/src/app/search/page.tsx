import Link from "next/link";
import {
  normalizeSearchCategory,
  normalizeSearchSort,
  searchArticles,
  SEARCH_CATEGORY_OPTIONS,
  SearchCategory,
  SearchSort,
} from "@/lib/search";
import SearchResultItem from "@/components/search/SearchResultItem";
import SearchSortSelect from "@/components/search/SearchSortSelect";

function buildSearchUrl(query: string, category: SearchCategory, sort: SearchSort) {
  const params = new URLSearchParams();

  if (query) params.set("q", query);
  if (category !== "all") params.set("category", category);
  if (sort !== "latest") params.set("sort", sort);

  const nextQuery = params.toString();
  return `/search${nextQuery ? `?${nextQuery}` : ""}`;
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string; sort?: string }>;
}) {
  const params = await searchParams;
  const query = params.q?.trim() ?? "";
  const category = normalizeSearchCategory(params.category);
  const sort = normalizeSearchSort(params.sort);
  const { items: results, categoryCounts } = await searchArticles({ query, category, sort });
  const searchLabel = query || "전체";

  return (
    <main className="min-h-screen bg-bg px-5 py-8 md:px-8">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <form action="/search" className="relative max-w-[680px]">
          <span className="pointer-events-none absolute left-8 top-1/2 -translate-y-1/2 text-[30px]" aria-hidden="true">
            🔍
          </span>
          <input
            type="search"
            name="q"
            defaultValue={query}
            placeholder="검색어를 입력하세요"
            className="h-[78px] w-full rounded-[38px] border-2 border-brand bg-card pl-24 pr-8 text-[24px] font-medium text-text outline-none shadow-sm transition placeholder:text-muted focus:border-brand"
          />
        </form>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <p className="text-heading-sm font-bold text-text">
            “{searchLabel}” 검색 결과 {results.length}건
          </p>

          <SearchSortSelect query={query} category={category} sort={sort} />
        </div>

        <nav className="flex flex-wrap gap-3" aria-label="검색 카테고리">
          {SEARCH_CATEGORY_OPTIONS.map((option) => (
            <Link
              key={option.value}
              href={buildSearchUrl(query, option.value, sort)}
              className={`inline-flex h-14 min-w-[78px] items-center justify-center rounded-full border px-6 text-body font-bold transition ${
                option.value === category
                  ? "border-brand bg-brand text-white"
                  : "border-line bg-card text-muted hover:border-brand hover:text-brand"
              }`}
            >
              <span>{option.label}</span>
              <span className={option.value === category ? "ml-2 text-white" : "ml-2 text-muted"}>
                {categoryCounts[option.value]}
              </span>
            </Link>
          ))}
        </nav>

        {results.length > 0 ? (
          <div className="flex flex-col gap-5">
            {results.map((article) => (
              <SearchResultItem key={article.id} article={article} />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-line bg-card px-6 py-20 text-center text-body text-muted">
            검색 결과가 없어요.
          </div>
        )}
      </section>
    </main>
  );
}

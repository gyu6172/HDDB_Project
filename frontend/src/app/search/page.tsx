import Link from "next/link";
import { CATEGORY_META } from "@/constants/category";
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
import { SearchIcon } from "@/components/main/MainIcons";
import Pagination from "@/components/common/Pagination";
import BackButton from "@/components/common/BackButton";

const PAGE_SIZE = 10;

function buildSearchUrl(query: string, category: SearchCategory, sort: SearchSort, page = 1) {
  const params = new URLSearchParams();

  if (query) params.set("q", query);
  if (category !== "all") params.set("category", category);
  if (sort !== "latest") params.set("sort", sort);
  if (page > 1) params.set("page", String(page));

  const nextQuery = params.toString();
  return `/search${nextQuery ? `?${nextQuery}` : ""}`;
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string; sort?: string; page?: string }>;
}) {
  const params = await searchParams;
  const query = params.q?.trim() ?? "";
  const category = normalizeSearchCategory(params.category);
  const sort = normalizeSearchSort(params.sort);
  const { items: results, categoryCounts, status } = await searchArticles({ query, category, sort });
  const searchLabel = query || "전체";
  const currentPage = Math.max(1, Number(params.page) || 1);
  const totalPages = Math.max(1, Math.ceil(results.length / PAGE_SIZE));
  const safePage = Math.min(currentPage, totalPages);
  const pagedResults = results.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  return (
    <main className="min-h-screen bg-bg px-5 py-8 md:px-8">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <BackButton />

        <form action="/search" className="relative max-w-[560px]">
          <SearchIcon className="pointer-events-none absolute left-5 top-1/2 size-6 -translate-y-1/2 text-muted" />
          <input
            type="search"
            name="q"
            defaultValue={query}
            placeholder="검색어를 입력하세요"
            className="h-14 w-full rounded-full border border-line bg-card pl-14 pr-5 text-body-sm font-semibold text-text outline-none shadow-sm transition placeholder:text-muted focus:border-brand"
          />
        </form>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <p className="text-body font-bold text-text">
            “{searchLabel}” 검색 결과 {results.length}건
          </p>

          <SearchSortSelect query={query} category={category} sort={sort} />
        </div>

        <nav className="flex flex-wrap gap-3" aria-label="검색 카테고리">
          {SEARCH_CATEGORY_OPTIONS.map((option) => (
            <Link
              key={option.value}
              href={buildSearchUrl(query, option.value, sort)}
              replace
              className={`inline-flex items-center justify-center rounded-full px-4 py-1.5 text-label font-medium transition-colors ${
                option.value === category
                  ? "border-brand bg-brand text-white"
                  : "border-line bg-card text-muted hover:border-brand hover:text-brand"
              }`}
            >
              {option.value !== "all" && (
                <span className="mr-1.5">{CATEGORY_META[option.value].emoji}</span>
              )}
              <span>{option.label}</span>
              <span className={option.value === category ? "ml-2 text-white" : "ml-2 text-muted"}>
                {categoryCounts[option.value]}
              </span>
            </Link>
          ))}
        </nav>

        {status === "idle" ? (
          <div className="rounded-2xl border border-line bg-card px-6 py-20 text-center text-body text-muted">
            검색어를 입력해주세요.
          </div>
        ) : status === "error" ? (
          <div className="rounded-2xl border border-line bg-card px-6 py-20 text-center text-body text-muted">
            검색 결과를 불러오지 못했어요.
          </div>
        ) : results.length > 0 ? (
          <>
            <div className="flex flex-col gap-5">
              {pagedResults.map((article) => (
                <SearchResultItem key={article.id} article={article} />
              ))}
            </div>
            <Pagination
              currentPage={safePage}
              totalPages={totalPages}
              buildUrl={(page) => buildSearchUrl(query, category, sort, page)}
            />
          </>
        ) : (
          <div className="rounded-2xl border border-line bg-card px-6 py-20 text-center text-body text-muted">
            검색 결과가 없어요.
          </div>
        )}
      </section>
    </main>
  );
}

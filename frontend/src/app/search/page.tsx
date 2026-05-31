import {
  normalizeSearchCategory,
  normalizeSearchSort,
  searchArticles,
  SEARCH_CATEGORY_OPTIONS,
  SEARCH_SORT_OPTIONS,
} from "@/lib/search";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string; sort?: string }>;
}) {
  const params = await searchParams;
  const query = params.q?.trim() ?? "";
  const category = normalizeSearchCategory(params.category);
  const sort = normalizeSearchSort(params.sort);
  const results = await searchArticles({ query, category, sort });
  const searchLabel = query || "전체";

  return (
    <main className="min-h-screen bg-bg px-8 py-10">
      <section className="mx-auto flex max-w-5xl flex-col gap-8">
        <div className="rounded-2xl border border-line bg-card px-6 py-5">
          <p className="text-label font-semibold text-muted">검색어</p>
          <h1 className="mt-2 text-heading font-bold text-text">{searchLabel}</h1>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-heading-sm font-bold text-text">
              “{searchLabel}” 검색 결과 {results.length}건
            </p>
            <p className="mt-2 text-label text-muted">
              category={category} · sort={sort}
            </p>
          </div>

          <div className="rounded-xl border border-line bg-card px-4 py-3 text-label text-muted">
            정렬: {SEARCH_SORT_OPTIONS.find((option) => option.value === sort)?.label}
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          {SEARCH_CATEGORY_OPTIONS.map((option) => (
            <span
              key={option.value}
              className={`rounded-full border px-4 py-2 text-label font-semibold ${
                option.value === category
                  ? "border-brand bg-brand text-white"
                  : "border-line bg-card text-muted"
              }`}
            >
              {option.label}
            </span>
          ))}
        </div>

        <div className="rounded-2xl border border-line bg-card p-6">
          <h2 className="text-body font-bold text-text">결과 제목 목록</h2>
          <ul className="mt-4 space-y-3">
            {results.map((article) => (
              <li key={article.id} className="text-body-sm text-text">
                {article.title}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}

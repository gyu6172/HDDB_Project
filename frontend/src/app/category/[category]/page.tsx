import { notFound } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import ArticleCard from "@/components/common/ArticleCard";
import Sort from "@/components/common/Sort";
import Pagination from "@/components/common/Pagination";
import BackButton from "@/components/common/BackButton";
import SearchButton from "@/components/common/SearchButton";
import { mockArticles } from "@/lib/mockData";
import { Category, Subcategory } from "@/types/article";
import { CATEGORY_META, SUBCATEGORY_META, SUBCATEGORIES, VALID_CATEGORIES } from "@/constants/category";

const CATEGORY_BG: Record<Category, string> = {
  sky:  "/images/bg-sky.jpg",
  land: "/images/bg-land.jpg",
  sea:  "/images/bg-sea.jpg",
};

export default async function CategoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ sub?: string; sort?: string; page?: string }>;
}) {
  const { category: rawCategory } = await params;
  const { sub, sort, page } = await searchParams;

  if (!VALID_CATEGORIES.includes(rawCategory as Category)) notFound();

  const category = rawCategory as Category;
  const { label, emoji, gradient, desc } = CATEGORY_META[category];
  const subcategories = SUBCATEGORIES[category];

  // sub 파라미터 없음 = 전체, sub="" = 아무것도 미선택, sub="bird,..." = 필터링
  const isAllActive = sub === undefined;
  const isEmptyState = !isAllActive && (!sub || sub.length === 0);
  const activeSubs: Subcategory[] = (!isAllActive && sub && sub.length > 0)
    ? (sub.split(",") as Subcategory[])
    : [];

  const activeSort = (sort === "relevance" && activeSubs.length > 0) ? "relevance" : "latest";
  const PAGE_SIZE = 9;
  const currentPage = Math.max(1, Number(page) || 1);

  const filtered = isEmptyState
    ? []
    : mockArticles
        .filter((a) => a.category === category && (isAllActive || activeSubs.includes(a.subcategory)))
        .sort((a, b) =>
          activeSort === "relevance"
            ? b.confidence - a.confidence
            : new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
        );

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(currentPage, totalPages);
  const articles = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  // subs === null → sub 파라미터 없음 (전체), subs === [] → sub= (미선택)
  function buildCategoryUrl(subs: Subcategory[] | null, newSort: string, p = 1) {
    const subParam = subs !== null ? `sub=${subs.join(",")}` : "";
    const sortParam = newSort === "relevance" ? "sort=relevance" : "";
    const pageParam = p > 1 ? `page=${p}` : "";
    const query = [subParam, sortParam, pageParam].filter(Boolean).join("&");
    return `/category/${category}${query ? `?${query}` : ""}`;
  }

  function buildSubUrl(toggleSub: Subcategory) {
    if (isAllActive) {
      // 전체 상태에서 클릭 → 해당 항목만 제외한 나머지 선택
      return buildCategoryUrl(subcategories.filter((s) => s !== toggleSub), activeSort);
    }
    const next = activeSubs.includes(toggleSub)
      ? activeSubs.filter((s) => s !== toggleSub)
      : [...activeSubs, toggleSub];
    const isAll = next.length === subcategories.length;
    return buildCategoryUrl(isAll ? null : next, activeSort);
  }

  return (
    <div className="relative min-h-screen flex flex-col">
      {/* 전체 페이지 배경 이미지 */}
      <div className="fixed inset-0 -z-10" aria-hidden="true">
        <Image
          src={CATEGORY_BG[category]}
          alt=""
          fill
          sizes="100vw"
          className="object-cover"
          aria-hidden="true"
        />
      </div>

      {/* 헤더: 프로스티드 글라스 — 이미지가 옅게 비치며 카테고리 색 틴트 */}
      {/* 불투명도 조정 포인트: bg-white/[.90] 값 */}
      <div className={`backdrop-blur-[2px] bg-white/60 bg-gradient-to-br ${gradient} border-b border-black/10`}>
        <div className="max-w-6xl mx-auto px-6 pt-5 pb-8">
          <div className="flex items-center justify-between">
            <BackButton />
            <SearchButton />
          </div>
          <div className="mt-4">
            <h1 className="text-heading font-bold text-text">
              {emoji} {label}
            </h1>
            <p className="text-body-sm text-muted mt-1.5">{desc}</p>
          </div>
        </div>
      </div>

      {/* 콘텐츠: 가벼운 흰색 워시 — 불투명도 조정 포인트: rgba 세 번째 인자(현재 0.60) */}
      <div className="relative flex-1" style={{ background: "rgba(255,255,255,0.60)" }}>
        <div className="relative max-w-6xl mx-auto px-6 py-3">
          {/* 서브카테고리 필터 + 정렬 */}
          <div className="flex items-center justify-between gap-4 mt-1 mb-5">
            <div className="flex items-center gap-2 flex-wrap">
              <Link
                href={isAllActive ? buildCategoryUrl([], activeSort) : buildCategoryUrl(null, activeSort)}
                className={`px-4 py-1.5 rounded-lg text-label font-medium transition-colors ${
                  isAllActive
                    ? "bg-brand text-white"
                    : "bg-card border border-line text-muted hover:border-brand hover:text-brand"
                }`}
              >
                전체
              </Link>
              <span className="w-px h-4 bg-line mx-0.5" />
              {subcategories.map((sub) => {
                const isActive = isAllActive || activeSubs.includes(sub);
                const { label, emoji } = SUBCATEGORY_META[sub];
                return (
                  <Link
                    key={sub}
                    href={buildSubUrl(sub)}
                    className={`px-4 py-1.5 rounded-full text-label font-medium transition-colors ${
                      isActive
                        ? "bg-brand text-white"
                        : "bg-card border border-line text-muted hover:border-brand hover:text-brand"
                    }`}
                  >
                    {isActive ? "−" : "+"} {label} {emoji}
                  </Link>
                );
              })}
            </div>
            <Sort
              category={category}
              activeSubs={activeSubs}
              activeSort={activeSort}
              isSelectionMode={!isAllActive}
            />
          </div>

          {/* 기사 목록 */}
          {isEmptyState ? (
            <div className="flex flex-col items-center justify-center py-24 gap-3">
              <div className="flex flex-col items-center gap-3 bg-white/60 px-8 py-6 rounded-2xl">
                <span className="text-4xl">🔍</span>
                <p className="text-body font-medium text-text">원하는 세부 카테고리를 선택해주세요!</p>
              </div>
            </div>
          ) : articles.length > 0 ? (
            <>
              <div className="grid grid-cols-3 gap-x-5 gap-y-4">
                {articles.map((article) => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
              <Pagination
                currentPage={safePage}
                totalPages={totalPages}
                buildUrl={(p) => buildCategoryUrl(activeSubs.length > 0 ? activeSubs : null, activeSort, p)}
              />
            </>
          ) : (
            <div className="flex items-center justify-center py-24 text-muted text-body-sm">
              해당 카테고리의 기사가 없어요.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

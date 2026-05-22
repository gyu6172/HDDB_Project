import { notFound } from "next/navigation";
import Link from "next/link";
import ArticleCard from "@/components/common/ArticleCard";
import Sort from "@/components/common/Sort";
import BackButton from "@/components/common/BackButton";
import SearchButton from "@/components/common/SearchButton";
import { mockArticles } from "@/lib/mockData";
import { Category, Subcategory } from "@/types/article";

const CATEGORY_META: Record<Category, { label: string; emoji: string; tint: string; desc: string }> = {
  sky:  { label: "하늘", emoji: "☁️", tint: "bg-sky-from/10",  desc: "하늘에서 일어나는 자연의 이야기" },
  land: { label: "땅",   emoji: "🌳", tint: "bg-land-from/10", desc: "땅 위에서 펼쳐지는 자연의 이야기" },
  sea:  { label: "바다", emoji: "🌊", tint: "bg-sea-from/10",  desc: "깊고 넓은 바다의 자연 이야기" },
};

const SUBCATEGORY_META: Record<Subcategory, { label: string; emoji: string }> = {
  bird:            { label: "새",      emoji: "🪺" },
  space:           { label: "우주",    emoji: "🚀" },
  weather:         { label: "기상",    emoji: "🌤️" },
  disaster:        { label: "자연재해", emoji: "🌋" },
  animal:          { label: "동식물",  emoji: "🐾" },
  pollution:       { label: "환경오염", emoji: "♻️" },
  marine_life:     { label: "해양생물", emoji: "🐠" },
  deep_sea:        { label: "심해",    emoji: "🧜‍♀️" },
  ocean_pollution: { label: "해양오염", emoji: "☠️" },
};

const SUBCATEGORIES: Record<Category, Subcategory[]> = {
  sky:  ["bird", "space", "weather"],
  land: ["disaster", "animal", "pollution"],
  sea:  ["marine_life", "deep_sea", "ocean_pollution"],
};

const VALID_CATEGORIES: Category[] = ["sky", "land", "sea"];

export default async function CategoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ sub?: string; sort?: string }>;
}) {
  const { category: rawCategory } = await params;
  const { sub, sort } = await searchParams;

  if (!VALID_CATEGORIES.includes(rawCategory as Category)) notFound();

  const category = rawCategory as Category;
  const { label, emoji, tint, desc } = CATEGORY_META[category];
  const subcategories = SUBCATEGORIES[category];
  const activeSubs: Subcategory[] = sub
    ? (sub.split(",") as Subcategory[])
    : [];

  const activeSort = sort === "relevance" ? "relevance" : "latest";

  const articles = mockArticles
    .filter((a) => a.category === category && (activeSubs.length === 0 || activeSubs.includes(a.subcategory)))
    .sort((a, b) =>
      activeSort === "relevance"
        ? b.confidence - a.confidence
        : new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
    );

  function buildSubUrl(toggleSub: Subcategory) {
    const next = activeSubs.includes(toggleSub)
      ? activeSubs.filter((s) => s !== toggleSub)
      : [...activeSubs, toggleSub];
    const subParam = next.length > 0 ? `sub=${next.join(",")}` : "";
    const sortParam = activeSort === "relevance" ? "sort=relevance" : "";
    const query = [subParam, sortParam].filter(Boolean).join("&");
    return `/category/${category}${query ? `?${query}` : ""}`;
  }

  function buildSortUrl(newSort: string) {
    const subParam = activeSubs.length > 0 ? `sub=${activeSubs.join(",")}` : "";
    const sortParam = newSort === "relevance" ? "sort=relevance" : "";
    const query = [subParam, sortParam].filter(Boolean).join("&");
    return `/category/${category}${query ? `?${query}` : ""}`;
  }

  return (
    <div className="min-h-screen bg-bg">
      {/* 헤더 */}
      <div className={`${tint} border-b border-line`}>
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

      <div className="max-w-6xl mx-auto px-6 py-3">
        {/* 서브카테고리 필터 + 정렬 */}
        <div className="flex items-center justify-between gap-4 mt-1 mb-5">
          <div className="flex items-center gap-2 flex-wrap">
            {subcategories.map((sub) => {
              const isActive = activeSubs.includes(sub);
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
          />
        </div>

        {/* 기사 목록 */}
        {articles.length > 0 ? (
          <>
            <div className="grid grid-cols-3 gap-5">
              {articles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>

            {/* 더보기 버튼 — 백엔드 연결 후 동작 구현 */}
            <div className="flex justify-center mt-10">
              <button className="btn btn-ghost px-8" disabled>
                + 더보기
              </button>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center py-24 text-muted text-body-sm">
            해당 카테고리의 기사가 없어요.
          </div>
        )}
      </div>
    </div>
  );
}

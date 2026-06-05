import { notFound } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import BackButton from "@/components/common/BackButton";
import { fetchArticleById } from "@/lib/api";
import { MAIN_NEWS_DATA } from "@/lib/mainMockData";
import { mockArticleDetails } from "@/lib/mockData";
import { CATEGORY_STYLE, SUBCATEGORY_META, CATEGORY_META } from "@/constants/category";
import { ArticleDetail, Category, Subcategory } from "@/types/article";

const CATEGORY_BG: Record<Category, string> = {
  sky:  "/images/bg-sky-2.jpg",
  land: "/images/bg-land.jpg",
  sea:  "/images/bg-sea.jpg",
};

const DEFAULT_SUBCATEGORY: Record<Category, Subcategory> = {
  sky: "weather",
  land: "disaster",
  sea: "marine_life",
};

function getMainFallbackArticle(id: string): ArticleDetail | undefined {
  for (const [category, section] of Object.entries(MAIN_NEWS_DATA) as [Category, typeof MAIN_NEWS_DATA[Category]][]) {
    const item = section.items.find((news) => news.id === id);

    if (!item?.id) continue;

    return {
      id: item.id,
      title: item.title,
      oneLineSummary: "백엔드가 연결되면 실제 기사 요약과 본문을 보여줄 수 있어요.",
      source: item.source,
      sourceLang: "ko",
      publishedAt: new Date().toISOString(),
      thumbnailUrl: CATEGORY_BG[category],
      category,
      subcategory: DEFAULT_SUBCATEGORY[category],
      confidence: null,
      originalUrl: "#",
      content: "현재 백엔드 응답을 받을 수 없어 메인 화면의 임시 기사 정보로 표시하고 있어요.",
      paragraphSummaries: [
        {
          paragraphIndex: 0,
          originalText: "현재 백엔드 응답을 받을 수 없어 메인 화면의 임시 기사 정보로 표시하고 있어요.",
          summary: "백엔드 연결 후 실제 문단 요약으로 교체됩니다.",
        },
      ],
    };
  }

  return undefined;
}

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const article = await fetchArticleById(id).catch(
    () => mockArticleDetails.find((a) => a.id === id) ?? getMainFallbackArticle(id),
  );

  if (!article) notFound();

  const {
    title,
    oneLineSummary,
    source,
    sourceLang,
    publishedAt,
    thumbnailUrl,
    category,
    subcategory,
    originalUrl,
    content,
    paragraphSummaries,
  } = article;

  const { bg, text } = CATEGORY_STYLE[category];
  const { label, emoji } = SUBCATEGORY_META[subcategory];
  const { gradient } = CATEGORY_META[category];

  const formattedDate = new Date(publishedAt).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const paragraphs = content.split("\n\n").filter(Boolean);

  return (
    <div className="min-h-screen">

      {/* 배경 이미지 */}
      <div className="fixed inset-0 -z-10" aria-hidden="true">
        <Image src={CATEGORY_BG[category]} alt="" fill sizes="100vw" className="object-cover" />
      </div>

      {/* 헤더: 프로스티드 글라스 */}
      <div className={`backdrop-blur-[2px] bg-white/60 bg-gradient-to-br ${gradient} border-b border-black/10`}>
        <div className="max-w-5xl mx-auto px-6 pt-5 pb-6">
          <BackButton />
          <div className="mt-5 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span className={`text-caption font-semibold px-2.5 py-1 rounded-full ${bg} ${text}`}>
                {label} {emoji}
              </span>
              {sourceLang === "en" && (
                <span className="text-caption font-medium px-2 py-0.5 rounded-full bg-black/8 text-muted">
                  EN
                </span>
              )}
            </div>
            <h1 className="text-heading font-bold text-text leading-tight">{title}</h1>
            <div className="flex items-center gap-2 text-body-sm text-muted">
              <span className="font-medium">{source}</span>
              <span>·</span>
              <span>{formattedDate}</span>
              <span>·</span>
              <Link
                href={originalUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-brand hover:underline"
              >
                원문 보기 →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* 본문 */}
      <div className="max-w-5xl mx-auto px-6 py-6">
        <div className="bg-white rounded-2xl border border-line px-8 py-8">

          {/* 문단별 원문 + 요약 */}
          <div className="flex flex-col gap-7">

            {/* 이미지 + AI 요약 설명 */}
            <div className="flex gap-8">
              <div className="flex-[1.3] relative aspect-video rounded-xl overflow-hidden">
                <Image src={thumbnailUrl} alt={title} fill className="object-cover" />
              </div>
              <div className="flex-1 flex flex-col gap-2 justify-end">
                <p className="text-body-sm font-semibold text-brand">🐾 AI 요약 안내</p>
                <p className="text-body-sm text-muted leading-relaxed">
                  각 문단의 핵심 내용을 AI가 한 문장으로 요약했어요.<br />
                  원문에 마우스를 올리면 확인할 수 있어요.
                </p>
              </div>
            </div>
            {paragraphSummaries.map((ps) => (
              <div key={ps.paragraphIndex} className="group flex gap-8 items-start">
                {/* 원문 */}
                <p className="flex-[1.3] text-body-sm text-text leading-relaxed border-l-2 border-transparent pl-3 transition-all duration-200 group-hover:border-brand">
                  {paragraphs[ps.paragraphIndex] ?? ps.originalText}
                </p>
                {/* 요약 카드 */}
                <div className="flex-1 rounded-2xl bg-bg px-4 py-3 opacity-0 translate-x-2 transition-all duration-200 group-hover:opacity-100 group-hover:translate-x-0">
                  <p className="text-label text-text leading-relaxed">
                    <span className="mr-1.5">🐾</span>
                    {ps.summary}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* 한 줄 요약 */}
          <div className="mt-8 rounded-xl bg-brand/8 border border-brand/15 px-6 py-4 flex items-start gap-3">
            <span className="flex-shrink-0 text-body-sm font-bold text-brand">한 줄 요약</span>
            <p className="text-body-sm text-text leading-relaxed">{oneLineSummary}</p>
          </div>

        </div>
      </div>
    </div>
  );
}

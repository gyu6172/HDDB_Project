import { notFound } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import BackButton from "@/components/common/BackButton";
import { mockArticleDetails } from "@/lib/mockData";
import { CATEGORY_STYLE, SUBCATEGORY_META, CATEGORY_META } from "@/constants/category";
import { Category } from "@/types/article";

const CATEGORY_BG: Record<Category, string> = {
  sky:  "/images/bg-sky-2.jpg",
  land: "/images/bg-land.jpg",
  sea:  "/images/bg-sea.jpg",
};

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const article = mockArticleDetails.find((a) => a.id === id);

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

          {/* 본문 이미지 */}
          <div className="relative w-full aspect-[3/1] rounded-xl overflow-hidden mb-8">
            <Image src={thumbnailUrl} alt={title} fill className="object-cover" />
          </div>

          {/* 문단별 원문 + 요약 */}
          <div className="flex flex-col gap-7">
            {paragraphSummaries.map((ps) => (
              <div key={ps.paragraph_index} className="group flex gap-8 items-start">
                {/* 원문 */}
                <p className="flex-[1.3] text-body-sm text-text leading-relaxed border-l-2 border-transparent pl-3 transition-all duration-200 group-hover:border-brand">
                  {paragraphs[ps.paragraph_index] ?? ps.original_text}
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

import Link from "next/link";
import { CATEGORY_META, CATEGORY_STYLE, SUBCATEGORY_META, THUMBNAIL_BG } from "@/constants/category";
import { Article } from "@/types/article";

interface Props {
  article: Article;
}

function formatRelativeTime(publishedAt: string) {
  const diffMs = Date.now() - new Date(publishedAt).getTime();
  const diffMinutes = Math.max(0, Math.floor(diffMs / 60000));

  if (diffMinutes < 60) {
    return `${Math.max(1, diffMinutes)}분 전`;
  }

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours}시간 전`;
  }

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}일 전`;
}

export default function SearchResultItem({ article }: Props) {
  const { id, title, oneLineSummary, source, publishedAt, category, subcategory } = article;
  const categoryLabel = CATEGORY_META[category].label;
  const subcategoryLabel = SUBCATEGORY_META[subcategory].label;
  const { bg, text } = CATEGORY_STYLE[category];

  return (
    <Link
      href={`/articles/${id}`}
      className="grid min-h-[190px] overflow-hidden rounded-2xl border border-line bg-card transition hover:-translate-y-0.5 hover:shadow-sm md:grid-cols-[220px_1fr]"
    >
      <div className={`min-h-[160px] bg-gradient-to-br ${THUMBNAIL_BG[category]}`} aria-hidden="true" />

      <article className="flex flex-col px-6 py-5 md:px-8">
        <span className={`self-start rounded-lg px-3 py-1 text-label font-bold ${bg} ${text}`}>
          {categoryLabel} · {subcategoryLabel}
        </span>

        <h2 className="mt-5 text-[22px] font-bold leading-snug text-text">
          {title}
        </h2>

        <p className="mt-3 line-clamp-2 text-body text-muted">
          {oneLineSummary}
        </p>

        <div className="mt-auto pt-6 text-label font-semibold text-muted">
          {source} · {formatRelativeTime(publishedAt)}
        </div>
      </article>
    </Link>
  );
}

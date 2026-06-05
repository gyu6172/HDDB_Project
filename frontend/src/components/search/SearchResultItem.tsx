import Link from "next/link";
import Image from "next/image";
import { CATEGORY_META, CATEGORY_STYLE, SUBCATEGORY_META, THUMBNAIL_BG } from "@/constants/category";
import { SearchResultArticle } from "@/lib/search";

interface Props {
  article: SearchResultArticle;
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
  const { id, title, oneLineSummary, source, publishedAt, thumbnailUrl, category, subcategory } = article;
  const categoryLabel = CATEGORY_META[category].label;
  const subcategoryLabel = SUBCATEGORY_META[subcategory].label;
  const { bg, text } = CATEGORY_STYLE[category];

  return (
    <Link
      href={`/articles/${id}`}
      className="grid min-h-[190px] overflow-hidden rounded-2xl border border-line bg-card transition hover:-translate-y-0.5 hover:shadow-sm md:grid-cols-[220px_1fr]"
    >
      <div className={`relative min-h-[160px] bg-gradient-to-br ${THUMBNAIL_BG[category]}`}>
        {thumbnailUrl && (
          <Image
            src={thumbnailUrl}
            alt={title}
            fill
            sizes="(max-width: 768px) 100vw, 220px"
            className="object-cover"
          />
        )}
      </div>

      <article className="flex flex-col px-6 py-5 md:px-8">
        <span className={`self-start rounded-lg px-2.5 py-1 text-caption font-semibold ${bg} ${text}`}>
          {categoryLabel} · {subcategoryLabel}
        </span>

        <h2 className="mt-4 text-body font-bold leading-snug text-text">
          {title}
        </h2>

        <p className="mt-2 line-clamp-2 text-body-sm text-muted">
          {oneLineSummary}
        </p>

        <div className="mt-auto pt-5 text-caption font-semibold text-muted">
          {source} · {formatRelativeTime(publishedAt)}
        </div>
      </article>
    </Link>
  );
}

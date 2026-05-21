import Link from "next/link";
import Image from "next/image";
import { Article, Category } from "@/types/article";

const CATEGORY_META: Record<Category, { label: string; emoji: string; bg: string; text: string }> = {
  sky:  { label: "하늘", emoji: "☁️", bg: "bg-sky-from/30",  text: "text-sky-text" },
  land: { label: "땅",   emoji: "🌿", bg: "bg-land-from/30", text: "text-land-text" },
  sea:  { label: "바다", emoji: "🌊", bg: "bg-sea-from/30",  text: "text-sea-text" },
};

const THUMBNAIL_BG: Record<Category, string> = {
  sky:  "from-sky-from to-sky-to",
  land: "from-land-from to-land-to",
  sea:  "from-sea-from to-sea-to",
};

interface Props {
  article: Article;
}

export default function ArticleCard({ article }: Props) {
  const { id, thumbnailUrl, title, oneLineSummary, source, publishedAt, category } = article;
  const { label, emoji, bg, text } = CATEGORY_META[category];

  const formattedDate = new Date(publishedAt).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <Link href={`/articles/${id}`} className="flex flex-col card card-interactive overflow-hidden">
      {/* 썸네일 */}
      <div className={`relative w-full aspect-[2/1] bg-gradient-to-br ${THUMBNAIL_BG[category]}`}>
        <Image src={thumbnailUrl} alt={title} fill className="object-cover" />
      </div>

      {/* 본문 */}
      <div className="p-4 flex flex-col gap-2">
        <span className={`self-start text-caption font-semibold px-2.5 py-1 rounded-full ${bg} ${text}`}>
          {label} {emoji}
        </span>
        <h3 className="text-body-sm font-bold text-text leading-snug line-clamp-2">
          {title}
        </h3>
        <p className="text-label text-muted leading-relaxed line-clamp-2">
          {oneLineSummary}
        </p>
        <div className="flex items-center gap-1.5 text-caption text-muted/70 mt-auto">
          <span className="font-medium">{source}</span>
          <span>·</span>
          <span>{formattedDate}</span>
        </div>
      </div>
    </Link>
  );
}

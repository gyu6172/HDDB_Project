import Link from "next/link";
import Image from "next/image";
import { Article } from "@/types/article";
import { CATEGORY_STYLE, SUBCATEGORY_META, THUMBNAIL_BG } from "@/constants/category";

interface Props {
  article: Article;
}

export default function ArticleCard({ article }: Props) {
  const { id, thumbnailUrl, title, oneLineSummary, source, publishedAt, category, subcategory } = article;
  const { bg, text } = CATEGORY_STYLE[category];
  const { label, emoji } = SUBCATEGORY_META[subcategory];

  const formattedDate = new Date(publishedAt).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <Link href={`/articles/${id}`} className="flex flex-col card card-interactive overflow-hidden">
      {/* 썸네일 */}
      <div className={`relative w-full aspect-[5/2] bg-gradient-to-br ${THUMBNAIL_BG[category]}`}>
        <Image src={thumbnailUrl} alt={title} fill className="object-cover" />
      </div>

      {/* 본문 */}
      <div className="px-4 pt-3 pb-4 flex flex-col gap-2">
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

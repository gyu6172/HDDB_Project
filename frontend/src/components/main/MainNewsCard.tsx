import type { ReactNode } from "react";
import NewsItem from "./NewsItem";

export type MainNews = {
  title: string;
  source: string;
  time: string;
};

type MainNewsCardVariant = "vertical" | "horizontal";

type MainNewsCardProps = {
  icon: ReactNode;
  title: string;
  titleClassName?: string;
  items: MainNews[];
  variant?: MainNewsCardVariant;
  moreLabel?: string;
  onMoreClick?: () => void;
};

export default function MainNewsCard({
  icon,
  title,
  titleClassName = "text-blue-700",
  items,
  variant = "vertical",
  moreLabel = "더보기",
  onMoreClick,
}: MainNewsCardProps) {
  return (
    <section className="rounded-3xl bg-card/90 px-8 py-7 shadow-sm">
      <div className="mb-8 flex items-center justify-between gap-6">
        <h2
          className={`flex items-center gap-2 text-2xl font-bold ${titleClassName}`}
        >
          {icon}
          {title}
        </h2>

        <button
          type="button"
          onClick={onMoreClick}
          className="text-lg font-semibold text-zinc-500 hover:text-zinc-800"
        >
          {moreLabel} ›
        </button>
      </div>

      <div
        className={
          variant === "horizontal"
            ? "grid gap-8 md:grid-cols-3"
            : "space-y-7"
        }
      >
        {items.map((item) => (
          <NewsItem key={`${item.source}-${item.title}`} {...item} />
        ))}
      </div>
    </section>
  );
}

import type { ReactNode } from "react";
import NewsItem from "./NewsItem";

export type MainNews = {
  title: string;
  source: string;
  time: string;
};

type MainNewsCardProps = {
  icon: ReactNode;
  title: string;
  items: MainNews[];
};

export default function MainNewsCard({
  icon,
  title,
  items,
}: MainNewsCardProps) {
  return (
    <section className="rounded-3xl bg-card/90 px-8 py-7 shadow-sm">
      <div className="mb-8 flex items-center justify-between gap-6">
        <h2 className="flex items-center gap-2 text-2xl font-bold text-blue-700">
          {icon}
          {title}
        </h2>

        <button type="button" className="text-lg font-semibold text-zinc-500">
          더보기 ›
        </button>
      </div>

      <div className="space-y-7">
        {items.map((item) => (
          <NewsItem key={`${item.source}-${item.title}`} {...item} />
        ))}
      </div>
    </section>
  );
}

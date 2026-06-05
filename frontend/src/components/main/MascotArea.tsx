"use client";

import { fetchRandomArticles } from "@/lib/api";
import type { Article } from "@/types/article";
import Link from "next/link";
import { useEffect, useState } from "react";

const FALLBACK_SUMMARY = "궁금한 뉴스가 있나요?";

type MascotArticle = Pick<Article, "id" | "oneLineSummary">;

export default function MascotArea() {
  const [articles, setArticles] = useState<MascotArticle[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    let isMounted = true;

    async function loadSummaries() {
      try {
        const randomArticles = await fetchRandomArticles(10);
        const nextArticles = randomArticles.filter((article) =>
          Boolean(article.oneLineSummary?.trim()),
        );

        if (isMounted && nextArticles.length > 0) {
          setArticles(nextArticles);
          setActiveIndex(0);
        }
      } catch (error) {
        console.warn("Failed to load mascot summaries", error);
      }
    }

    loadSummaries();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (articles.length <= 1) return;

    const timerId = window.setInterval(() => {
      setActiveIndex((index) => (index + 1) % articles.length);
    }, 5000);

    return () => window.clearInterval(timerId);
  }, [articles.length]);

  const activeArticle = articles[activeIndex];
  const summary = activeArticle?.oneLineSummary?.trim() || FALLBACK_SUMMARY;
  const bubbleClassName =
    "max-w-[260px] rounded-3xl bg-card px-7 py-4 text-center text-lg font-semibold leading-tight text-text shadow-sm transition-colors hover:bg-white";

  return (
    <div className="flex min-h-[360px] flex-col items-center justify-center gap-14">
      {activeArticle ? (
        <Link href={`/articles/${activeArticle.id}`} className={bubbleClassName}>
          {summary}
        </Link>
      ) : (
        <div className={bubbleClassName}>{summary}</div>
      )}

      <div
        aria-hidden="true"
        className="flex size-32 items-center justify-center text-7xl"
      >
        🦦
      </div>
    </div>
  );
}

"use client";

import { fetchRandomArticles } from "@/lib/api";
import { useEffect, useState } from "react";

const FALLBACK_SUMMARY = "궁금한 뉴스가 있나요?";

export default function MascotArea() {
  const [summaries, setSummaries] = useState<string[]>([FALLBACK_SUMMARY]);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    let isMounted = true;

    async function loadSummaries() {
      try {
        const articles = await fetchRandomArticles(10);
        const nextSummaries = articles
          .map((article) => article.oneLineSummary?.trim())
          .filter((summary): summary is string => Boolean(summary));

        if (isMounted && nextSummaries.length > 0) {
          setSummaries(nextSummaries);
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
    if (summaries.length <= 1) return;

    const timerId = window.setInterval(() => {
      setActiveIndex((index) => (index + 1) % summaries.length);
    }, 5000);

    return () => window.clearInterval(timerId);
  }, [summaries.length]);

  return (
    <div className="flex min-h-[360px] flex-col items-center justify-center gap-14">
      <div className="max-w-[260px] rounded-3xl bg-card px-7 py-4 text-center text-lg font-semibold leading-tight text-text shadow-sm">
        {summaries[activeIndex]}
      </div>

      <div
        aria-hidden="true"
        className="flex size-32 items-center justify-center text-7xl"
      >
        🦦
      </div>
    </div>
  );
}

"use client";

import MainNewsCard from "@/components/main/MainNewsCard";
import type { MainNews } from "@/components/main/MainNewsCard";
import MascotArea from "@/components/main/MascotArea";
import SearchDock from "@/components/main/SearchDock";
import { CloudIcon, MountainIcon, WaveIcon } from "@/components/main/MainIcons";
import { fetchArticlesByCategory } from "@/lib/api";
import type { Article, Category } from "@/types/article";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const SECTION_META = {
  sky: {
    icon: <CloudIcon />,
    titleClassName: "text-sky-icon",
    variant: "horizontal" as const,
  },
  land: {
    icon: <MountainIcon />,
    titleClassName: "text-land-icon",
    variant: "vertical" as const,
  },
  sea: {
    icon: <WaveIcon />,
    titleClassName: "text-sea-icon",
    variant: "vertical" as const,
  },
};

type MainNewsCategory = {
  title: string;
  items: MainNews[];
};

type MainNewsData = Record<Category, MainNewsCategory>;

const CATEGORY_TITLES: Record<Category, string> = {
  sky: "하늘",
  land: "땅",
  sea: "바다",
};

const CATEGORIES: Category[] = ["sky", "land", "sea"];

const EMPTY_MAIN_NEWS_DATA: MainNewsData = {
  sky: {
    title: CATEGORY_TITLES.sky,
    items: [],
  },
  land: {
    title: CATEGORY_TITLES.land,
    items: [],
  },
  sea: {
    title: CATEGORY_TITLES.sea,
    items: [],
  },
};

function formatRelativeTime(isoDate: string) {
  const publishedTime = new Date(isoDate).getTime();

  if (Number.isNaN(publishedTime)) return "방금 전";

  const diffMs = Date.now() - publishedTime;
  const diffMinutes = Math.max(0, Math.floor(diffMs / 60000));

  if (diffMinutes < 1) return "방금 전";
  if (diffMinutes < 60) return `${diffMinutes}분 전`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}시간 전`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}일 전`;

  return new Intl.DateTimeFormat("ko-KR", {
    month: "long",
    day: "numeric",
  }).format(new Date(isoDate));
}

function toMainNews(article: Article): MainNews {
  return {
    id: article.id,
    title: article.title,
    source: article.source,
    time: formatRelativeTime(article.publishedAt),
  };
}

function mergeMainData(
  currentData: MainNewsData,
  category: Category,
  articles: Article[],
): MainNewsData {
  return {
    ...currentData,
    [category]: {
      title: CATEGORY_TITLES[category],
      items: articles.map(toMainNews),
    },
  };
}

export default function MainView() {
  const router = useRouter();
  const [newsData, setNewsData] = useState<MainNewsData>(EMPTY_MAIN_NEWS_DATA);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadMainNews() {
      try {
        const responses = await Promise.allSettled(
          CATEGORIES.map((category) =>
            fetchArticlesByCategory(category, { limit: 3, sort: "recent" }),
          ),
        );

        if (!isMounted) return;

        const nextData = CATEGORIES.reduce<MainNewsData>(
          (data, category, index) => {
            const response = responses[index];

            if (response.status !== "fulfilled") {
              console.warn(`Failed to load ${category} news`, response.reason);
              return data;
            }

            return mergeMainData(data, category, response.value.items);
          },
          EMPTY_MAIN_NEWS_DATA,
        );

        setNewsData(nextData);
      } catch (error) {
        console.warn("Failed to load main news", error);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadMainNews();

    return () => {
      isMounted = false;
    };
  }, []);

  const { sky, land, sea } = newsData;

  function moveToCategory(category: Category) {
    router.push(`/category/${category}?sub=all`);
  }

  return (
    <main className="min-h-screen bg-bg px-5 py-5">
      <div className="mx-auto flex min-h-[calc(100vh-40px)] max-w-[1840px] flex-col rounded-[28px] bg-[linear-gradient(180deg,#add9f3_0%,#b8d0af_50%,#6fa5cf_100%)] px-9 py-8">
        <section className="grid flex-1 grid-rows-[auto_auto_auto_1fr] gap-8">
          <div className="flex justify-center pt-1">
            <SearchDock />
          </div>

          <MainNewsCard
            icon={SECTION_META.sky.icon}
            title={sky.title}
            titleClassName={SECTION_META.sky.titleClassName}
            items={sky.items}
            variant={SECTION_META.sky.variant}
            moreLabel={isLoading ? "불러오는 중" : "더보기"}
            onMoreClick={() => moveToCategory("sky")}
          />

          <div className="grid items-start gap-9 lg:grid-cols-[1fr_300px_1fr]">
            <MainNewsCard
              icon={SECTION_META.land.icon}
              title={land.title}
              titleClassName={SECTION_META.land.titleClassName}
              items={land.items}
              variant={SECTION_META.land.variant}
              moreLabel={isLoading ? "불러오는 중" : "더보기"}
              onMoreClick={() => moveToCategory("land")}
            />

            <MascotArea />

            <MainNewsCard
              icon={SECTION_META.sea.icon}
              title={sea.title}
              titleClassName={SECTION_META.sea.titleClassName}
              items={sea.items}
              variant={SECTION_META.sea.variant}
              moreLabel={isLoading ? "불러오는 중" : "더보기"}
              onMoreClick={() => moveToCategory("sea")}
            />
          </div>
        </section>
      </div>
    </main>
  );
}

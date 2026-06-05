import MainNewsCard from "@/components/main/MainNewsCard";
import MascotArea from "@/components/main/MascotArea";
import SearchDock from "@/components/main/SearchDock";
import { CloudIcon, MountainIcon, WaveIcon } from "@/components/main/MainIcons";
import { MAIN_NEWS_DATA } from "@/lib/mainMockData";

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

export default function MainView() {
  const { sky, land, sea } = MAIN_NEWS_DATA;

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
          />

          <div className="grid items-start gap-9 lg:grid-cols-[1fr_300px_1fr]">
            <MainNewsCard
              icon={SECTION_META.land.icon}
              title={land.title}
              titleClassName={SECTION_META.land.titleClassName}
              items={land.items}
              variant={SECTION_META.land.variant}
            />

            <MascotArea />

            <MainNewsCard
              icon={SECTION_META.sea.icon}
              title={sea.title}
              titleClassName={SECTION_META.sea.titleClassName}
              items={sea.items}
              variant={SECTION_META.sea.variant}
            />
          </div>
        </section>
      </div>
    </main>
  );
}

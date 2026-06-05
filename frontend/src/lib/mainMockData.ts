import type { MainNews } from "@/components/main/MainNewsCard";

type MainNewsCategory = {
  title: string;
  items: MainNews[];
};

export const MAIN_NEWS_DATA: Record<"sky" | "land" | "sea", MainNewsCategory> =
  {
    sky: {
      title: "하늘",
      items: [
        {
          id: "main-sky-1",
          title: "NASA, 화성에서 새로운 물의 흔적 발견",
          source: "NASA",
          time: "2시간 전",
        },
        {
          id: "main-sky-2",
          title: "북극 대기오염 물질 역대 최고 수준",
          source: "환경뉴스",
          time: "4시간 전",
        },
        {
          id: "main-sky-3",
          title: "철새 1,000km 이동 경로 추적 성공",
          source: "조류연구소",
          time: "6시간 전",
        },
      ],
    },
    land: {
      title: "땅",
      items: [
        {
          id: "main-land-1",
          title: "일본 남부 규모 6.1 지진 발생",
          source: "연합뉴스",
          time: "1시간 전",
        },
        {
          id: "main-land-2",
          title: "인도네시아 화산 폭발 경보",
          source: "KBS",
          time: "3시간 전",
        },
        {
          id: "main-land-3",
          title: "야생 코끼리 무리, 마을 접근",
          source: "BBC",
          time: "5시간 전",
        },
      ],
    },
    sea: {
      title: "바다",
      items: [
        {
          id: "main-sea-1",
          title: "심해 3,000m에서 신종 생물 발견",
          source: "해양연구소",
          time: "2시간 전",
        },
        {
          id: "main-sea-2",
          title: "태평양 플라스틱 쓰레기 증가",
          source: "해양환경단체",
          time: "4시간 전",
        },
        {
          id: "main-sea-3",
          title: "산호초 백화 현상 심화",
          source: "YTN",
          time: "6시간 전",
        },
      ],
    },
  };

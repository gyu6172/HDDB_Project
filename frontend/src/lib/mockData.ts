import { Article } from "@/types/article";

export const mockArticles: Article[] = [
  {
    id: "1",
    title: "철새 이동 경로에서 포착된 희귀종 발견",
    content:
      "국립생태원 연구팀이 금강 하구 철새 도래지에서 국내 미기록 희귀종 새를 발견했다고 밝혔다. 이번 발견은 기후변화로 인한 철새 이동 경로 변화를 보여주는 중요한 사례로 평가된다.",
    source: "연합뉴스",
    publishedAt: "2026-05-18T09:00:00Z",
    category: "sky",
    subcategory: "bird",
    oneLineSummary: "금강 하구에서 국내 미기록 희귀 철새가 발견됐어요.",
    cardSummary:
      "기후변화로 철새 이동 경로가 바뀌면서 국내에서 한 번도 기록된 적 없는 희귀 조류가 포착됐어요. 국립생태원은 지속적인 모니터링이 필요하다고 밝혔답니다.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "국립생태원 연구팀이 금강 하구 철새 도래지에서 국내 미기록 희귀종 새를 발견했다.",
        summary: "금강 하구에서 처음 보는 새가 발견됐어요.",
      },
    ],
    thumbnail: "/images/bird-rare.jpg",
  },
  {
    id: "2",
    title: "제임스 웹 망원경, 새로운 외계행성 대기 성분 확인",
    content:
      "NASA의 제임스 웹 우주망원경이 지구로부터 약 120광년 떨어진 외계행성 K2-18b의 대기에서 탄소 기반 분자를 검출하는 데 성공했다. 과학자들은 이 발견이 생명체 존재 가능성을 시사할 수 있다고 밝혔다.",
    source: "사이언스타임즈",
    publishedAt: "2026-05-17T14:30:00Z",
    category: "sky",
    subcategory: "space",
    oneLineSummary: "웹 망원경이 외계행성에서 생명 가능성 분자를 발견했어요.",
    cardSummary:
      "제임스 웹 망원경이 120광년 거리 외계행성 대기에서 탄소 기반 분자를 확인했어요. 생명체 존재 가능성의 단서가 될 수 있어 전 세계 과학계가 주목하고 있답니다.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "NASA의 제임스 웹 우주망원경이 외계행성 K2-18b의 대기에서 탄소 기반 분자를 검출했다.",
        summary: "웹 망원경이 외계행성 대기에서 특별한 분자를 찾았어요.",
      },
    ],
    thumbnail: "/images/space-webb.jpg",
  },
  {
    id: "3",
    title: "한반도 봄철 황사, 올해 역대급 농도 기록",
    content:
      "기상청은 이번 주 한반도에 유입된 황사의 미세먼지 농도가 관측 이래 최고 수준을 기록했다고 발표했다. 중국 내몽골 지역 사막화 가속이 주요 원인으로 분석된다.",
    source: "그린포스트코리아",
    publishedAt: "2026-05-16T08:00:00Z",
    category: "sky",
    subcategory: "weather",
    oneLineSummary: "올봄 황사 농도가 역대 최고 수준을 기록했어요.",
    cardSummary:
      "이번 봄 한반도를 덮친 황사가 관측 사상 최고 농도를 기록했어요. 중국 내몽골 사막화가 빨라지면서 앞으로도 황사 피해가 심해질 수 있다고 해요.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "기상청은 이번 황사의 미세먼지 농도가 관측 이래 최고 수준이라고 발표했다.",
        summary: "이번 황사가 역대 가장 나쁜 수준이래요.",
      },
    ],
    thumbnail: "/images/weather-dust.jpg",
  },
  {
    id: "4",
    title: "강원도 산불, 이틀째 확산…주민 대피령 발령",
    content:
      "강원도 영동 지역에서 발생한 산불이 이틀째 확산되면서 인근 마을 주민들에게 대피령이 발령됐다. 강풍과 건조한 날씨가 진화를 어렵게 하고 있으며 소방 당국은 헬기 20대를 동원해 대응 중이다.",
    source: "한겨레",
    publishedAt: "2026-05-15T11:00:00Z",
    category: "land",
    subcategory: "disaster",
    oneLineSummary: "강원 산불이 이틀째 번지며 주민 대피가 시작됐어요.",
    cardSummary:
      "강원도 영동 지역 산불이 강풍과 건조한 날씨 탓에 이틀째 꺼지지 않고 있어요. 소방 헬기 20대가 투입됐지만 진화가 쉽지 않아 주민들이 긴급 대피했답니다.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "강원도 영동 지역 산불이 이틀째 확산되면서 주민 대피령이 발령됐다.",
        summary: "강원 산불이 계속 번지며 주민들이 피난했어요.",
      },
    ],
    thumbnail: "/images/land-wildfire.jpg",
  },
  {
    id: "5",
    title: "멸종위기 수달, 한강 도심 구간서 번식 확인",
    content:
      "환경부는 멸종위기 1급 수달이 한강 도심 구간에서 번식에 성공한 것을 공식 확인했다고 밝혔다. 수달 개체 수 회복은 한강 수질 개선과 생태계 복원의 성과로 평가된다.",
    source: "연합뉴스",
    publishedAt: "2026-05-14T10:00:00Z",
    category: "land",
    subcategory: "animal",
    oneLineSummary: "멸종위기 수달이 한강 도심에서 새끼를 낳았어요.",
    cardSummary:
      "한강 도심 구간에서 멸종위기 1급 수달이 번식한 사실이 공식 확인됐어요. 한강 수질이 많이 좋아진 덕분이라고 하니 정말 반가운 소식이에요.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "환경부는 멸종위기 1급 수달이 한강 도심 구간에서 번식한 것을 확인했다.",
        summary: "수달이 한강 도심에서 번식에 성공했어요.",
      },
    ],
    thumbnail: "/images/land-otter.jpg",
  },
  {
    id: "6",
    title: "낙동강 수계 퇴적물서 중금속 오염 심각",
    content:
      "환경부 산하 국립환경과학원이 낙동강 수계 퇴적물을 조사한 결과 납·카드뮴 등 중금속 농도가 기준치를 초과한 구간이 다수 발견됐다. 인근 공단 폐수 유입이 주요 원인으로 지목됐다.",
    source: "그린포스트코리아",
    publishedAt: "2026-05-13T09:30:00Z",
    category: "land",
    subcategory: "pollution",
    oneLineSummary: "낙동강 퇴적물에서 기준치 초과 중금속이 발견됐어요.",
    cardSummary:
      "낙동강 곳곳의 퇴적물에서 납·카드뮴 등 중금속이 기준치를 넘겼어요. 공단 폐수가 강으로 흘러들어 생태계와 수질에 심각한 영향을 주고 있답니다.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "국립환경과학원 조사 결과 낙동강 수계 퇴적물에서 중금속 농도가 기준치를 초과했다.",
        summary: "낙동강 퇴적물 중금속 오염이 심각해요.",
      },
    ],
    thumbnail: "/images/land-pollution.jpg",
  },
  {
    id: "7",
    title: "남해 참돔 어획량 30% 감소…수온 상승이 원인",
    content:
      "국립수산과학원은 올해 남해 참돔 어획량이 전년 대비 30% 감소했다고 밝혔다. 수온 상승으로 참돔 서식지가 북상하면서 전통 어장에서의 어획이 줄어든 것으로 분석된다.",
    source: "연합뉴스",
    publishedAt: "2026-05-12T13:00:00Z",
    category: "sea",
    subcategory: "marine_life",
    oneLineSummary: "남해 참돔이 수온 상승으로 30% 줄었어요.",
    cardSummary:
      "남해 참돔 어획량이 올해 크게 줄었어요. 바다 온도가 오르면서 참돔 서식지가 북쪽으로 올라가 전통 어장에서 잡히는 양이 감소했답니다.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "국립수산과학원은 올해 남해 참돔 어획량이 전년 대비 30% 감소했다고 밝혔다.",
        summary: "남해 참돔 어획량이 30% 줄었어요.",
      },
    ],
    thumbnail: "/images/sea-snapper.jpg",
  },
  {
    id: "8",
    title: "동해 수심 2000m서 신종 해양 생물 발견",
    content:
      "한국해양과학기술원(KIOST) 심해 탐사팀이 동해 수심 2000m 지점에서 기존에 보고된 적 없는 신종 갑각류를 발견했다. 이 생물은 극단적인 수압과 어둠 속에서 생존하는 독특한 적응 형태를 보인다.",
    source: "사이언스타임즈",
    publishedAt: "2026-05-11T15:00:00Z",
    category: "sea",
    subcategory: "deep_sea",
    oneLineSummary: "동해 심해 2000m에서 신종 갑각류가 발견됐어요.",
    cardSummary:
      "KIOST 탐사팀이 동해 깊은 곳에서 새로운 생물을 찾아냈어요. 엄청난 수압과 칠흑 같은 어둠 속에서도 살아남은 신기한 갑각류랍니다.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "KIOST 심해 탐사팀이 동해 수심 2000m에서 신종 갑각류를 발견했다.",
        summary: "동해 심해에서 처음 보는 갑각류가 발견됐어요.",
      },
    ],
    thumbnail: "/images/sea-deepsea.jpg",
  },
  {
    id: "9",
    title: "태평양 플라스틱 쓰레기 섬, 한반도 면적의 6배",
    content:
      "환경단체 오션클린업(The Ocean Cleanup)이 발표한 최신 보고서에 따르면 태평양 대형 쓰레기 지대(GPGP)의 면적이 한반도의 약 6배 규모로 확대됐다. 미세 플라스틱 농도도 10년 전 대비 3배 증가한 것으로 나타났다.",
    source: "BBC Earth",
    publishedAt: "2026-05-10T07:00:00Z",
    category: "sea",
    subcategory: "ocean_pollution",
    oneLineSummary: "태평양 쓰레기 섬이 한반도의 6배 크기로 커졌어요.",
    cardSummary:
      "태평양 한가운데 떠 있는 플라스틱 쓰레기 더미가 한반도의 6배 크기로 커졌어요. 미세플라스틱도 10년 새 3배로 늘어 해양 생태계를 심각하게 위협하고 있답니다.",
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text:
          "태평양 대형 쓰레기 지대가 한반도의 약 6배 규모로 확대됐다.",
        summary: "태평양 플라스틱 쓰레기 섬이 한반도의 6배가 됐어요.",
      },
    ],
    thumbnail: "/images/sea-plastic.jpg",
  },
];

import { Article, ArticleDetail } from "@/types/article";

export const mockArticles: Article[] = [
  {
    id: "1",
    title: "철새 이동 경로에서 포착된 희귀종 발견",
    oneLineSummary: "금강 하구에서 국내 미기록 희귀 철새가 발견됐어요.",
    source: "연합뉴스",
    sourceLang: "ko",
    publishedAt: "2026-05-18T09:00:00Z",
    thumbnailUrl: "/images/bird-rare.jpg",
    category: "sky",
    subcategory: "bird",
    confidence: 0.95,
  },
  {
    id: "2",
    title: "제임스 웹 망원경, 새로운 외계행성 대기 성분 확인",
    oneLineSummary: "웹 망원경이 외계행성에서 생명 가능성 분자를 발견했어요.",
    source: "사이언스타임즈",
    sourceLang: "ko",
    publishedAt: "2026-05-17T14:30:00Z",
    thumbnailUrl: "/images/space-webb.jpg",
    category: "sky",
    subcategory: "space",
    confidence: 0.92,
  },
  {
    id: "3",
    title: "한반도 봄철 황사, 올해 역대급 농도 기록",
    oneLineSummary: "올봄 황사 농도가 역대 최고 수준을 기록했어요.",
    source: "그린포스트코리아",
    sourceLang: "ko",
    publishedAt: "2026-05-16T08:00:00Z",
    thumbnailUrl: "/images/weather-dust.jpg",
    category: "sky",
    subcategory: "weather",
    confidence: 0.97,
  },
  {
    id: "10",
    title: "수도권 초미세먼지 주의보…노약자 외출 자제 권고",
    oneLineSummary: "수도권에 초미세먼지 주의보가 발령되며 외출 자제가 권고됐어요.",
    source: "환경부",
    sourceLang: "ko",
    publishedAt: "2026-05-19T07:00:00Z",
    thumbnailUrl: "/images/sky-airpollution.jpg",
    category: "sky",
    subcategory: "air_pollution",
    confidence: 0.94,
  },
  {
    id: "4",
    title: "강원도 산불, 이틀째 확산…주민 대피령 발령",
    oneLineSummary: "강원 산불이 이틀째 번지며 주민 대피가 시작됐어요.",
    source: "한겨레",
    sourceLang: "ko",
    publishedAt: "2026-05-15T11:00:00Z",
    thumbnailUrl: "/images/land-wildfire.jpg",
    category: "land",
    subcategory: "disaster",
    confidence: 0.98,
  },
  {
    id: "5",
    title: "멸종위기 수달, 한강 도심 구간서 번식 확인",
    oneLineSummary: "멸종위기 수달이 한강 도심에서 새끼를 낳았어요.",
    source: "연합뉴스",
    sourceLang: "ko",
    publishedAt: "2026-05-14T10:00:00Z",
    thumbnailUrl: "/images/land-otter.jpg",
    category: "land",
    subcategory: "animal",
    confidence: 0.96,
  },
  {
    id: "6",
    title: "낙동강 수계 퇴적물서 중금속 오염 심각",
    oneLineSummary: "낙동강 퇴적물에서 기준치 초과 중금속이 발견됐어요.",
    source: "그린포스트코리아",
    sourceLang: "ko",
    publishedAt: "2026-05-13T09:30:00Z",
    thumbnailUrl: "/images/land-pollution.jpg",
    category: "land",
    subcategory: "ground_pollution",
    confidence: 0.93,
  },
  {
    id: "11",
    title: "기후변화로 한반도 매미 개체수 급증…도심 소음 피해 확산",
    oneLineSummary: "기후변화로 매미 개체수가 늘며 도심 소음 민원이 급증하고 있어요.",
    source: "한겨레",
    sourceLang: "ko",
    publishedAt: "2026-05-17T10:00:00Z",
    thumbnailUrl: "/images/land-insect.jpg",
    category: "land",
    subcategory: "insect",
    confidence: 0.88,
  },
  {
    id: "7",
    title: "남해 참돔 어획량 30% 감소…수온 상승이 원인",
    oneLineSummary: "남해 참돔이 수온 상승으로 30% 줄었어요.",
    source: "연합뉴스",
    sourceLang: "ko",
    publishedAt: "2026-05-12T13:00:00Z",
    thumbnailUrl: "/images/sea-snapper.jpg",
    category: "sea",
    subcategory: "marine_life",
    confidence: 0.91,
  },
  {
    id: "8",
    title: "동해 수심 2000m서 신종 해양 생물 발견",
    oneLineSummary: "동해 심해 2000m에서 신종 갑각류가 발견됐어요.",
    source: "사이언스타임즈",
    sourceLang: "ko",
    publishedAt: "2026-05-11T15:00:00Z",
    thumbnailUrl: "/images/sea-deepsea.jpg",
    category: "sea",
    subcategory: "deep_sea",
    confidence: 0.94,
  },
  {
    id: "9",
    title: "태평양 플라스틱 쓰레기 섬, 한반도 면적의 6배",
    oneLineSummary: "태평양 쓰레기 섬이 한반도의 6배 크기로 커졌어요.",
    source: "BBC Earth",
    sourceLang: "en",
    publishedAt: "2026-05-10T07:00:00Z",
    thumbnailUrl: "/images/sea-plastic.jpg",
    category: "sea",
    subcategory: "ocean_pollution",
    confidence: 0.89,
  },
];

export const mockArticleDetails: ArticleDetail[] = [
  {
    id: "1",
    title: "철새 이동 경로에서 포착된 희귀종 발견",
    oneLineSummary: "금강 하구에서 국내 미기록 희귀 철새가 발견됐어요.",
    source: "연합뉴스",
    sourceLang: "ko",
    publishedAt: "2026-05-18T09:00:00Z",
    thumbnailUrl: "/images/bird-rare.jpg",
    category: "sky",
    subcategory: "bird",
    confidence: 0.95,
    originalUrl: "https://www.yna.co.kr/view/example-1",
    content: `금강 하구 철새 도래지에서 국내에서 한 번도 기록된 적 없는 희귀 철새가 발견돼 조류 학계의 주목을 받고 있다. 국립생태원 조류 연구팀은 지난 16일 충남 서천군 금강 하구 일대에서 정기 모니터링을 진행하던 중 미기록종으로 추정되는 개체를 처음 포착했다고 밝혔다.

발견된 새는 도요목에 속하는 종으로, 외형적 특징이 기존 국내 기록종과 다수 상이한 것으로 확인됐다. 연구팀은 현장에서 촬영한 사진과 영상을 토대로 표본 채취 없이 1차 동정을 완료했으며, 현재 국제 조류 전문가 그룹에 검토를 의뢰한 상태다.

금강 하구는 매년 봄·가을 이동 철마다 수십만 마리의 철새가 거쳐 가는 동아시아 철새 이동 경로의 핵심 기착지다. 연구팀은 기후변화로 인한 이동 경로 변화가 이번 미기록종 출현의 원인일 가능성이 높다고 분석했다.

국립생태원 관계자는 "확정적인 동정 결과가 나오기까지 수 주가 소요될 수 있다"며 "만약 신종 또는 국내 미기록종으로 최종 확인될 경우 학술적으로 매우 중요한 발견이 될 것"이라고 말했다. 해당 지역은 발견 직후부터 일반인 출입이 제한됐으며, 추가 개체 확인을 위한 집중 조사가 이어지고 있다.`,
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text: "금강 하구 철새 도래지에서 국내에서 한 번도 기록된 적 없는 희귀 철새가 발견돼 조류 학계의 주목을 받고 있다.",
        summary: "충남 금강 하구에서 국내 미기록 희귀 철새가 처음 포착됨.",
      },
      {
        paragraph_index: 1,
        original_text: "발견된 새는 도요목에 속하는 종으로, 외형적 특징이 기존 국내 기록종과 다수 상이한 것으로 확인됐다.",
        summary: "도요목 계열로 추정되며 국제 전문가 검토 중임.",
      },
      {
        paragraph_index: 2,
        original_text: "금강 하구는 매년 봄·가을 이동 철마다 수십만 마리의 철새가 거쳐 가는 동아시아 철새 이동 경로의 핵심 기착지다.",
        summary: "기후변화로 인한 이동 경로 변화가 원인으로 분석됨.",
      },
      {
        paragraph_index: 3,
        original_text: "국립생태원 관계자는 확정적인 동정 결과가 나오기까지 수 주가 소요될 수 있다고 말했다.",
        summary: "최종 확인까지 수 주 소요 예정이며 현장 출입이 통제됨.",
      },
    ],
  },
  {
    id: "2",
    title: "제임스 웹 망원경, 새로운 외계행성 대기 성분 확인",
    oneLineSummary: "웹 망원경이 외계행성에서 생명 가능성 분자를 발견했어요.",
    source: "사이언스타임즈",
    sourceLang: "ko",
    publishedAt: "2026-05-17T14:30:00Z",
    thumbnailUrl: "/images/space-webb.jpg",
    category: "sky",
    subcategory: "space",
    confidence: 0.92,
    originalUrl: "https://www.sciencetimes.co.kr/example-2",
    content: `미국 항공우주국(NASA)의 제임스 웹 우주망원경(JWST)이 지구에서 약 120광년 떨어진 외계행성 K2-18b의 대기에서 디메틸황화물(DMS) 신호를 포착했다고 연구팀이 발표했다. DMS는 지구에서 해양 생물에 의해서만 생성되는 것으로 알려진 분자로, 이번 발견은 생명체 존재 가능성을 시사하는 중요한 단서로 여겨진다.

케임브리지대 천문학과 연구팀이 주도한 이번 연구는 웹 망원경의 NIRSpec 분광기를 활용해 K2-18b가 항성 앞을 통과할 때 대기를 투과하는 별빛의 스펙트럼을 분석하는 방식으로 진행됐다. 연구팀은 메테인, 이산화탄소와 함께 DMS 신호를 확인했으나, 아직 통계적 유의성을 높이기 위한 추가 관측이 필요하다고 밝혔다.

K2-18b는 질량이 지구의 약 8.6배에 달하는 '미니 넵튠' 또는 '하이션(Hycean)' 행성으로 분류된다. 하이션 행성은 수소 대기와 광대한 액체 바다를 가진 것으로 추정되며, 이론적으로 생명체 거주 가능 조건을 충족할 수 있다.

다만 일부 천문학자들은 DMS가 비생물학적 화학반응으로도 생성될 수 있다는 점을 들어 성급한 결론을 경계하고 있다. NASA는 후속 관측을 통해 신호의 신뢰도를 높이는 연구를 계속 지원할 예정이라고 전했다.`,
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text: "제임스 웹 우주망원경이 외계행성 K2-18b의 대기에서 DMS 신호를 포착했다.",
        summary: "웹 망원경이 K2-18b 대기에서 생명 관련 분자를 검출함.",
      },
      {
        paragraph_index: 1,
        original_text: "케임브리지대 연구팀이 NIRSpec 분광기로 대기 스펙트럼을 분석해 DMS 신호를 확인했다.",
        summary: "DMS 신호 확인됐으나 통계적 유의성 확보를 위한 추가 관측이 필요함.",
      },
      {
        paragraph_index: 2,
        original_text: "K2-18b는 지구 질량의 8.6배인 하이션 행성으로, 이론적으로 생명체 거주 조건을 충족할 수 있다.",
        summary: "K2-18b는 이론적으로 생명체 거주 조건을 갖춘 하이션 행성임.",
      },
      {
        paragraph_index: 3,
        original_text: "일부 천문학자들은 DMS가 비생물학적 반응으로도 생성될 수 있어 성급한 결론을 경계한다.",
        summary: "비생물학적 생성 가능성도 있어 NASA가 후속 관측을 이어갈 예정임.",
      },
    ],
  },
  {
    id: "4",
    title: "강원도 산불, 이틀째 확산…주민 대피령 발령",
    oneLineSummary: "강원 산불이 이틀째 번지며 주민 대피가 시작됐어요.",
    source: "한겨레",
    sourceLang: "ko",
    publishedAt: "2026-05-15T11:00:00Z",
    thumbnailUrl: "/images/land-wildfire.jpg",
    category: "land",
    subcategory: "disaster",
    confidence: 0.98,
    originalUrl: "https://www.hani.co.kr/example-4",
    content: `강원도 강릉시 연곡면 일대에서 발생한 산불이 이틀째 이어지며 인근 마을로 번져 주민 대피령이 발령됐다. 소방청에 따르면 15일 오전 현재 산불은 축구장 약 280개 면적(200ha)을 태웠으며 진화율은 30%에 머물고 있다.

산림청은 헬기 21대와 지상 진화대원 800여 명을 투입해 진화 작업을 벌이고 있으나, 강한 바람과 건조한 날씨로 진화에 어려움을 겪고 있다. 강릉 기상대에 따르면 이날 순간 최대풍속이 초속 18m에 달해 불길이 예측하기 어려운 방향으로 번지고 있는 상황이다.

강릉시는 연곡면 일대 주민 1,200여 명에게 대피 명령을 내리고 인근 학교와 마을회관을 임시 대피소로 운영 중이다. 현재까지 인명 피해는 없으나 농가 10여 채와 비닐하우스 수십 동이 소실된 것으로 집계됐다.

행정안전부는 강원도에 재난안전 특별교부세를 긴급 지원하고 이재민 구호 물품 배분에 나섰다. 기상청은 오늘 오후부터 강원 영동 지역의 바람이 다소 약해질 것으로 예보하고 있어 진화 여건이 개선될 것으로 기대된다.`,
    paragraphSummaries: [
      {
        paragraph_index: 0,
        original_text: "강원도 강릉 연곡면 산불이 이틀째 번지며 200ha를 태우고 진화율 30%에 머물고 있다.",
        summary: "강릉 연곡면 산불이 이틀째 200ha를 태우며 진화율 30%에 머무름.",
      },
      {
        paragraph_index: 1,
        original_text: "헬기 21대와 진화대원 800명이 투입됐으나 초속 18m의 강풍으로 진화에 어려움을 겪고 있다.",
        summary: "강풍·건조 날씨로 대규모 인력 투입에도 진화에 어려움을 겪음.",
      },
      {
        paragraph_index: 2,
        original_text: "강릉시는 주민 1,200여 명에게 대피 명령을 내렸고, 농가·비닐하우스 등 재산 피해가 발생했다.",
        summary: "주민 1,200명 대피 및 농가·비닐하우스 수십 동 소실됨.",
      },
      {
        paragraph_index: 3,
        original_text: "행안부가 특별교부세를 긴급 지원하고, 오후부터 바람이 약해져 진화 여건이 개선될 전망이다.",
        summary: "오후부터 바람이 약해져 진화 여건 개선이 기대됨.",
      },
    ],
  },
];

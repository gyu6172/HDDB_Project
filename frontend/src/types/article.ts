export type Category = "sky" | "land" | "sea";

// sky
type SkySubcategory = "bird" | "space" | "weather" | "air_pollution";
// land
type LandSubcategory = "disaster" | "animal" | "ground_pollution" | "insect";
// sea
type SeaSubcategory = "marine_life" | "deep_sea" | "ocean_pollution";

export type Subcategory = SkySubcategory | LandSubcategory | SeaSubcategory;

export interface ParagraphSummary {
  paragraphIndex: number;
  originalText: string;
  summary: string;
}

// 리스트(카드)용
export interface Article {
  id: string;
  title: string;
  oneLineSummary: string;
  cardSummary?: string;
  source: string;
  sourceLang: "ko" | "en";
  publishedAt: string;
  thumbnailUrl: string;
  category: Category;
  subcategory: Subcategory;
  confidence: number | null;
}

// 상세용
export interface ArticleDetail extends Article {
  content: string | null;
  originalUrl: string;
  paragraphSummaries: ParagraphSummary[] | null;
}

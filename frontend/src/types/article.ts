export type Category = "sky" | "land" | "sea";

// sky
type SkySubcategory = "bird" | "space" | "weather" | "air_pollution";
// land
type LandSubcategory = "disaster" | "animal" | "ground_pollution" | "insect";
// sea
type SeaSubcategory = "marine_life" | "deep_sea" | "ocean_pollution";

export type Subcategory = SkySubcategory | LandSubcategory | SeaSubcategory;

export interface ParagraphSummary {
  paragraph_index: number;
  original_text: string;
  summary: string;
}

// 리스트(카드)용 — §3.2
export interface Article {
  id: string;
  title: string;
  oneLineSummary: string;
  source: string;
  sourceLang: "ko" | "en";
  publishedAt: string;
  thumbnailUrl: string;
  category: Category;
  subcategory: Subcategory;
  confidence: number;
}

// 상세용 — §3.3
export interface ArticleDetail extends Article {
  content: string;
  originalUrl: string;
  paragraphSummaries: ParagraphSummary[];
}

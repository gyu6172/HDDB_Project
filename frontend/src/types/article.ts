export type Category = "sky" | "land" | "sea";

type SkySubcategory = "bird" | "space" | "weather";
type LandSubcategory = "disaster" | "animal" | "pollution";
type SeaSubcategory = "marine_life" | "deep_sea" | "ocean_pollution";

export type Subcategory = SkySubcategory | LandSubcategory | SeaSubcategory;

export interface ParagraphSummary {
  paragraph_index: number;
  original_text: string;
  summary: string;
}

export interface Article {
  id: string;
  title: string;
  content: string;
  source: string;
  publishedAt: string;
  category: Category;
  subcategory: Subcategory;
  oneLineSummary: string;
  cardSummary: string;
  paragraphSummaries: ParagraphSummary[];
  thumbnail: string;
}

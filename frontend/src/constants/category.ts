import { Category, Subcategory } from "@/types/article";

export const CATEGORY_META: Record<Category, { label: string; emoji: string; gradient: string; desc: string }> = {
  sky:  { label: "하늘", emoji: "☁️", gradient: "from-sky-from/30 to-sky-to/20",   desc: "하늘에서 일어나는 자연의 이야기" },
  land: { label: "땅",   emoji: "🌳", gradient: "from-land-from/30 to-land-to/20", desc: "땅 위에서 펼쳐지는 자연의 이야기" },
  sea:  { label: "바다", emoji: "🌊", gradient: "from-sea-from/25 to-sea-to/15",   desc: "깊고 넓은 바다의 자연 이야기" },
};

export const SUBCATEGORY_META: Record<Subcategory, { label: string; emoji: string }> = {
  bird:            { label: "새",      emoji: "🪺" },
  space:           { label: "우주",    emoji: "🚀" },
  weather:         { label: "기상",    emoji: "🌤️" },
  air_pollution:   { label: "대기오염", emoji: "🌫️" },
  disaster:        { label: "자연재해", emoji: "🌋" },
  animal:          { label: "동식물",  emoji: "🐾" },
  ground_pollution:  { label: "토양오염", emoji: "♻️" },
  insect:          { label: "곤충",    emoji: "🦋" },
  marine_life:     { label: "해양생물", emoji: "🐠" },
  deep_sea:        { label: "심해",    emoji: "🧜‍♀️" },
  ocean_pollution: { label: "해양오염", emoji: "☠️" },
};

export const CATEGORY_STYLE: Record<Category, { bg: string; text: string }> = {
  sky:  { bg: "bg-sky-from/30",  text: "text-sky-text" },
  land: { bg: "bg-land-from/30", text: "text-land-text" },
  sea:  { bg: "bg-sea-from/30",  text: "text-sea-text" },
};

export const THUMBNAIL_BG: Record<Category, string> = {
  sky:  "from-sky-from to-sky-to",
  land: "from-land-from to-land-to",
  sea:  "from-sea-from to-sea-to",
};

export const SUBCATEGORIES: Record<Category, Subcategory[]> = {
  sky:  ["bird", "space", "weather", "air_pollution"],
  land: ["disaster", "animal", "ground_pollution", "insect"],
  sea:  ["marine_life", "deep_sea", "ocean_pollution"],
};

export const VALID_CATEGORIES: Category[] = ["sky", "land", "sea"];

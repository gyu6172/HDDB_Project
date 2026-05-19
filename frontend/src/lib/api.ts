import { Article, Category } from "@/types/article";

export async function fetchArticlesByCategory(category: Category): Promise<Article[]> {
  const res = await fetch(`/api/articles?category=${category}`);
  return res.json();
}

export async function fetchArticleById(id: string): Promise<Article> {
  const res = await fetch(`/api/articles/${id}`);
  return res.json();
}

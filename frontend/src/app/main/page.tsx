import ArticleCard from "@/components/common/ArticleCard";
import { mockArticles } from "@/lib/mockData";

export default function MainPage() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <h1 className="text-heading font-bold text-text mb-6">최신 기사</h1>
      <div className="grid grid-cols-3 gap-5">
        {mockArticles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </div>
  );
}

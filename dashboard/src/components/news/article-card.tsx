import { Article } from "@/types/article";

export default function ArticleCard({
  article,
}: {
  article: Article;
}) {
  return (
    <div className="border rounded-lg p-4 shadow">
      <h2 className="font-bold text-lg">
        {article.title}
      </h2>

      <p className="text-sm mt-2">
        {article.description}
      </p>

      <div className="mt-3 text-xs text-gray-500">
        Score: {article.score ?? 0}
      </div>
    </div>
  );
}
import Link from "next/link";

export type NewsItemProps = {
  id?: string;
  title: string;
  source: string;
  time: string;
};

export default function NewsItem({ id, title, source, time }: NewsItemProps) {
  const content = (
    <>
      <h3 className="text-xl font-bold text-text">{title}</h3>
      <p className="mt-2 text-lg font-medium text-muted">
        {source} · {time}
      </p>
    </>
  );

  return (
    <article className="rounded-xl">
      {id ? (
        <Link
          href={`/articles/${id}`}
          className="-mx-3 block rounded-xl px-3 py-2 transition-colors hover:bg-black/[0.03]"
        >
          {content}
        </Link>
      ) : (
        content
      )}
    </article>
  );
}
